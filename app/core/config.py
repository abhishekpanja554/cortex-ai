from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_queue_key: str = "jobs:embedding"
    redis_brpop_timeout_seconds: int = 5
    cortex_api_base_url: str
    cortex_ai_api_key: str
    db_host: str
    db_port: int = 5432
    db_name: str = "cortex-ai"
    db_user: str
    db_password: str

    gemini_api_key: str
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_chat_model: str = "gemini-3.5-flash-lite"
    gemini_complex_model: str
    embedding_dimension: int = 3072

    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 50

    model_config = SettingsConfigDict(env_file = ".env")

    jwt_secret: str

@lru_cache
def get_settings() -> Settings:
    return Settings()
