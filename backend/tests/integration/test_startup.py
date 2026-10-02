from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app import dependencies
from app.config import get_settings
from app.main import create_app

CACHED_BUILDERS = [
    get_settings,
    dependencies.get_repository,
    dependencies.get_vector_store,
    dependencies.get_ingestion_service,
    dependencies.get_rag_service,
]


@pytest.fixture
def fresh_services(monkeypatch, tmp_path: Path) -> Iterator[None]:
    """Real (fake-AI) services on a temp dir, with nothing built yet."""
    monkeypatch.setenv("AI_PROVIDER", "fake")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    for builder in CACHED_BUILDERS:
        builder.cache_clear()
    yield
    for builder in CACHED_BUILDERS:
        builder.cache_clear()


@pytest.mark.usefixtures("fresh_services")
def test_services_are_built_at_startup() -> None:
    app = create_app()
    assert dependencies.get_vector_store.cache_info().currsize == 0

    with TestClient(app):
        assert dependencies.get_ingestion_service.cache_info().currsize == 1
        assert dependencies.get_rag_service.cache_info().currsize == 1


@pytest.mark.usefixtures("fresh_services")
def test_concurrent_first_requests_succeed(sample_pdf: Path) -> None:
    # Regression: the page's list request and an upload arriving together on a fresh
    # server used to initialise Chroma twice at once, and both returned 500.
    with TestClient(create_app()) as client, ThreadPoolExecutor(max_workers=2) as pool:
        listing = pool.submit(client.get, "/api/documents")
        upload = pool.submit(
            client.post,
            "/api/documents",
            files={"file": ("contract.pdf", sample_pdf.read_bytes(), "application/pdf")},
        )

        assert listing.result().status_code == 200
        assert upload.result().status_code == 201


def test_startup_uses_dependency_overrides() -> None:
    app = create_app()
    ingestion, rag = Mock(), Mock()
    app.dependency_overrides[dependencies.get_ingestion_service] = ingestion
    app.dependency_overrides[dependencies.get_rag_service] = rag

    with TestClient(app):
        ingestion.assert_called_once_with()
        rag.assert_called_once_with()
