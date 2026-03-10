"""
Document business logic: orchestrate store and content extraction.
Routes call the service; the service calls the store and other services.
"""
from app.db.schemas import Document, DocumentSummary
from app.db.store import DocumentStore
from app.models.api import DocumentChange
from app.services.extraction_utils import extract_text_from_bytes, is_docx_file

## domain specific errors defined here
class DocumentNotFoundError(Exception):
    """Document does not exist."""


class PreconditionFailedError(Exception):
    """If-Match version does not match current document version (412)."""

## service class
class DocumentService:
    """Document operations. Injected with a DocumentStore (e.g. from get_store)."""

    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    ## list all documents with content
    def list_documents(self) -> list[Document]:
        """Return all documents with content."""
        return self._store.list_documents()

    ## list document summaries, optionally filtered by metadata (party_id, party_name, doc_type)
    def list_document_summaries(
        self,
        *,
        party_id: str | None = None,
        party_name: str | None = None,
        doc_type: str | None = None,
    ) -> list[DocumentSummary]:
        """Return document summaries (no content). Pass any of party_id, party_name, doc_type to filter; all if none."""
        if party_id is not None or party_name is not None or doc_type is not None:
            return self._store.list_document_summaries_by_metadata(
                party_id=party_id,
                party_name=party_name,
                doc_type=doc_type,
            )
        return self._store.list_document_summaries()

    ## get document by id
    def get_document(self, doc_id: str) -> Document | None:
        """Return document by id or None if not found."""
        return self._store.get_document(doc_id)

    ## create a new document
    def create_document(
        self,
        title: str,
        content: str = "",
        *,
        id: str | None = None,
        party_id: str | None = None,
        party_name: str | None = None,
        doc_type: str | None = None,
    ) -> Document:
        """Create a new document with the given title and content. Optional id for seeded docs."""
        return self._store.create_document(
            title=title,
            content=content,
            id=id,
            party_id=party_id,
            party_name=party_name,
            doc_type=doc_type,
        )

    ## create a new document by copying a template (or any document)
    def create_document_from_template(
        self,
        template_id: str,
        *,
        title: str | None = None,
    ) -> Document:
        """
        Create a new document with the same content as the template. New doc gets a new id and version 1.
        Raises DocumentNotFoundError if template_id does not exist.
        """
        template = self._store.get_document(template_id)
        if template is None:
            raise DocumentNotFoundError()
        new_title = title if title is not None else f"Copy of {template.title}"
        return self._store.create_document(
            title=new_title,
            content=template.content,
        )

    ## create a new document from uploaded file
    ## we only accept .docx files and extract the text from the file
    def create_document_from_upload(
        self,
        title: str,
        *,
        file_bytes: bytes,
        filename: str | None = None,
        content_type: str | None = None,
        id: str | None = None,
        party_id: str | None = None,
        party_name: str | None = None,
        doc_type: str | None = None,
    ) -> Document:
        """
        Raises ValueError if file is not .docx or extraction fails.
        """
        if not is_docx_file(filename, content_type):
            raise ValueError("Only .docx files are accepted.")
        content = extract_text_from_bytes(
            file_bytes,
            filename=filename,
            content_type=content_type,
        )
        return self._store.create_document(
            title=title,
            content=content,
            id=id,
            party_id=party_id,
            party_name=party_name,
            doc_type=doc_type,
        )

    ## update document content
    ## expects changes with operation "replace", range { start, end }, and text
    ## sorts by range.start descending and applies so indices stay valid (handles add/remove)
    def update_document_content(
        self,
        doc_id: str,
        if_match_version: int | None,
        changes: list[DocumentChange],
    ) -> Document:
        """
        Apply range-based changes to document content. Each change has operation "replace",
        range { start, end }, and text (empty = removal). Sorted by range.start descending.
        Raises DocumentNotFoundError if doc does not exist.
        Raises PreconditionFailedError if If-Match version is missing or does not match.
        Raises ValueError if a range is out of bounds for the current content.
        """
        doc = self._store.get_document(doc_id)
        if doc is None:
            raise DocumentNotFoundError()
        if if_match_version is None or if_match_version != doc.version:
            raise PreconditionFailedError()
        content = doc.content
        n = len(content)
        # Sort by range.start descending so we can apply without tracking offset
        sorted_changes = sorted(changes, key=lambda c: c.range.start, reverse=True)
        for c in sorted_changes:
            start, end, text = c.range.start, c.range.end, c.text
            if start < 0 or end > n or start > end:
                raise ValueError(
                    f"Change range [{start}, {end}) out of bounds for content length {n}"
                )
            content = content[:start] + text + content[end:]
        updated = self._store.update_document(doc_id, content=content) ## update the store with the updated content
        assert updated is not None
        return updated


    ## SEARCH FEATURES
