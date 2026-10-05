from uuid import UUID

import httpx

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
    return {
        "results": [
            {"note_id": str(r["note_id"]), "snippet": r.get("chunk_text") or r.get("title")}
            for r in res
        ]
    }

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