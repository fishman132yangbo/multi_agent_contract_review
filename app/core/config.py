from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "deepseek"
    llm_api_key: str | None = None
    llm_model: str = "deepseek-v4-flash"
    llm_base_url: str = "https://api.deepseek.com"
    llm_timeout_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
