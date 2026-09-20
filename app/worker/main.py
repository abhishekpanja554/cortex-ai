import redis
import logging

from app.core.config import get_settings
from app.core.cortex_api_client import CortexApiClient
from app.core.models import EmbeddingJobMessage

logger = logging.getLogger(__name__)

def _process(message: EmbeddingJobMessage) -> None:
    logger.info("called")

def run() -> None:
    settings = get_settings()
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses = True
    )
    api_client = CortexApiClient(settings.cortex_api_base_url, settings.cortex_ai_api_key)

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
            _process(embedding_job_message)
            api_client.complete(embedding_job_message.job_id)
        except Exception as e:
            logger.exception(e)
            try:
                api_client.fail(embedding_job_message.job_id, str(e))
            except Exception as e:
                logger.exception(e)


if __name__ == "__main__":
    run()