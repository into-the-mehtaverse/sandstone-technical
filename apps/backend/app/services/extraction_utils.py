"""
Extract plain text from uploaded file bytes. Document uploads only accept .docx.
"""
import io
from pathlib import Path

from docx import Document as DocxDocument

## just checks if the file is a .docx file
def is_docx_file(filename: str | None, content_type: str | None) -> bool:
    """True if the file appears to be .docx (extension or Content-Type). Used for upload validation."""
    if filename and Path(filename).suffix.lower() == ".docx":
        return True
    if content_type and "wordprocessingml" in content_type:
        return True
    return False

## extracts the text from the file
def extract_text_from_bytes(
    data: bytes,
    *,
    filename: str | None = None,
    content_type: str | None = None,
) -> str:
    """
    Extract plain text from .docx file bytes. Only .docx is supported for document uploads.
    Raises ValueError if type is not .docx or extraction fails.
    """
    if is_docx_file(filename, content_type):
        doc = DocxDocument(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    raise ValueError("Only .docx files are accepted.")
