"""
DB-layer types: internal document model and helpers.
"""
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DocumentSummary:
    """Document without content (for list views)."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    version: int
    party_id: str | None = None
    party_name: str | None = None
    doc_type: str | None = None


@dataclass
class Document:
    """Internal document model (db layer)."""

    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    version: int
    party_id: str | None = None
    party_name: str | None = None
    doc_type: str | None = None

    @classmethod
    def create(
        cls,
        title: str,
        content: str = "",
        *,
        party_id: str | None = None,
        party_name: str | None = None,
        doc_type: str | None = None,
        version: int = 1,
    ) -> "Document":
        now = datetime.now(timezone.utc)
        doc_id = str(uuid.uuid4())
        return cls(
            id=doc_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
            version=version,
            party_id=party_id,
            party_name=party_name,
            doc_type=doc_type,
        )
