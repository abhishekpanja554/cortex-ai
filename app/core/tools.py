from uuid import UUID

import httpx

from app.core.chunk_repository import get_chunk_text_for_note
from app.core.cortex_api_client import CortexApiClient
from app.core.embeddings import GeminiEmbeddingClient
from app.core.hybrid_search import hybrid_search


def search_notes_tool(
    owner_id: UUID,
    embedding_client: GeminiEmbeddingClient,
    cortex_api_client: CortexApiClient,
    query: str,
    top_k: int = 5,
) -> dict:
    res = hybrid_search(
        owner_id,
        query,
        top_k=top_k,
        embedding_client=embedding_client,
        cortex_api_client=cortex_api_client)
    results = []
    for r in res:
        snippet = r.get("chunk_text")
        if snippet is None:
            # Keyword-only hit. Unlike /chat, don't drop it when there are no chunks yet:
            # a just-created note (e.g. from create_note) isn't embedded for a few seconds,
            # and the agent still needs to see it to act on it. Fall back to the title.
            snippet = get_chunk_text_for_note(owner_id, r["note_id"]) or r.get("title")
        results.append({"note_id": str(r["note_id"]), "title": r.get("title"), "snippet": snippet})
    return {"results": results}

def get_note_tool(
        owner_id: UUID,
        cortex_api_client:
        CortexApiClient,
        note_id: str
) -> dict:
    try:
        note = cortex_api_client.get_note(owner_id, UUID(note_id))
        return {"success": True, "title": note["title"], "body": note["body"]}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"No note found with id {note_id}"}
        raise

def delete_note_tool(
        owner_id: UUID,
        cortex_api_client: CortexApiClient,
        note_id: str
) -> dict:
    try:
        cortex_api_client.delete_note(owner_id, UUID(note_id))
        return {"success": True}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"No note found with id {note_id}"}
        raise

def create_note_tool(
        owner_id: UUID,
        cortex_api_client: CortexApiClient,
        title: str,
        body: str
) -> dict:
    try:
        note = cortex_api_client.create_note(owner_id, title, body)
        return {"success": True, "note_id": note["id"], "title": note["title"]}
    except httpx.HTTPStatusError as e:
        if e.response.status_code < 500:
            return {"success": False, "error": "Failed to create note"}
        raise

def update_note_tool(
        owner_id: UUID,
        cortex_api_client: CortexApiClient,
        note_id: str,
        title: str,
        body: str
) -> dict:
    try:
        note = cortex_api_client.update_note(owner_id, UUID(note_id), title, body)
        return {"success": True, "title": note["title"]}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"No note found with id {note_id}"}
        raise

def bulk_delete_notes_tool(
        owner_id: UUID,
        cortex_api_client: CortexApiClient,
        note_ids: list[str]
) -> dict:
    return {"results": [
        {"note_id": nid, **delete_note_tool(owner_id, cortex_api_client, nid)} for nid in note_ids
    ]}