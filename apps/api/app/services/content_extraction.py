"""
Extract plain text from uploaded file bytes (.txt, .docx).
"""
import io
from pathlib import Path

from docx import Document as DocxDocument


ALLOWED_EXTENSIONS = {".txt", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _is_docx(filename: str | None, content_type: str | None) -> bool:
    if filename and Path(filename).suffix.lower() == ".docx":
        return True
    if content_type and "wordprocessingml" in content_type:
        return True
    return False


def _is_txt(filename: str | None, content_type: str | None) -> bool:
    if filename and Path(filename).suffix.lower() == ".txt":
        return True
    if content_type and content_type.strip().startswith("text/plain"):
        return True
    return False


def extract_text_from_bytes(
    data: bytes,
    *,
    filename: str | None = None,
    content_type: str | None = None,
) -> str:
    """
    Extract plain text from file bytes. Supports .txt and .docx.
    Raises ValueError if type is not supported or extraction fails.
    """
    if _is_txt(filename, content_type):
        return data.decode("utf-8", errors="replace")
    if _is_docx(filename, content_type):
        doc = DocxDocument(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    raise ValueError(
        "Unsupported file type. Use .txt or .docx, or set Content-Type / filename accordingly."
    )


def is_allowed_file(filename: str | None, content_type: str | None) -> bool:
    """Return True if the file type is supported for upload."""
    if filename and Path(filename).suffix.lower() in ALLOWED_EXTENSIONS:
        return True
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if ct in ALLOWED_CONTENT_TYPES:
            return True
    return False
