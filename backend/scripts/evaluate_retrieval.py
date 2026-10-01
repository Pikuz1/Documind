"""Measure retrieval quality (hit rate@k) for different chunking settings.
Run from backend/: python -m scripts.evaluate_retrieval

Retrieval only — no LLM calls, so it's free and deterministic.
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import yaml
from langchain_core.embeddings import Embeddings

from app.ai.providers import build_embeddings
from app.config import get_settings
from app.core.ingestion import IngestionService, build_splitter
from app.db.repository import Repository
from app.vectorstore.chroma_store import build_vector_store

EVAL_DIR = Path(__file__).resolve().parent.parent / "eval"
CHUNK_CONFIGS = [(400, 60), (800, 120), (1200, 200)]
K = 4


@dataclass(frozen=True)
class GoldenQuestion:
    question: str
    page: int


@dataclass(frozen=True)
class EvalResult:
    chunk_size: int
    chunk_overlap: int
    chunk_count: int
    hit_at_1: float
    hit_at_k: float
    avg_top_score: float
    misses: list[str]


def load_golden_set(path: Path) -> tuple[str, list[GoldenQuestion]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["document"], [GoldenQuestion(**q) for q in data["questions"]]


def evaluate(
    embeddings: Embeddings,
    document: str,
    questions: list[GoldenQuestion],
    chunk_size: int,
    chunk_overlap: int,
) -> EvalResult:
    store = build_vector_store(embeddings, persist_dir=None, collection=uuid4().hex)
    with tempfile.TemporaryDirectory() as tmp:
        splitter = build_splitter(chunk_size, chunk_overlap)
        service = IngestionService(splitter, store, Repository(Path(tmp) / "eval.db"))
        record = service.ingest(EVAL_DIR / document, document)

    hits_at_1 = hits_at_k = 0
    top_scores: list[float] = []
    misses: list[str] = []
    for item in questions:
        results = store.similarity_search_with_relevance_scores(
            item.question, k=K, filter={"document_id": record.id}
        )
        pages = [doc.metadata["page"] for doc, _ in results]
        hits_at_1 += pages[0] == item.page
        if item.page in pages:
            hits_at_k += 1
        else:
            misses.append(f"{item.question} (expected p. {item.page}, got {pages})")
        top_scores.append(results[0][1])

    total = len(questions)
    return EvalResult(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        chunk_count=record.chunk_count,
        hit_at_1=hits_at_1 / total,
        hit_at_k=hits_at_k / total,
        avg_top_score=sum(top_scores) / total,
        misses=misses,
    )


def main() -> None:
    document, questions = load_golden_set(EVAL_DIR / "golden_set.yaml")
    # Always evaluate the real embedding model, whatever AI_PROVIDER says.
    embeddings = build_embeddings(get_settings().model_copy(update={"ai_provider": "real"}))

    results = [
        evaluate(embeddings, document, questions, size, overlap) for size, overlap in CHUNK_CONFIGS
    ]

    print(f"\n{len(questions)} questions against {document}\n")
    print(f"| chunk_size | overlap | chunks | hit@1 | hit@{K} | avg top score |")
    print("|---:|---:|---:|---:|---:|---:|")
    for r in results:
        print(
            f"| {r.chunk_size} | {r.chunk_overlap} | {r.chunk_count} "
            f"| {r.hit_at_1:.0%} | {r.hit_at_k:.0%} | {r.avg_top_score:.3f} |"
        )
    for r in results:
        for miss in r.misses:
            print(f"miss @ {r.chunk_size}/{r.chunk_overlap}: {miss}")


if __name__ == "__main__":
    main()
