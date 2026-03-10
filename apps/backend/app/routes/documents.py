"""Document routes: list, get by id, PATCH content. Thin HTTP layer; logic in service."""
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.core.deps import get_document_service
from app.models.api import DocumentSummaryResponse, PatchDocumentRequest
from app.routes.utils.formatting import parse_version_header
from app.routes.utils.mappers import doc_to_response, summary_to_response
from app.services.documents import DocumentNotFoundError, DocumentService, PreconditionFailedError

router = APIRouter(prefix="/documents", tags=["documents"])

VERSION_HEADER = "Version"

## list documents (summaries only, no content). Optional query params filter by metadata.
@router.get("", response_model=list[DocumentSummaryResponse])
def list_documents(
    party_id: str | None = Query(None, description="Filter by party_id"),
    party_name: str | None = Query(None, description="Filter by party_name"),
    doc_type: str | None = Query(None, description="Filter by doc_type (e.g. template, loan_agreement)"),
    _service: DocumentService = Depends(get_document_service),
):
    """List documents (summaries only). Omit query params for all; use party_id, party_name, or doc_type to filter."""
    summaries = _service.list_document_summaries(
        party_id=party_id,
        party_name=party_name,
        doc_type=doc_type,
    )
    return [summary_to_response(s) for s in summaries]


## get full document by id
@router.get("/{doc_id}")
def get_document(
    doc_id: str = Path(..., description="Document ID"),
    if_none_match: str | None = Header(None, alias="If-None-Match"),
    _service: DocumentService = Depends(get_document_service),
) -> Response:
    """Get full document by id. 304 if If-None-Match matches current version."""
    doc = _service.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    client_version = parse_version_header(if_none_match)
    if client_version is not None and client_version == doc.version:
        return Response(
            status_code=304,
            headers={VERSION_HEADER: str(doc.version)},
        )
    body = doc_to_response(doc).model_dump(mode="json")
    return JSONResponse(
        content=body,
        headers={VERSION_HEADER: str(doc.version)},
    )

## apply changes to document content
## will return 412 if version does not match, client will need to fetch the latest version and apply changes again
@router.patch("/{doc_id}")
def patch_document(
    doc_id: str = Path(..., description="Document ID"),
    body: PatchDocumentRequest = ...,
    if_match: str | None = Header(None, alias="If-Match"),
    _service: DocumentService = Depends(get_document_service),
) -> JSONResponse:
    """Apply changes to document content. Requires If-Match: version. 412 if missing or mismatch."""
    try:
        version = parse_version_header(if_match)
        doc = _service.update_document_content(doc_id, version, body.changes)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except PreconditionFailedError:
        raise HTTPException(
            status_code=412,
            detail="Precondition Failed: If-Match is required and must match current document version.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    response_body = doc_to_response(doc).model_dump(mode="json")
    return JSONResponse(
        content=response_body,
        headers={VERSION_HEADER: str(doc.version)},
    )
