"""Tests for range-based document content updates (PATCH)."""
import pytest

from app.db.store import DocumentStore
from app.models.api import DocumentChange, ReplaceRange
from app.services.documents import DocumentNotFoundError, DocumentService, PreconditionFailedError

## in memory store for tests
@pytest.fixture
def store() -> DocumentStore:
    """In-memory store for tests."""
    return DocumentStore(path=":memory:")

## service for tests
@pytest.fixture
def service(store: DocumentStore) -> DocumentService:
    return DocumentService(store)

## helper function to create a document change
def _ch(start: int, end: int, text: str) -> DocumentChange:
    return DocumentChange(operation="replace", range=ReplaceRange(start=start, end=end), text=text)


def test_single_replace_insert(service: DocumentService) -> None:
    """Insert text at end: 'hello' -> 'hello world'."""
    doc = service.create_document("Test", content="hello")
    updated = service.update_document_content(
        doc.id,
        doc.version,
        [_ch(5, 5, " world")],
    )
    assert updated.content == "hello world"
    assert updated.version == 2


def test_single_replace_removal(service: DocumentService) -> None:
    """Remove substring: 'hello world' -> 'hello'."""
    doc = service.create_document("Test", content="hello world")
    updated = service.update_document_content(
        doc.id,
        doc.version,
        [_ch(5, 11, "")],
    )
    assert updated.content == "hello"
    assert updated.version == 2


def test_single_replace_in_place(service: DocumentService) -> None:
    """Replace substring: 'hello world' -> 'hello there'."""
    doc = service.create_document("Test", content="hello world")
    updated = service.update_document_content(
        doc.id,
        doc.version,
        [_ch(6, 11, "there")],
    )
    assert updated.content == "hello there"


def test_multiple_changes_applied_descending(service: DocumentService) -> None:
    """Multiple replacements applied in descending start order."""
    # "one two three" -> change "two"->"2", then "three"->"3" (reverse order so indices stay valid)
    doc = service.create_document("Test", content="one two three")
    changes = [
        _ch(4, 7, "2"),   # two -> 2
        _ch(8, 13, "3"),  # three -> 3
    ]
    updated = service.update_document_content(doc.id, doc.version, changes)
    assert updated.content == "one 2 3"


def test_empty_changes_leaves_content_unchanged(service: DocumentService) -> None:
    doc = service.create_document("Test", content="unchanged")
    updated = service.update_document_content(doc.id, doc.version, [])
    assert updated.content == "unchanged"
    assert updated.version == 2  # store still bumps version on update_document with same content


def test_document_not_found_raises(service: DocumentService) -> None:
    with pytest.raises(DocumentNotFoundError):
        service.update_document_content(
            "nonexistent-id",
            1,
            [_ch(0, 0, "x")],
        )


def test_version_mismatch_raises_precondition(service: DocumentService) -> None:
    doc = service.create_document("Test", content="hello")
    with pytest.raises(PreconditionFailedError):
        service.update_document_content(doc.id, 999, [_ch(0, 0, "x")])


def test_missing_if_match_version_raises_precondition(service: DocumentService) -> None:
    doc = service.create_document("Test", content="hello")
    with pytest.raises(PreconditionFailedError):
        service.update_document_content(doc.id, None, [_ch(0, 0, "x")])


def test_out_of_bounds_range_raises(service: DocumentService) -> None:
    doc = service.create_document("Test", content="hi")  # len=2
    with pytest.raises(ValueError, match="out of bounds"):
        service.update_document_content(doc.id, doc.version, [_ch(0, 10, "x")])
