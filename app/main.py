"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import engine
from app.exceptions import (
    ApiError,
    api_error_handler,
    http_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)
from app.models import Base
from app.routers import media, tweets, users
from app.schemas import ErrorResponse
from app.seed import seed_demo_data

from fastapi.responses import FileResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create database tables and demo users before serving requests."""
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    yield


app = FastAPI(
    title="Corporate Microblog API",
    description="Backend for a corporate microblog service.",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        status_code: {"model": ErrorResponse}
        for status_code in (401, 403, 404, 409, 422, 500)
    },
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)
app.add_exception_handler(
    StarletteHTTPException,
    http_error_handler,
)
app.add_exception_handler(
    Exception,
    unexpected_error_handler,
)

app.include_router(tweets.router)
app.include_router(users.router)
app.include_router(media.router)

media_directory = Path("static/media")
media_directory.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static/media",
    StaticFiles(directory=str(media_directory)),
    name="media",
)


@app.get(
    "/{full_path:path}",
    include_in_schema=False,
)
def serve_frontend(full_path: str) -> FileResponse:
    """Serve the Vue single-page application."""
    index_file = Path("frontend") / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Frontend is not available",
        )

    return FileResponse(index_file)


@app.get("/health", tags=["Service"])
def healthcheck() -> dict[str, str]:
    """Return application health status."""
    return {"status": "ok"}