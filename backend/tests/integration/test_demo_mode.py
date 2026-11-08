"""The public demo: a preloaded sample document, and no uploads or deletes."""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings


@pytest.fixture
def settings(tmp_path: Path, sample_pdf: Path) -> Settings:
    # Replaces the shared fixture, so the shared `app` and `client` run in demo mode.
    return Settings(
        _env_file=None,
        ai_provider="fake",
        data_dir=tmp_path,
        min_relevance_score=-1,
        demo_document=sample_pdf,
    )


def test_health_reports_demo_mode(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok", "demo": True}


def test_sample_document_is_indexed_at_startup(client: TestClient) -> None:
    documents = client.get("/api/documents").json()

    assert [doc["filename"] for doc in documents] == ["sample_contract.pdf"]


def test_sample_document_is_indexed_only_once(app: FastAPI) -> None:
    with TestClient(app):  # first start
        pass
    with TestClient(app) as client:  # restart on the same data dir
        assert len(client.get("/api/documents").json()) == 1


def test_questions_work_on_the_sample_document(client: TestClient) -> None:
    document_id = client.get("/api/documents").json()[0]["id"]

    response = client.post("/api/query", json={"document_id": document_id, "question": "Notice?"})

    assert response.status_code == 200


def test_upload_is_refused(upload, sample_pdf: Path) -> None:
    response = upload(sample_pdf.read_bytes())

    assert response.status_code == 403
    assert response.json() == {"detail": "The public demo is read-only"}


def test_delete_is_refused(client: TestClient) -> None:
    document_id = client.get("/api/documents").json()[0]["id"]

    response = client.delete(f"/api/documents/{document_id}")

    assert response.status_code == 403
    assert len(client.get("/api/documents").json()) == 1
