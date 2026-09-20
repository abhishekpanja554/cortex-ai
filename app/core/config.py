from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_queue_key: str = "jobs:embedding"
    redis_brpop_timeout_seconds: int = 5
    cortex_api_base_url: str
    cortex_ai_api_key: str

    model_config = SettingsConfigDict(env_file = ".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()
