"""Shared error response models. Used by exception handlers to return consistent JSON."""
from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Standard error body for 4xx and 5xx responses. All endpoints use this shape."""

    model_config = ConfigDict(extra="forbid")

    error: str = Field(..., description="Human-readable error message")
    code: int = Field(..., description="HTTP status code")
