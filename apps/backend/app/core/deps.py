"""Shared dependencies: store and services. Override get_store in tests."""
from app.core.config import settings
from app.db.store import DocumentStore

# Singleton for the app (file-backed). Tests override get_store with :memory: store.
_store: DocumentStore | None = None

## initialize store
def get_store() -> DocumentStore:
    """Document store (SQLite path from config; override in tests for :memory:)."""
    global _store
    if _store is None:
        _store = DocumentStore(path=settings.document_db_path)
    return _store
