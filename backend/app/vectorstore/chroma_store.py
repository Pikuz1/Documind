from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

COLLECTION = "contract_chunks"


def cosine_relevance(distance: float) -> float:
    """Map Chroma's cosine distance (0..2) to a relevance score (0..1).

    LangChain's default (1 - distance) goes negative for unrelated text, which makes
    it log a warning containing the matched chunks' text — contract content in logs.
    """
    return max(0.0, 1.0 - distance)


def build_vector_store(
    embeddings: Embeddings, persist_dir: Path | None, collection: str = COLLECTION
) -> Chroma:
    """LangChain wrapper around a Chroma collection.

    persist_dir=None → in-memory (tests). A path → saved to disk (app).
    The embedding function is attached here, so add_documents() and
    similarity_search() embed text automatically.
    """
    return Chroma(
        collection_name=collection,
        embedding_function=embeddings,
        persist_directory=str(persist_dir) if persist_dir else None,
        collection_metadata={"hnsw:space": "cosine"},  # distance metric for the index
        relevance_score_fn=cosine_relevance,
    )


def chunk_ids(document_id: str, count: int) -> list[str]:
    """Deterministic ids — we can delete a document's chunks without searching."""
    return [f"{document_id}:{i}" for i in range(count)]
