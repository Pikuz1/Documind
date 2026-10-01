import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_chroma import Chroma

from app.ai.prompts import NOT_FOUND
from app.ai.providers import FAKE_ANSWER, build_llm
from app.config import Settings
from app.core.rag import RagService
from app.dependencies import get_rag_service
from tests.fakes import QuotaExceededLLM


def ask(client: TestClient, document_id: str, question: str = "What is the notice period?"):
    return client.post("/api/query", json={"document_id": document_id, "question": question})


def stats(client: TestClient, document_id: str) -> dict:
    return client.get(f"/api/documents/{document_id}/stats").json()


def test_query_returns_answer_with_sources(client: TestClient, document: dict) -> None:
    response = ask(client, document["id"])

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == FAKE_ANSWER
    assert {source["page"] for source in body["sources"]} <= {1, 2}
    assert body["top_score"] == max(source["score"] for source in body["sources"])
    assert body["latency_ms"] >= 0


def test_query_is_logged_as_answered(client: TestClient, document: dict) -> None:
    ask(client, document["id"])

    assert stats(client, document["id"])["total_questions"] == 1
    assert stats(client, document["id"])["answered_count"] == 1


def test_query_without_relevant_chunks_is_logged_as_unanswered(
    app: FastAPI, client: TestClient, document: dict, vector_store: Chroma, settings: Settings
) -> None:
    strict = RagService(vector_store, build_llm(settings), min_score=2.0)  # nothing can pass
    app.dependency_overrides[get_rag_service] = lambda: strict

    response = ask(client, document["id"])

    assert response.json()["answer"] == NOT_FOUND
    assert response.json()["sources"] == []
    assert response.json()["top_score"] is None
    assert stats(client, document["id"])["answered_count"] == 0


def test_query_returns_503_when_llm_fails(
    app: FastAPI, client: TestClient, document: dict, vector_store: Chroma
) -> None:
    failing = RagService(vector_store, QuotaExceededLLM(responses=[]), min_score=-1)
    app.dependency_overrides[get_rag_service] = lambda: failing

    response = ask(client, document["id"])

    assert response.status_code == 503
    assert "try again later" in response.json()["detail"]
    assert stats(client, document["id"])["total_questions"] == 0  # failed calls aren't logged


def test_query_unknown_document_returns_404(client: TestClient) -> None:
    response = ask(client, "missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document 'missing' not found"}


@pytest.mark.parametrize("question", ["", "   ", "x" * 501])
def test_query_rejects_invalid_question(client: TestClient, document: dict, question: str) -> None:
    assert ask(client, document["id"], question).status_code == 422
