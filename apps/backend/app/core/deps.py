"""Shared dependencies: store and services. Override get_store in tests."""
from fastapi import Depends

from app.core.config import settings
from app.db.store import DocumentStore
from app.services.documents import DocumentService

# Singleton for the app (file-backed). Tests override get_store with :memory: store.
_store: DocumentStore | None = None


def get_store() -> DocumentStore:
    """Document store (SQLite path from config; override in tests for :memory:)."""
    global _store
    if _store is None:
        _store = DocumentStore(path=settings.document_db_path)
    return _store


def get_document_service(store: DocumentStore = Depends(get_store)) -> DocumentService:
    """Document service backed by the store. Use in routes via Depends(get_document_service)."""
    return DocumentService(store)
