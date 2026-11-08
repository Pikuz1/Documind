import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import documents, health, query
from app.config import Settings, get_settings
from app.core.errors import DocumentNotFoundError, EmptyDocumentError, LLMUnavailableError
from app.core.ingestion import IngestionService
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


def seed_demo_document(service: IngestionService, pdf_path: Path) -> None:
    # The data dir may survive a restart: index the sample only once.
    if not service.list_documents():
        service.ingest(pdf_path, pdf_path.name)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Build every service before the first request. Built lazily, two concurrent first
    # requests would initialise Chroma on the same directory at once and both fail.
    resolve = app.dependency_overrides.get  # respects test overrides
    for builder in (get_ingestion_service, get_rag_service):
        resolve(builder, builder)()
    settings = resolve(get_settings, get_settings)()
    if settings.demo_document:
        seed_demo_document(
            resolve(get_ingestion_service, get_ingestion_service)(), settings.demo_document
        )
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="DocuMind API", version="0.1.0", lifespan=lifespan)
    for router in (health.router, documents.router, query.router):
        app.include_router(router, prefix="/api")
    for error_type in ERROR_STATUS:
        app.add_exception_handler(error_type, handle_domain_error)
    # Mounted last: "/" matches everything, so /api routes must be registered first.
    if settings.static_dir and settings.static_dir.is_dir():
        app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="ui")
    return app


app = create_app()
