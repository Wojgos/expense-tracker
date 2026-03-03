from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    redis_url: str = "redis://localhost:6379/0"
    exchange_rate_cache_ttl: int = 3600


settings = Settings()
