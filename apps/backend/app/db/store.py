"""
Document store: SQLite-backed persistence. Same interface for app and tests.
"""
import sqlite3
from datetime import datetime, timezone

from app.db.schemas import Document, DocumentSummary

## table schema defined here, can be moved into orm layer if project is extended
_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER NOT NULL,
    party_id TEXT,
    party_name TEXT,
    doc_type TEXT
)
"""

## reuseable list for selecting columns from table
_SELECT_COLS = "id, title, content, created_at, updated_at, version, party_id, party_name, doc_type"
_SUMMARY_COLS = "id, title, created_at, updated_at, version, party_id, party_name, doc_type"

## map full doc including content to Document Model
def _row_to_document(row: tuple) -> Document:
    """Build Document from table row."""
    (
        id_,
        title,
        content,
        created_at_s,
        updated_at_s,
        version,
        party_id,
        party_name,
        doc_type,
    ) = row
    created_at = datetime.fromisoformat(created_at_s)
    updated_at = datetime.fromisoformat(updated_at_s)
    return Document(
        id=id_,
        title=title,
        content=content,
        created_at=created_at,
        updated_at=updated_at,
        version=version,
        party_id=party_id,
        party_name=party_name,
        doc_type=doc_type,
    )

## map doc summary to DocumentSummary Model (no content)
def _row_to_summary(row: tuple) -> DocumentSummary:
    """Build DocumentSummary from table row (no content)."""
    (
        id_,
        title,
        created_at_s,
        updated_at_s,
        version,
        party_id,
        party_name,
        doc_type,
    ) = row
    created_at = datetime.fromisoformat(created_at_s)
    updated_at = datetime.fromisoformat(updated_at_s)
    return DocumentSummary(
        id=id_,
        title=title,
        created_at=created_at,
        updated_at=updated_at,
        version=version,
        party_id=party_id,
        party_name=party_name,
        doc_type=doc_type,
    )

## time util
def _datetime_iso(dt: datetime) -> str:
    """Serialize datetime to ISO string for SQLite."""
    return dt.isoformat()



## store class
class DocumentStore:
    """SQLite-backed store for documents. Use path=':memory:' for tests."""

    def __init__(self, path: str = ":memory:") -> None:
        ## initialize connection and create document table
        self._path = path
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(_TABLE_SQL)

    ## select all documents with content
    def list_documents(self) -> list[Document]:
        cur = self._conn.execute(f"SELECT {_SELECT_COLS} FROM documents")
        return [_row_to_document(row) for row in cur.fetchall()]

    ## select all documents without content for list views
    def list_document_summaries(self) -> list[DocumentSummary]:
        cur = self._conn.execute(f"SELECT {_SUMMARY_COLS} FROM documents")
        return [_row_to_summary(row) for row in cur.fetchall()]

    ## select document by id
    def get_document(self, doc_id: str) -> Document | None:
        """Return document by id or None if not found."""
        cur = self._conn.execute(
            f"SELECT {_SELECT_COLS} FROM documents WHERE id = ?",
            (doc_id,),
        )
        row = cur.fetchone()
        return _row_to_document(row) if row else None

    ## create a new document
    def create_document(
        self,
        title: str,
        content: str = "",
        *,
        party_id: str | None = None,
        party_name: str | None = None,
        doc_type: str | None = None,
    ) -> Document:
        """Create a new document and return it."""
        doc = Document.create(
            title=title,
            content=content,
            party_id=party_id,
            party_name=party_name,
            doc_type=doc_type,
        )
        self._conn.execute(
            "INSERT INTO documents (id, title, content, created_at, updated_at, version, party_id, party_name, doc_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                doc.id,
                doc.title,
                doc.content,
                _datetime_iso(doc.created_at),
                _datetime_iso(doc.updated_at),
                doc.version,
                doc.party_id,
                doc.party_name,
                doc.doc_type,
            ),
        )
        self._conn.commit()
        return doc

    ## update existing document
    def update_document(
        self,
        doc_id: str,
        *,
        content: str | None = None,
        title: str | None = None,
        party_id: str | None = None,
        party_name: str | None = None,
        doc_type: str | None = None,
    ) -> Document | None:
        """Update document by id. Bumps version. Returns None if not found."""
        doc = self.get_document(doc_id)
        if doc is None:
            return None
        new_content = content if content is not None else doc.content
        new_title = title if title is not None else doc.title
        new_party_id = party_id if party_id is not None else doc.party_id
        new_party_name = party_name if party_name is not None else doc.party_name
        new_doc_type = doc_type if doc_type is not None else doc.doc_type
        now = datetime.now(timezone.utc)
        new_version = doc.version + 1
        self._conn.execute(
            "UPDATE documents SET title = ?, content = ?, updated_at = ?, version = ?, party_id = ?, party_name = ?, doc_type = ? WHERE id = ?",
            (
                new_title,
                new_content,
                _datetime_iso(now),
                new_version,
                new_party_id,
                new_party_name,
                new_doc_type,
                doc_id,
            ),
        )
        self._conn.commit()
        return Document(
            id=doc.id,
            title=new_title,
            content=new_content,
            created_at=doc.created_at,
            updated_at=now,
            version=new_version,
            party_id=new_party_id,
            party_name=new_party_name,
            doc_type=new_doc_type,
        )
