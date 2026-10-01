from uuid import uuid4

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding

from app.core.errors import DocumentNotFoundError, EmptyDocumentError
from app.core.ingestion import IngestionService, build_splitter
from app.db.repository import Repository
from app.vectorstore.chroma_store import build_vector_store


@pytest.fixture
def ingestion(tmp_path):
    embeddings = DeterministicFakeEmbedding(size=8)
    vector_store = build_vector_store(embeddings, persist_dir=None, collection=uuid4().hex)
    repository = Repository(tmp_path / "test.db")
    splitter = build_splitter(chunk_size=800, chunk_overlap=120)
    service = IngestionService(splitter, vector_store, repository)
    return service, vector_store, repository


def test_ingest_creates_chunks_with_correct_metadata(ingestion, sample_pdf) -> None:
    service, vector_store, _ = ingestion

    record = service.ingest(sample_pdf, "contract.pdf")

    assert record.filename == "contract.pdf"
    assert record.page_count == 2
    assert record.chunk_count == 2  # each page's text is short enough to stay one chunk

    results = vector_store.similarity_search(
        "notice period", k=1, filter={"document_id": record.id}
    )
    assert results[0].metadata == {
        "document_id": record.id,
        "filename": "contract.pdf",
        "page": 1,
        "chunk_index": 0,
    }


def test_ingest_persists_sql_record(ingestion, sample_pdf) -> None:
    service, _, repository = ingestion

    record = service.ingest(sample_pdf, "contract.pdf")

    assert repository.get_document(record.id) == record


def test_ingest_raises_on_empty_pdf(ingestion, empty_pdf) -> None:
    service, _, _ = ingestion

    with pytest.raises(EmptyDocumentError, match="no extractable text"):
        service.ingest(empty_pdf, "empty.pdf")


def test_ingest_removes_vectors_when_sql_insert_fails(ingestion, sample_pdf, monkeypatch) -> None:
    service, vector_store, repository = ingestion

    def fail(_record):
        raise RuntimeError("disk full")

    monkeypatch.setattr(repository, "add_document", fail)

    with pytest.raises(RuntimeError, match="disk full"):
        service.ingest(sample_pdf, "contract.pdf")

    assert vector_store.get()["ids"] == []  # no orphaned chunks left behind


def test_delete_removes_vectors_and_sql_row(ingestion, sample_pdf) -> None:
    service, vector_store, repository = ingestion
    record = service.ingest(sample_pdf, "contract.pdf")

    service.delete(record.id)

    assert repository.get_document(record.id) is None
    results = vector_store.similarity_search(
        "notice period", k=4, filter={"document_id": record.id}
    )
    assert results == []


def test_delete_unknown_document_raises(ingestion) -> None:
    service, _, _ = ingestion

    with pytest.raises(DocumentNotFoundError):
        service.delete("missing")


def test_get_returns_ingested_record(ingestion, sample_pdf) -> None:
    service, _, _ = ingestion
    record = service.ingest(sample_pdf, "contract.pdf")

    assert service.get(record.id) == record


def test_get_unknown_document_raises(ingestion) -> None:
    service, _, _ = ingestion

    with pytest.raises(DocumentNotFoundError, match="missing"):
        service.get("missing")


def test_list_documents_returns_ingested_records(ingestion, sample_pdf) -> None:
    service, _, _ = ingestion
    record = service.ingest(sample_pdf, "contract.pdf")

    assert service.list_documents() == [record]
