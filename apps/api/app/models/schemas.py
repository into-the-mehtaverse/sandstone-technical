"""
Application-wide HTTP request/response schemas (API contract).
Used by routes and reflected in OpenAPI. Snake_case throughout.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---- Document schemas (base + variants) ----


class DocumentBase(BaseModel):
    """Shared document fields (no content)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    etag: str


class DocumentSummary(DocumentBase):
    """Document list item (no content)."""

    pass


class DocumentResponse(DocumentBase):
    """Full document (includes content)."""

    content: str


# ---- Error (shared 4xx/5xx body) ----


class ErrorResponse(BaseModel):
    """Shared error body for 4xx and 5xx responses."""

    model_config = ConfigDict(extra="forbid")

    error: str
    code: int
