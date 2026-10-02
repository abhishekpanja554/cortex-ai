from uuid import UUID

from app.core.chunk_repository import search_chunks
from app.core.cortex_api_client import CortexApiClient
from app.core.embeddings import GeminiEmbeddingClient

_RRF_K = 60

def hybrid_search(
        owner_id: UUID,
        query: str,
        top_k: int,
        embedding_client: GeminiEmbeddingClient,
        cortex_api_client: CortexApiClient,
        candidate_limit: int = 20
) -> list[dict]:
    query_embedding = embedding_client.embed_query(query)
    search_res = search_chunks(owner_id, query_embedding,candidate_limit)
    vector_ranks = _rank_vector_results(search_res)
    cortex_api_search_res =  cortex_api_client.search_notes(owner_id,query,candidate_limit)
    keyword_ranks = _rank_keyword_results(cortex_api_search_res)
    return _fuse_rankings(vector_ranks, keyword_ranks, top_k)

def _rank_vector_results(chunk_results: list[dict]) -> dict[UUID, tuple[int, float, str]]:
    best_matches_by_note = {}
    for chunk in chunk_results:
        note_id = chunk["note_id"]
        distance = chunk["distance"]
        chunk_text = chunk["chunk_text"]

        if note_id not in best_matches_by_note or distance < best_matches_by_note[note_id][0]:
            best_matches_by_note[note_id] = (distance, chunk_text)

    sorted_notes = sorted(best_matches_by_note.items(), key=lambda item: item[1][0])

    final_ranked_results = {}
    for rank, (note_id, (distance, text)) in enumerate(sorted_notes, start=1):
        final_ranked_results[note_id] = (rank, distance, text)

    return final_ranked_results

def _rank_keyword_results(note_results: list[dict]) -> dict[UUID, tuple[int, str]]:
    final_ranked_results = {}
    for rank, note in enumerate(note_results, start=1):
        note_id = UUID(note["id"])
        title = note["title"]
        final_ranked_results[note_id] = (rank, title)
    return final_ranked_results

def _fuse_rankings(
        vector_ranks: dict[UUID, tuple[int, float, str]],
        keyword_ranks: dict[UUID, tuple[int, str]],
        top_k: int,
) -> list[dict]:
    all_note_ids = set(vector_ranks.keys()) | set(keyword_ranks.keys())
    fused_results = []
    for note_id in all_note_ids:
        score = 0.0
        distance = None
        chunk_text = None
        title = None

        v_data = vector_ranks.get(note_id)
        k_data = keyword_ranks.get(note_id)

        if v_data is not None:
            v_rank, distance, chunk_text = v_data
            score += 1.0 / (_RRF_K + v_rank)

        if k_data is not None:
            k_rank, title = k_data
            score += 1.0 / (_RRF_K + k_rank)
        fused_results.append({
            "note_id": note_id,
            "score": score,
            "distance": distance,
            "chunk_text": chunk_text,
            "title": title
        })
    fused_results.sort(key=lambda x: x["score"], reverse=True)

    return fused_results[:top_k]
