"""
In-memory document store.
"""
from datetime import datetime, timezone

from app.db.schemas import Document, compute_etag


class DocumentStore:
    """In-memory store for documents."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    def list_documents(self) -> list[Document]:
        """Return all documents (order not guaranteed)."""
        return list(self._documents.values())

    def get_document(self, doc_id: str) -> Document | None:
        """Return document by id or None if not found."""
        return self._documents.get(doc_id)

    def create_document(self, title: str, content: str = "") -> Document:
        """Create a new document and return it."""
        doc = Document.create(title=title, content=content)
        self._documents[doc.id] = doc
        return doc

    def update_document(
        self,
        doc_id: str,
        *,
        content: str | None = None,
        title: str | None = None,
    ) -> Document | None:
        """Update document by id. Recomputes etag if content changes. Returns None if not found."""
        doc = self._documents.get(doc_id)
        if doc is None:
            return None
        new_content = content if content is not None else doc.content
        new_title = title if title is not None else doc.title
        now = datetime.now(timezone.utc)
        updated = Document(
            id=doc.id,
            title=new_title,
            content=new_content,
            created_at=doc.created_at,
            updated_at=now,
            etag=compute_etag(new_content),
        )
        self._documents[doc_id] = updated
        return updated


# Singleton store instance for the app (can be replaced with dependency injection later)
store = DocumentStore()
