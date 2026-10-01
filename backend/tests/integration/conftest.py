from collections.abc import Callable, Iterator
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_chroma import Chroma

from app.ai.providers import build_embeddings, build_llm
from app.config import Settings, get_settings
from app.core.ingestion import IngestionService, build_splitter
from app.core.rag import RagService
from app.db.repository import Repository
from app.dependencies import (
    get_ingestion_service,
    get_rag_service,
    get_repository,
)
from app.main import create_app
from app.vectorstore.chroma_store import build_vector_store


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        ai_provider="fake",
        data_dir=tmp_path,
        min_relevance_score=-1,  # fake embeddings give arbitrary scores
        max_upload_mb=1,
    )


@pytest.fixture
def vector_store(settings: Settings) -> Chroma:
    return build_vector_store(build_embeddings(settings), persist_dir=None, collection=uuid4().hex)


@pytest.fixture
def app(settings: Settings, vector_store: Chroma) -> FastAPI:
    repository = Repository(settings.sqlite_path)
    splitter = build_splitter(settings.chunk_size, settings.chunk_overlap)
    ingestion = IngestionService(splitter, vector_store, repository)
    rag = RagService(
        vector_store,
        build_llm(settings),
        top_k=settings.top_k,
        min_score=settings.min_relevance_score,
    )

    app = create_app()
    app.dependency_overrides.update(
        {
            get_settings: lambda: settings,
            get_repository: lambda: repository,
            get_ingestion_service: lambda: ingestion,
            get_rag_service: lambda: rag,
        }
    )
    return app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


Upload = Callable[..., httpx.Response]


@pytest.fixture
def upload(client: TestClient) -> Upload:
    def _upload(content: bytes, filename: str = "contract.pdf") -> httpx.Response:
        return client.post("/api/documents", files={"file": (filename, content, "application/pdf")})

    return _upload


@pytest.fixture
def document(upload: Upload, sample_pdf: Path) -> dict:
    response = upload(sample_pdf.read_bytes())
    assert response.status_code == 201
    return response.json()
