import redis
import logging

from app.core.chunk_repository import delete_chunks, save_chunks
from app.core.chunking import chunk_text
from app.core.config import get_settings
from app.core.cortex_api_client import CortexApiClient
from app.core.embeddings import GeminiEmbeddingClient
from app.core.models import EmbeddingJobMessage, JobType

logger = logging.getLogger(__name__)

def _process(message: EmbeddingJobMessage, embedding_client: GeminiEmbeddingClient) -> None:
    settings = get_settings()
    if message.job_type == JobType.DELETE_EMBEDDINGS:
        delete_chunks(message.note_id)
        return

    full_text = f"{message.title}\n\n{message.body}"
    chunks = chunk_text(full_text, settings.chunk_size_tokens, settings.chunk_overlap_tokens)
    embeddings = embedding_client.embed(chunks)
    save_chunks(message.note_id, message.owner_id, chunks, embeddings)

def run() -> None:
    settings = get_settings()
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses = True
    )
    api_client = CortexApiClient(settings.cortex_api_base_url, settings.cortex_ai_api_key)
    embedding_client = GeminiEmbeddingClient(settings.gemini_api_key, settings.gemini_embedding_model)

    while True:
        res = redis_client.brpop(
            [settings.redis_queue_key],
            timeout=settings.redis_brpop_timeout_seconds
        )
        if res is None:
            continue
        raw_message = res[1]
        try:
            embedding_job_message = EmbeddingJobMessage.model_validate_json(raw_message)
        except Exception as e:
            logger.exception(e)
            continue

        try:
            _process(embedding_job_message, embedding_client)
            api_client.complete(embedding_job_message.job_id)
        except Exception as e:
            logger.exception(e)
            try:
                api_client.fail(embedding_job_message.job_id, str(e))
            except Exception as e:
                logger.exception(e)


if __name__ == "__main__":
    run()