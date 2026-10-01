from uuid import uuid4

from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

from app.vectorstore.chroma_store import build_vector_store, chunk_ids


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
