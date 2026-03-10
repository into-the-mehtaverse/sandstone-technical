"""Tests for create_document_from_template (copy template to new document)."""
import pytest

from app.db.store import DocumentStore
from app.services.documents import DocumentNotFoundError, DocumentService


@pytest.fixture
def store() -> DocumentStore:
    return DocumentStore(path=":memory:")


@pytest.fixture
def service(store: DocumentStore) -> DocumentService:
    return DocumentService(store)


def test_create_from_template_copies_content(service: DocumentService) -> None:
    """New document has same content as template, new id and version 1."""
    template = service.create_document("My Template", content="Hello world")
    doc = service.create_document_from_template(template.id)
    assert doc.id != template.id
    assert doc.title == "Copy of My Template"
    assert doc.content == template.content
    assert doc.version == 1


def test_create_from_template_with_custom_title(service: DocumentService) -> None:
    """Optional title overrides default 'Copy of ...'."""
    template = service.create_document("Template", content="x")
    doc = service.create_document_from_template(template.id, title="My Instance")
    assert doc.title == "My Instance"
    assert doc.content == "x"


def test_create_from_template_not_found_raises(service: DocumentService) -> None:
    """Raises DocumentNotFoundError when template_id does not exist."""
    with pytest.raises(DocumentNotFoundError):
        service.create_document_from_template("nonexistent")
