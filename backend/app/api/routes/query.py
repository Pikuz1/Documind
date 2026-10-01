import time

from fastapi import APIRouter

from app.api.schemas import QueryIn, QueryOut, SourceOut
from app.dependencies import IngestionServiceDep, RagServiceDep, RepositoryDep

router = APIRouter(tags=["query"])


@router.post("/query")
def ask(
    body: QueryIn,
    documents: IngestionServiceDep,
    rag: RagServiceDep,
    repository: RepositoryDep,
) -> QueryOut:
    documents.get(body.document_id)  # raises DocumentNotFoundError → 404

    started = time.perf_counter()
    result = rag.answer(body.question, body.document_id)
    latency_ms = round((time.perf_counter() - started) * 1000)

    repository.log_query(
        body.document_id, body.question, result.top_score, result.answered, latency_ms
    )
    return QueryOut(
        answer=result.answer,
        sources=[SourceOut.model_validate(source) for source in result.sources],
        top_score=result.top_score,
        latency_ms=latency_ms,
    )
