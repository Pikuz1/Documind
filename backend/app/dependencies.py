"""Builds each service once and shares it across requests.

Routes receive these through FastAPI's Depends(); tests replace them with
app.dependency_overrides[...]."""

from functools import lru_cache

from langchain_chroma import Chroma

from app.ai.providers import build_embeddings, build_llm
from app.config import get_settings
from app.core.ingestion import IngestionService, build_splitter
from app.core.rag import RagService
from app.db.repository import Repository
from app.vectorstore.chroma_store import build_vector_store


@lru_cache
def get_repository() -> Repository:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return Repository(settings.sqlite_path)


@lru_cache
def get_vector_store() -> Chroma:
    # One instance for the whole app: ingestion writes to it, RAG reads from it.
    settings = get_settings()
    return build_vector_store(build_embeddings(settings), persist_dir=settings.chroma_dir)


@lru_cache
def get_ingestion_service() -> IngestionService:
    settings = get_settings()
    splitter = build_splitter(settings.chunk_size, settings.chunk_overlap)
    return IngestionService(splitter, get_vector_store(), get_repository())


@lru_cache
def get_rag_service() -> RagService:
    settings = get_settings()
    return RagService(
        get_vector_store(),
        build_llm(settings),
        top_k=settings.top_k,
        min_score=settings.min_relevance_score,
    )
