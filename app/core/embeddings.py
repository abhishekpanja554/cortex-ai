from google import genai
from google.genai import types


class GeminiEmbeddingClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        res = self.client.models.embed_content(
            model=self.model,
            contents=[types.Content(parts=[types.Part(text=t)]) for t in texts],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        if res.embeddings is None:
            raise RuntimeError("Gemini returned no embeddings")
        return [embedding.values for embedding in res.embeddings if embedding.values is not None]