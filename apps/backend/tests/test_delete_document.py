"""Tests for document delete (store and service)."""
import pytest

from app.db.store import DocumentStore
from app.services.documents import DocumentNotFoundError, DocumentService


@pytest.fixture
def store() -> DocumentStore:
    return DocumentStore(path=":memory:")


@pytest.fixture
def service(store: DocumentStore) -> DocumentService:
    return DocumentService(store)


def test_store_delete_removes_document(store: DocumentStore) -> None:
    doc = store.create_document("To Delete", content="x")
    assert store.get_document(doc.id) is not None
    deleted = store.delete_document(doc.id)
    assert deleted is True
    assert store.get_document(doc.id) is None


def test_store_delete_nonexistent_returns_false(store: DocumentStore) -> None:
    deleted = store.delete_document("nonexistent-id")
    assert deleted is False


def test_service_delete_succeeds(service: DocumentService) -> None:
    doc = service.create_document("To Delete", content="y")
    service.delete_document(doc.id)
    assert service.get_document(doc.id) is None


def test_service_delete_not_found_raises(service: DocumentService) -> None:
    with pytest.raises(DocumentNotFoundError):
        service.delete_document("nonexistent-id")
