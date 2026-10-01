"""Try the pipeline for real: ingest a PDF and ask it questions via the real LLM.
Run: AI_PROVIDER=real python scripts/try_real.py path/to/contract.pdf
"""

import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from app.ai.providers import build_embeddings, build_llm
from app.config import get_settings
from app.core.ingestion import IngestionService, build_splitter
from app.core.rag import RagService
from app.db.repository import Repository
from app.vectorstore.chroma_store import build_vector_store

load_dotenv()
settings = get_settings()

pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/fixtures/sample_contract.pdf")

embeddings = build_embeddings(settings)
vector_store = build_vector_store(embeddings, persist_dir=None)
db_path = Path(tempfile.mkdtemp()) / "try_real.db"
repository = Repository(db_path)
splitter = build_splitter(settings.chunk_size, settings.chunk_overlap)

ingestion = IngestionService(splitter, vector_store, repository)
record = ingestion.ingest(pdf_path, pdf_path.name)
print(f"Ingested '{record.filename}': {record.page_count} pages, {record.chunk_count} chunks\n")

rag = RagService(vector_store, build_llm(settings), settings.top_k, settings.min_relevance_score)

questions = [
    "What is the notice period?",
    "How much paid vacation do I get per year?",
    "What is the probation period?",
    "What is the monthly salary?",
    "Does this contract include a company car?",  # not in the document — should say "not found"
]
for question in questions:
    result = rag.answer(question, record.id)
    print(f"Q: {question}\nA: {result.answer}  (top_score={result.top_score})\n")
