import json
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from app.core.agent import run_agent_turn, confirm_pending_action
from app.core.auth import get_current_owner_id
from app.core.chunk_repository import search_chunks
from app.core.config import get_settings
from app.core.cortex_api_client import CortexApiClient
from app.core.embeddings import GeminiEmbeddingClient
from app.core.generation import GeminiChatClient
from app.core.hybrid_search import hybrid_search
from app.core.rag import answer_query
import logging

from app.core.rate_limit import rate_limiter
from app.core.reranking import CrossEncoderReranker

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

class SearchRequest(BaseModel):
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
def search(request: SearchRequest, owner_id: UUID = Depends(rate_limiter("search", 30, 60))) -> SearchResponse:
    query_embedding = embedding_client.embed_query(request.query)
    results = search_chunks(owner_id, query_embedding, request.top_k)
    return SearchResponse(results=[SearchResultItem(**r) for r in results])

class HybridSearchRequest(BaseModel):
    query: str
    top_k: int = 5

cortex_api_client = CortexApiClient(get_settings().cortex_api_base_url, get_settings().cortex_ai_api_key)
@app.post("/hybrid-search")
def hybrid_search_endpoint(request: HybridSearchRequest, owner_id: UUID = Depends(rate_limiter("hybrid_search", 30, 60))) -> list[dict]:
    return hybrid_search(
        owner_id,
        request.query,
        request.top_k,
        embedding_client=embedding_client,
        cortex_api_client=cortex_api_client
    )

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    conversation_id: UUID | None = None

chat_client = GeminiChatClient(get_settings().gemini_api_key, get_settings().gemini_chat_model)
complex_chat_client = GeminiChatClient(get_settings().gemini_api_key, get_settings().gemini_complex_model)
reranker = CrossEncoderReranker(get_settings().reranker_model)
@app.post("/chat")
def chat(request: ChatRequest, owner_id: UUID = Depends(rate_limiter("chat", 10, 60))) -> StreamingResponse:
    def event_stream():
        for event in answer_query(
                owner_id,
                request.query,
                embedding_client,
                cortex_api_client,
                chat_client,
                complex_chat_client,
                reranker,
                request.top_k,
                conversation_id=request.conversation_id,):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

class AgentChatRequest(BaseModel):
    query: str

@app.post("/agent-chat")
def agent_chat(request: AgentChatRequest, owner_id: UUID = Depends(rate_limiter("agent_chat", 10, 60))) -> StreamingResponse:
    def event_stream():
        for event in run_agent_turn(owner_id, request.query, embedding_client, cortex_api_client, chat_client):
            yield f"data: {json.dumps(event, default=str)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

class AgentConfirmRequest(BaseModel):
    confirmation_id: UUID
    approve: bool

@app.post("/agent-chat/confirm")
def agent_chat_confirm(request: AgentConfirmRequest, owner_id: UUID = Depends(rate_limiter("confirm", 20, 60))) -> dict:
    res = confirm_pending_action(
        owner_id,
        request.confirmation_id,
        request.approve,
        cortex_api_client
    )
    if res["status"] == "not_found":
        raise HTTPException(status_code=404, detail=res["message"])
    if res["status"] == "error":
        raise HTTPException(status_code=500, detail=res["message"])
    return res