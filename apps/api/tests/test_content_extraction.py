"""
Tests for content extraction (.txt, .docx).
"""
import pytest
from pathlib import Path

from app.services.content_extraction import (
    extract_text_from_bytes,
    is_allowed_file,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_extract_text_from_bytes_txt():
    """Plain text is decoded as UTF-8."""
    data = b"Hello, world.\nSecond line."
    out = extract_text_from_bytes(data, filename="doc.txt")
    assert out == "Hello, world.\nSecond line."


def test_extract_text_from_bytes_txt_via_content_type():
    """Plain text via Content-Type works."""
    data = b"Only a line."
    out = extract_text_from_bytes(data, content_type="text/plain")
    assert out == "Only a line."


def test_extract_text_from_bytes_unsupported_raises():
    """Unsupported type raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text_from_bytes(b"x", filename="file.xyz")


def test_is_allowed_file():
    """Allowed extensions and content types return True."""
    assert is_allowed_file("doc.txt", None) is True
    assert is_allowed_file("doc.docx", None) is True
    assert is_allowed_file(None, "text/plain") is True
    assert is_allowed_file(
        None, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ) is True
    assert is_allowed_file("file.xyz", None) is False


@pytest.fixture
def sample_docx_path():
    """First .docx in fixtures dir (e.g. sample.docx or loan_agreement_template.docx)."""
    docx_files = list(FIXTURES_DIR.glob("*.docx"))
    return docx_files[0] if docx_files else FIXTURES_DIR / "sample.docx"


def test_extract_text_from_docx_fixture(sample_docx_path):
    """Extract text from a .docx in fixtures (skipped if none found)."""
    if not sample_docx_path.exists():
        pytest.skip(f"No .docx fixture found in {FIXTURES_DIR}")
    data = sample_docx_path.read_bytes()
    text = extract_text_from_bytes(data, filename=sample_docx_path.name)
    assert isinstance(text, str)
    assert len(text) > 0, "Fixture .docx should have extractable text"
    words = text.split()[:20]
    print(f"\nFirst 20 words from {sample_docx_path.name}: {' '.join(words)}")
