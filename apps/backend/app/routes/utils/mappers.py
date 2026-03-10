"""Map DB/service types to API response models."""
from app.db.schemas import Document, DocumentSummary
from app.models.api import DocumentResponse, DocumentSummaryResponse



def doc_to_response(doc: Document) -> DocumentResponse:
    """Build DocumentResponse from DB Document."""
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        version=doc.version,
        party_id=doc.party_id,
        party_name=doc.party_name,
        doc_type=doc.doc_type,
    )


def summary_to_response(s: DocumentSummary) -> DocumentSummaryResponse:
    """Build DocumentSummaryResponse from DB DocumentSummary."""
    return DocumentSummaryResponse(
        id=s.id,
        title=s.title,
        created_at=s.created_at,
        updated_at=s.updated_at,
        version=s.version,
        party_id=s.party_id,
        party_name=s.party_name,
        doc_type=s.doc_type,
    )
