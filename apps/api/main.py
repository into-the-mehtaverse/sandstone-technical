from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Sandstone Document API", lifespan=lifespan)
app.include_router(documents.router)
