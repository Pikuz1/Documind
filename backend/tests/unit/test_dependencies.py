from collections.abc import Iterator
from pathlib import Path

import pytest

from app import dependencies
from app.ai.providers import FAKE_ANSWER
from app.config import get_settings

CACHED_BUILDERS = [
    get_settings,
    dependencies.get_repository,
    dependencies.get_vector_store,
    dependencies.get_ingestion_service,
    dependencies.get_rag_service,
]


def clear_caches() -> None:
    for builder in CACHED_BUILDERS:
        builder.cache_clear()


@pytest.fixture(autouse=True)
def data_dir(monkeypatch, tmp_path: Path) -> Iterator[Path]:
    data_dir = tmp_path / "data"
    monkeypatch.setenv("AI_PROVIDER", "fake")
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("MIN_RELEVANCE_SCORE", "-1")  # fake embeddings give arbitrary scores
    clear_caches()
    yield data_dir
    clear_caches()


def test_get_repository_creates_database_in_data_dir(data_dir: Path) -> None:
    dependencies.get_repository()

    assert (data_dir / "documind.db").is_file()


def test_builders_are_cached() -> None:
    for builder in CACHED_BUILDERS:
        assert builder() is builder()


def test_vector_store_persists_under_chroma_dir(data_dir: Path) -> None:
    dependencies.get_vector_store()

    assert (data_dir / "chroma").is_dir()


def test_ingested_document_is_answerable_through_rag(sample_pdf: Path) -> None:
    record = dependencies.get_ingestion_service().ingest(sample_pdf, "contract.pdf")

    result = dependencies.get_rag_service().answer("What is the notice period?", record.id)

    # Proves both services share one store: RAG finds what ingestion wrote.
    assert result.answer == FAKE_ANSWER
    assert result.sources
    assert dependencies.get_repository().get_document(record.id) == record
