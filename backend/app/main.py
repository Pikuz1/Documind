import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.routes import documents, health, query
from app.core.errors import DocumentNotFoundError, EmptyDocumentError, LLMUnavailableError
from app.dependencies import get_ingestion_service, get_rag_service

logger = logging.getLogger(__name__)

# Domain errors → HTTP status codes, in one place, so core/ never imports FastAPI.
ERROR_STATUS: dict[type[Exception], int] = {
    DocumentNotFoundError: status.HTTP_404_NOT_FOUND,
    EmptyDocumentError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    LLMUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


async def handle_domain_error(_request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, LLMUnavailableError):
        logger.error("LLM call failed", exc_info=exc.__cause__)
    return JSONResponse(status_code=ERROR_STATUS[type(exc)], content={"detail": str(exc)})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Build every service before the first request. Built lazily, two concurrent first
    # requests would initialise Chroma on the same directory at once and both fail.
    for builder in (get_ingestion_service, get_rag_service):
        app.dependency_overrides.get(builder, builder)()  # respects test overrides
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="DocuMind API", version="0.1.0", lifespan=lifespan)
    for router in (health.router, documents.router, query.router):
        app.include_router(router, prefix="/api")
    for error_type in ERROR_STATUS:
        app.add_exception_handler(error_type, handle_domain_error)
    return app


app = create_app()
