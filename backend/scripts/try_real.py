"""Try the pipeline for real: ingest a PDF and ask it questions via the real LLM.
Run from backend/:  python -m scripts.try_real [path/to/contract.pdf]
"""

import sys
import tempfile
from pathlib import Path

from app.ai.providers import build_embeddings, build_llm
from app.config import get_settings
from app.core.ingestion import IngestionService, build_splitter
from app.core.rag import RagService
from app.db.repository import Repository
from app.vectorstore.chroma_store import build_vector_store

DEFAULT_PDF = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "sample_contract.pdf"
QUESTIONS = [
    "What is the notice period?",
    "How much paid vacation do I get per year?",
    "What is the probation period?",
    "What is the monthly salary?",
    "Does this contract include a company car?",  # not in the fixture: expect "not found"
]


def main() -> None:
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    settings = get_settings()
    vector_store = build_vector_store(build_embeddings(settings), persist_dir=None)

    with tempfile.TemporaryDirectory() as tmp:
        repository = Repository(Path(tmp) / "try_real.db")
        splitter = build_splitter(settings.chunk_size, settings.chunk_overlap)
        ingestion = IngestionService(splitter, vector_store, repository)
        record = ingestion.ingest(pdf_path, pdf_path.name)
        print(f"Ingested '{record.filename}': {record.page_count} pages, ", end="")
        print(f"{record.chunk_count} chunks\n")

        rag = RagService(
            vector_store, build_llm(settings), settings.top_k, settings.min_relevance_score
        )
        for question in QUESTIONS:
            result = rag.answer(question, record.id)
            print(f"Q: {question}\nA: {result.answer}  (top_score={result.top_score})\n")


if __name__ == "__main__":
    main()
