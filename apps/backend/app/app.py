"""FastAPI app factory. Main entry for the server."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    """Build FastAPI app. Routers and error handlers are registered here."""
    app = FastAPI(
        title="Sandstone Document API",
        lifespan=lifespan,
    )
    app.include_router(documents.router)
    return app


app = create_app()
