from uuid import uuid4

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models import FakeListChatModel

from app.ai.prompts import NOT_FOUND
from app.core.errors import LLMUnavailableError
from app.core.rag import RagAnswer, RagService, Source
from app.vectorstore.chroma_store import build_vector_store, chunk_ids
from tests.fakes import ExplodingLLM, QuotaExceededLLM


def make_store(docs_by_id: dict[str, list[tuple[str, int]]]):
    """docs_by_id: {document_id: [(text, page), ...]}"""
    embeddings = DeterministicFakeEmbedding(size=8)
    store = build_vector_store(embeddings, persist_dir=None, collection=uuid4().hex)
    for document_id, entries in docs_by_id.items():
        docs = [
            Document(page_content=text, metadata={"document_id": document_id, "page": page})
            for text, page in entries
        ]
        store.add_documents(docs, ids=chunk_ids(document_id, len(docs)))
    return store


def test_answer_returns_llm_response_and_sources() -> None:
    store = make_store({"doc-1": [("Notice period: three months.", 1)]})
    llm = FakeListChatModel(responses=["The notice period is three months (p. 1)."])
    service = RagService(store, llm, top_k=4, min_score=-1)

    result = service.answer("What is the notice period?", "doc-1")

    assert result.answer == "The notice period is three months (p. 1)."
    assert len(result.sources) == 1
    assert result.sources[0].page == 1
    assert result.sources[0].text == "Notice period: three months."
    assert result.top_score == result.sources[0].score


def test_answer_returns_not_found_without_calling_llm_when_below_threshold() -> None:
    store = make_store({"doc-1": [("Notice period: three months.", 1)]})
    service = RagService(store, ExplodingLLM(responses=[]), top_k=4, min_score=2.0)

    result = service.answer("What is the notice period?", "doc-1")

    assert result.answer == NOT_FOUND
    assert result.sources == []


def test_answer_keeps_documents_separate_via_filter() -> None:
    store = make_store(
        {
            "doc-1": [("Notice period: three months.", 1)],
            "doc-2": [("Rent is 950 EUR per month.", 1)],
        }
    )
    llm = FakeListChatModel(responses=["answer"])
    service = RagService(store, llm, top_k=4, min_score=-1)

    result = service.answer("What is the notice period?", "doc-1")

    assert len(result.sources) == 1
    assert result.sources[0].text == "Notice period: three months."


def test_answer_returns_not_found_for_document_without_chunks() -> None:
    store = make_store({"doc-1": [("Notice period: three months.", 1)]})
    service = RagService(store, ExplodingLLM(responses=[]), top_k=4, min_score=-1)

    result = service.answer("What is the notice period?", "unknown-doc")

    assert result.answer == NOT_FOUND


def test_top_score_is_none_when_no_sources() -> None:
    assert RagAnswer(answer=NOT_FOUND, sources=[]).top_score is None


def test_answer_wraps_llm_failures() -> None:
    store = make_store({"doc-1": [("Notice period: three months.", 1)]})
    service = RagService(store, QuotaExceededLLM(responses=[]), top_k=4, min_score=-1)

    with pytest.raises(LLMUnavailableError) as exc_info:
        service.answer("What is the notice period?", "doc-1")

    assert isinstance(exc_info.value.__cause__, RuntimeError)  # original error kept for logs


def test_answered_is_true_for_a_real_answer() -> None:
    source = Source(page=1, text="Notice period: three months.", score=0.8)

    assert RagAnswer(answer="Three months (p. 1).", sources=[source]).answered is True


def test_answered_is_false_when_llm_declines_despite_sources() -> None:
    source = Source(page=1, text="Notice period: three months.", score=0.8)

    assert RagAnswer(answer=f"  {NOT_FOUND}\n", sources=[source]).answered is False
