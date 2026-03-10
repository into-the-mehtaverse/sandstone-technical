"""FastAPI app factory. Main entry for the server."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exception_handlers import register_exception_handlers
from app.models.errors import ErrorResponse
from app.routes import documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    """Build FastAPI app. Routers and error handlers are registered here."""
    app = FastAPI(
        title="Sandstone Document API",
        lifespan=lifespan,
        responses={
            400: {"model": ErrorResponse, "description": "Bad request"},
            404: {"model": ErrorResponse, "description": "Not found"},
            412: {"model": ErrorResponse, "description": "Precondition failed"},
            422: {"model": ErrorResponse, "description": "Validation error"},
            500: {"model": ErrorResponse, "description": "Internal server error"},
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(documents.router)
    return app


app = create_app()
