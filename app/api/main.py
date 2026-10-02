from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel

from app.core.chunk_repository import search_chunks
from app.core.config import get_settings
from app.core.cortex_api_client import CortexApiClient
from app.core.embeddings import GeminiEmbeddingClient
from app.core.hybrid_search import hybrid_search

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

class SearchRequest(BaseModel):
    owner_id: UUID
    query: str
    top_k: int = 5

class SearchResultItem(BaseModel):
    note_id: UUID
    chunk_index: int
    chunk_text: str
    distance: float

class SearchResponse(BaseModel):
    results: list[SearchResultItem]

embedding_client = GeminiEmbeddingClient(get_settings().gemini_api_key, get_settings().gemini_embedding_model)
@app.post("/search")
def search(request: SearchRequest) -> SearchResponse:
    query_embedding = embedding_client.embed_query(request.query)
    results = search_chunks(request.owner_id, query_embedding, request.top_k)
    return SearchResponse(results=[SearchResultItem(**r) for r in results])

class HybridSearchRequest(BaseModel):
    owner_id: UUID
    query: str
    top_k: int = 5

cortex_api_client = CortexApiClient(get_settings().cortex_api_base_url, get_settings().cortex_ai_api_key)
@app.post("/hybrid-search")
def hybrid_search_endpoint(request: HybridSearchRequest) -> list[dict]:
    return hybrid_search(
        request.owner_id,
        request.query,
        request.top_k,
        embedding_client=embedding_client,
        cortex_api_client=cortex_api_client
    )