"""Document routes: list, get by id, PATCH content. Thin HTTP layer; logic in service."""
from fastapi import APIRouter, Depends, Header, HTTPException, Path
from fastapi.responses import JSONResponse, Response

from app.core.deps import get_document_service
from app.models.api import DocumentSummaryResponse, PatchDocumentRequest
from app.routes.utils.formatting import parse_version_header
from app.routes.utils.mappers import doc_to_response, summary_to_response
from app.services.documents import DocumentNotFoundError, DocumentService, PreconditionFailedError

router = APIRouter(prefix="/documents", tags=["documents"])

VERSION_HEADER = "Version"

## list all documents (summaries only, no content)
@router.get("", response_model=list[DocumentSummaryResponse])
def list_documents(
    _service: DocumentService = Depends(get_document_service),
):
    """List all documents (summaries only, no content)."""
    summaries = _service.list_document_summaries()
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
