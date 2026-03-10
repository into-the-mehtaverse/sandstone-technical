"""App configuration from env. Use pydantic-settings for validation and defaults."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend root (apps/backend). Ensures DB path is absolute so seed and server use same file.
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # SQLite path. If relative, resolved against backend root. Default: app/db/documents.db
    document_db_path: str = "app/db/documents.db"

    def get_document_db_path(self) -> str:
        """Return absolute path to the document DB so it's stable regardless of process cwd."""
        p = Path(self.document_db_path)
        return str(p if p.is_absolute() else _BACKEND_ROOT / p)


settings = Settings()
