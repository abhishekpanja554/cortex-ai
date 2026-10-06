import functools
import logging
from typing import Iterator
from uuid import UUID

from google.genai import types

from app.core.agent_tools_schema import SEARCH_NOTES_DECLARATION, GET_NOTE_DECLARATION, DELETE_NOTE_DECLARATION
from app.core.audit import log_llm_call
from app.core.cortex_api_client import CortexApiClient
from app.core.embeddings import GeminiEmbeddingClient
from app.core.generation import GeminiChatClient
from app.core.pending_actions import create_pending_action, resolve_pending_action
from app.core.pii import redact_dict_vals
from app.core.tools import search_notes_tool, get_note_tool, delete_note_tool

logger = logging.getLogger(__name__)

MAX_TOOL_HOPS = 5
DESTRUCTIVE_TOOLS = {"delete_note"}
EXECUTABLE_TOOLS = {"delete_note": delete_note_tool}

AGENT_SYSTEM_INSTRUCT = (
    "You are an assistant with tool access to the user's notes. "
    "Use search_notes and get_note freely to look things up. "
    "Call delete_note whenever the user asks to delete something — "
    "do not refuse or ask for confirmation yourself, the system handles that."
)

def run_agent_turn(
    owner_id: UUID,
    query: str,
    embedding_client: GeminiEmbeddingClient,
    cortex_api_client: CortexApiClient,
    chat_client: GeminiChatClient,
) -> Iterator[dict]:
    safe_tools = {
        "search_notes": functools.partial(search_notes_tool, owner_id, embedding_client, cortex_api_client),
        "get_note": functools.partial(get_note_tool, owner_id, cortex_api_client),
    }

    try:
        tool = types.Tool(function_declarations=[SEARCH_NOTES_DECLARATION, GET_NOTE_DECLARATION, DELETE_NOTE_DECLARATION,])
        content_config = types.GenerateContentConfig(
            system_instruction=AGENT_SYSTEM_INSTRUCT,
            tools=[tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        chat = chat_client.create_chat(content_config)
        message = query

        for _ in range(MAX_TOOL_HOPS):
            res = chat.send_message(message)
            parts = res.candidates[0].content.parts or []
            call_part = next((p for p in parts if p.function_call), None)

            if call_part is None:
                yield {"type": "answer", "text": res.text}
                return
            name, args = call_part.function_call.name, call_part.function_call.args or {}

            if name in DESTRUCTIVE_TOOLS:
                confirmation_id = create_pending_action(owner_id, name, args)
                yield {"type": "confirmation_required", "confirmation_id": str(confirmation_id), "tool": name, "args": args}
                return
            yield {"type": "tool_call", "tool": name, "args": args}
            res = safe_tools[name](**args)
            yield {"type": "tool_result", "tool": name, "result": res}
            redacted_res, redact_count = redact_dict_vals(res)
            log_llm_call(owner_id, f"agent_chat:{name}", chat_client.model, redact_count)
            message = types.Part.from_function_response(name=name, response=redacted_res)
        else:
            yield {"type": "error", "message": "Agent exceeded max tool call steps."}
    except Exception as e:
        logger.exception("Agent turn failed.")
        yield {"type": "error", "message": str(e)}
    finally:
        yield {"type": "done"}

def confirm_pending_action(
    owner_id: UUID,
    confirmation_id: UUID,
    approved: bool,
    cortex_api_client: CortexApiClient,
) -> dict:
    resolved = resolve_pending_action(confirmation_id, owner_id, approved)
    if resolved is None:
        return {
            "status": "not_found",
            "message": "Pending action not found, already resolved, or not yours."
        }
    if not approved:
        return {
            "status": "rejected",
            "message": "Action discarded."
        }
    tool_name = resolved["tool_name"]
    tool_args = resolved["tool_args"]
    try:
        res = EXECUTABLE_TOOLS[tool_name](owner_id, cortex_api_client, **tool_args)
        return {
            "status": "executed",
            "result": res
        }
    except Exception as e:
        logger.exception("Failed to execute confirmed action.")
        return {
            "status": "error",
            "message": str(e)
        }