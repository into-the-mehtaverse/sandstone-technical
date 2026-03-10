"""API request/response schemas (Pydantic)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---- Document response (API contract) ----


class DocumentSummaryResponse(BaseModel):
    """Document list item (no content)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    version: int
    party_id: str | None = None
    party_name: str | None = None
    doc_type: str | None = None


class DocumentResponse(DocumentSummaryResponse):
    """Full document (includes content)."""

    content: str


# ---- Document change (PATCH request) ----


## replace uses range / position based approach
## character range [start, end) for a replace operation
## start is inclusive, end is exclusive
## used to specify the range of characters to replace
## start must be less than end
class ReplaceRange(BaseModel):
    """Character range [start, end) for a replace operation."""

    model_config = ConfigDict(extra="forbid")

    start: int = Field(..., ge=0, description="Start index (inclusive)")
    end: int = Field(..., ge=0, description="End index (exclusive)")

    @model_validator(mode="after")
    def start_le_end(self) -> "ReplaceRange":
        if self.start > self.end:
            raise ValueError("start must be <= end")
        return self


class DocumentChange(BaseModel):
    """Single change for PATCH /documents/{id}. Only 'replace' is supported."""

    model_config = ConfigDict(extra="forbid")

    operation: str = Field(..., description="Operation type; only 'replace' is supported")
    range: ReplaceRange = Field(..., description="Character range to replace")
    text: str = Field(..., description="Replacement text (empty string = removal)")

    @model_validator(mode="after")
    def only_replace(self) -> "DocumentChange":
        if self.operation != "replace":
            raise ValueError("operation must be 'replace'")
        return self


class PatchDocumentRequest(BaseModel):
    """Body for PATCH /documents/{id}. Changes applied in reverse order by range.start. Optional title update."""

    model_config = ConfigDict(extra="forbid")

    changes: list[DocumentChange] = Field(default_factory=list, description="List of replace operations")
    title: str | None = Field(None, description="If set, update the document title")


# ---- Create from template (POST /documents/from-template) ----


class CreateFromTemplateRequest(BaseModel):
    """Body for POST /documents/from-template. Creates a new document as a copy of the template."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    template_id: str = Field(..., alias="templateId", description="ID of the template document to copy")
    title: str | None = Field(None, description="Title for the new document; default 'Copy of {template.title}'")


# ---- Search response (API contract) ----


class SearchMatchResponse(BaseModel):
    """Single search hit."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)

    document_id: str = Field(..., alias="documentId")
    title: str = ""
    snippet: str = ""
    start_index: int = Field(..., alias="startIndex")
    end_index: int = Field(..., alias="endIndex")


class SearchResponse(BaseModel):
    """Search results: matches for this page and total hit count."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)

    matches: list[SearchMatchResponse] = Field(default_factory=list)
    total: int = 0
