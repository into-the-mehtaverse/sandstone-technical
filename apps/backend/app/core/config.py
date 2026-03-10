"""App configuration from env. Use pydantic-settings for validation and defaults."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    document_db_path: str = "documents.db"


settings = Settings()
