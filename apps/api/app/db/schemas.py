"""
DB-layer types: internal document model and helpers.
"""
import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


def compute_etag(content: str) -> str:
    """Cache of content hash for concurrency (If-Match)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]


@dataclass
class Document:
    """Internal document model (db layer)."""

    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    etag: str

    @classmethod
    def create(cls, title: str, content: str = "") -> "Document":
        now = datetime.now(timezone.utc)
        doc_id = str(uuid.uuid4())
        etag = compute_etag(content)
        return cls(
            id=doc_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
            etag=etag,
        )
