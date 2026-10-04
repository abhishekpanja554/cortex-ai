from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        pairs = []
        for c in candidates:
            pairs.append((query, c["chunk_text"]))
        scores = self.model.predict(pairs)
        for c, score in zip(candidates, scores):
            c["rerank_score"] = float(score)
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]