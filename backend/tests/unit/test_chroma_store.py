import warnings
from uuid import uuid4

import pytest
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

from app.ai.providers import EMBEDDING_DIM
from app.vectorstore.chroma_store import build_vector_store, chunk_ids, cosine_relevance

# With these fake vectors, the query is slightly "opposite" to one chunk: similarity < 0.
CHUNKS = [
    "Employment Contract\nNotice period: The notice period is three months to the end of the "
    "month.\nSalary: The monthly gross salary is EUR 4,500.",
    "Vacation: The employee receives 30 working days of paid vacation per year.\n"
    "Probation period: The probation period is six months.",
]
QUERY = "What is the notice period?"


@pytest.mark.parametrize(
    ("distance", "expected"), [(0.0, 1.0), (0.25, 0.75), (1.0, 0.0), (1.6, 0.0), (2.0, 0.0)]
)
def test_cosine_relevance_maps_distance_to_unit_range(distance: float, expected: float) -> None:
    assert cosine_relevance(distance) == pytest.approx(expected)


def test_langchain_default_relevance_warns_for_negative_similarity() -> None:
    # Guards the test below: proves this input really produces an out-of-range score.
    store = Chroma(
        collection_name=uuid4().hex,
        embedding_function=DeterministicFakeEmbedding(size=EMBEDDING_DIM),
        collection_metadata={"hnsw:space": "cosine"},
    )
    store.add_texts(CHUNKS)

    with pytest.warns(UserWarning, match="Relevance scores must be between 0 and 1"):
        store.similarity_search_with_relevance_scores(QUERY, k=2)


def test_relevance_scores_stay_in_range_without_warnings() -> None:
    store = build_vector_store(
        DeterministicFakeEmbedding(size=EMBEDDING_DIM), persist_dir=None, collection=uuid4().hex
    )
    store.add_texts(CHUNKS)

    with warnings.catch_warnings():
        warnings.simplefilter("error")  # any warning (which would log chunk text) fails the test
        results = store.similarity_search_with_relevance_scores(QUERY, k=2)

    assert all(0.0 <= score <= 1.0 for _, score in results)


def test_build_vector_store_stores_and_searches_in_memory() -> None:
    store = build_vector_store(
        DeterministicFakeEmbedding(size=8), persist_dir=None, collection=uuid4().hex
    )
    docs = [Document(page_content="notice period is three months")]

    store.add_documents(docs, ids=chunk_ids("doc-1", len(docs)))

    results = store.similarity_search("notice period", k=1)
    assert results[0].page_content == "notice period is three months"


def test_build_vector_store_persists_to_disk(tmp_path) -> None:
    collection = uuid4().hex
    embeddings = DeterministicFakeEmbedding(size=8)
    docs = [Document(page_content="vacation is 30 days per year")]

    store = build_vector_store(embeddings, persist_dir=tmp_path, collection=collection)
    store.add_documents(docs, ids=chunk_ids("doc-1", len(docs)))

    reopened = build_vector_store(embeddings, persist_dir=tmp_path, collection=collection)
    results = reopened.similarity_search("vacation", k=1)
    assert results[0].page_content == "vacation is 30 days per year"


def test_chunk_ids_are_deterministic_and_indexed() -> None:
    assert chunk_ids("doc-1", 3) == ["doc-1:0", "doc-1:1", "doc-1:2"]


def test_chunk_ids_empty_for_zero_count() -> None:
    assert chunk_ids("doc-1", 0) == []
