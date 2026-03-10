"""Exception handlers that return shared ErrorResponse format. Register on the app in create_app."""
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models.errors import ErrorResponse


def _error_response(status_code: int, message: str) -> JSONResponse:
    body = ErrorResponse(error=message, code=status_code).model_dump()
    return JSONResponse(status_code=status_code, content=body)


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else json.dumps(exc.detail)
    return _error_response(exc.status_code, detail)


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    msg = " ".join(
        f"{e.get('loc', [])!s}: {e.get('msg', '')}" for e in exc.errors()
    ) or "Validation error"
    return _error_response(422, msg)


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    return _error_response(500, "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(Exception)(unhandled_exception_handler)
