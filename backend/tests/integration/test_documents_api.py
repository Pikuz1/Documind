from pathlib import Path

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_returns_created_document(upload, sample_pdf: Path) -> None:
    response = upload(sample_pdf.read_bytes())

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "contract.pdf"
    assert body["page_count"] == 2
    assert body["chunk_count"] == 2
    assert body["id"] and body["created_at"]


def test_upload_drops_client_directories_from_filename(upload, sample_pdf: Path) -> None:
    response = upload(sample_pdf.read_bytes(), filename="../../secret/contract.pdf")

    assert response.json()["filename"] == "contract.pdf"


def test_upload_rejects_non_pdf_content(upload) -> None:
    # Named .pdf and sent as application/pdf, but the bytes aren't a PDF.
    response = upload(b"just some text", filename="notes.pdf")

    assert response.status_code == 415
    assert response.json() == {"detail": "Only PDF files are supported"}


def test_upload_rejects_file_over_size_limit(upload) -> None:
    too_large = b"%PDF-" + b"0" * (1024 * 1024)  # limit is 1 MB in the test settings

    response = upload(too_large)

    assert response.status_code == 413
    assert response.json() == {"detail": "File is larger than 1 MB"}


def test_upload_rejects_pdf_without_text(upload, empty_pdf: Path) -> None:
    response = upload(empty_pdf.read_bytes(), filename="scan.pdf")

    assert response.status_code == 422
    assert "no extractable text" in response.json()["detail"]


def test_upload_requires_a_file(client: TestClient) -> None:
    assert client.post("/api/documents").status_code == 422


def test_list_documents_empty(client: TestClient) -> None:
    response = client.get("/api/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_list_documents_returns_uploaded(client: TestClient, document: dict) -> None:
    assert client.get("/api/documents").json() == [document]


def test_delete_document(client: TestClient, document: dict) -> None:
    response = client.delete(f"/api/documents/{document['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/api/documents").json() == []


def test_delete_unknown_document_returns_404(client: TestClient) -> None:
    response = client.delete("/api/documents/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document 'missing' not found"}


def test_stats_for_new_document(client: TestClient, document: dict) -> None:
    response = client.get(f"/api/documents/{document['id']}/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_questions": 0,
        "answered_count": 0,
        "answer_rate": None,
        "average_top_score": None,
    }


def test_stats_for_unknown_document_returns_404(client: TestClient) -> None:
    assert client.get("/api/documents/missing/stats").status_code == 404
