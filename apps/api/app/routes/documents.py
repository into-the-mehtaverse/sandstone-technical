"""
Document routes. Thin HTTP layer; business logic in services.
"""
from fastapi import APIRouter, Depends

from app.db import store
from app.models.schemas import DocumentSummary

router = APIRouter(prefix="/documents", tags=["documents"])


def get_store():
    """Dependency for document store (can be overridden for tests)."""
    return store


@router.get("", response_model=list[DocumentSummary])
def list_documents(_store=Depends(get_store)):
    """List all documents (summaries only, no content)."""
    docs = _store.list_documents()
    return [
        DocumentSummary(
            id=d.id,
            title=d.title,
            created_at=d.created_at,
            updated_at=d.updated_at,
            etag=d.etag,
        )
        for d in docs
    ]
