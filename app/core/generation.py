from typing import Iterator

from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class GeminiChatClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def stream_answer(self,
        system_instruct: str,
        user_content: str,
        history = None,
        usage_out: dict | None = None
    ) -> Iterator[str]:
        config = types.GenerateContentConfig(system_instruction=system_instruct)
        chat = self.create_chat(config=config, history=history)
        responses = chat.send_message_stream(user_content)

        usage = None
        for chunk in responses:
            if chunk.text is not None:
                yield chunk.text
            if chunk.usage_metadata is not None:
                usage = chunk.usage_metadata

        if usage is not None:
            logger.info(
                "Gemini chat call (model=%s): %d prompt tokens, %d output tokens, %d total tokens",
                self.model,
                usage.prompt_token_count,
                usage.candidates_token_count,
                usage.total_token_count,
            )
            if usage_out is not None:
                usage_out["prompt_tokens"] = usage.prompt_token_count
                usage_out["output_tokens"] = usage.candidates_token_count

    def create_chat(self, config: types.GenerateContentConfig, history: list[types.Content] | None = None):
        return self.client.chats.create(model=self.model, config=config, history=history)