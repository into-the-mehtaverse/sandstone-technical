"""Document routes: list, get by id, PATCH content, search. Thin HTTP layer; logic in service."""
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response

from app.core.deps import get_document_service, get_search_service
from app.models.api import (
    CreateFromTemplateRequest,
    DocumentResponse,
    DocumentSummaryResponse,
    PatchDocumentRequest,
    SearchMatchResponse,
    SearchResponse,
)
from app.routes.utils.formatting import parse_version_header
from app.routes.utils.mappers import doc_to_response, summary_to_response
from app.services.documents import DocumentNotFoundError, DocumentService, PreconditionFailedError
from app.services.search import SearchService

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


## search (must be before /{doc_id} so /documents/search is not matched as doc_id)
@router.get("/search", response_model=SearchResponse)
def search_documents(
    q: str = Query(..., min_length=1, description="Search query (phrase, case-insensitive)"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    document_ids: list[str] | None = Query(None, description="Restrict to these document IDs"),
    _service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search all documents (or a subset by document_ids). Returns matches and total count."""
    page, total = _service.search(q=q, limit=limit, offset=offset, document_ids=document_ids)
    matches = [
        SearchMatchResponse(
            document_id=m.document_id,
            title=m.title,
            snippet=m.snippet,
            start_index=m.start_index,
            end_index=m.end_index,
        )
        for m in page
    ]
    return SearchResponse(matches=matches, total=total)


@router.get("/{doc_id}/search", response_model=SearchResponse)
def search_in_document(
    doc_id: str = Path(..., description="Document ID"),
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search within a single document. Same response shape as global search."""
    page, total = _service.search(q=q, limit=limit, offset=offset, document_ids=[doc_id])
    matches = [
        SearchMatchResponse(
            document_id=m.document_id,
            title=m.title,
            snippet=m.snippet,
            start_index=m.start_index,
            end_index=m.end_index,
        )
        for m in page
    ]
    return SearchResponse(matches=matches, total=total)


## create a new document from a template (copy); must be before /{doc_id}
@router.post("/from-template", status_code=201, response_model=DocumentResponse)
def create_from_template(
    body: CreateFromTemplateRequest,
    _service: DocumentService = Depends(get_document_service),
) -> JSONResponse:
    """Create a new document as a copy of the given template. Returns the new document (use its id for PATCH)."""
    try:
        doc = _service.create_document_from_template(
            body.template_id,
            title=body.title,
        )
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found")
    response_body = doc_to_response(doc).model_dump(mode="json")
    return JSONResponse(
        content=response_body,
        status_code=201,
        headers={VERSION_HEADER: str(doc.version)},
    )


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
        doc = _service.update_document_content(
            doc_id, version, body.changes, title=body.title
        )
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
