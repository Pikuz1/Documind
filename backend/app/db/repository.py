import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


@dataclass(frozen=True)
class DocumentRecord:
    id: str
    filename: str
    page_count: int
    chunk_count: int
    created_at: str = ""


@dataclass(frozen=True)
class DocumentStats:
    total_questions: int
    answered_count: int
    answer_rate: float | None
    average_top_score: float | None


class Repository:
    def __init__(self, db_path: Path | str) -> None:
        self._db_path = str(db_path)
        with closing(self._connect()) as conn, conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # rows behave like dicts
        conn.execute("PRAGMA foreign_keys = ON")  # SQLite needs this for ON DELETE CASCADE
        return conn

    def add_document(self, doc: DocumentRecord) -> DocumentRecord:
        with closing(self._connect()) as conn, conn:  # `with conn` = commit or rollback
            row = conn.execute(
                "INSERT INTO documents (id, filename, page_count, chunk_count)"
                " VALUES (?, ?, ?, ?) RETURNING *",
                (doc.id, doc.filename, doc.page_count, doc.chunk_count),  # always parameterised!
            ).fetchone()
        return DocumentRecord(**dict(row))

    def get_document(self, doc_id: str) -> DocumentRecord | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return DocumentRecord(**dict(row)) if row else None

    def list_documents(self) -> list[DocumentRecord]:
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        return [DocumentRecord(**dict(row)) for row in rows]

    def delete_document(self, doc_id: str) -> bool:
        with closing(self._connect()) as conn, conn:
            deleted = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,)).rowcount
        return deleted > 0

    def log_query(
        self,
        document_id: str,
        question: str,
        top_score: float | None,
        answered: bool,
        latency_ms: int,
    ) -> None:
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "INSERT INTO query_log (document_id, question, top_score, answered, latency_ms)"
                " VALUES (?, ?, ?, ?, ?)",
                (document_id, question, top_score, int(answered), latency_ms),
            )

    def document_stats(self, document_id: str) -> DocumentStats:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total, SUM(answered) AS answered_count,"
                " AVG(top_score) AS avg_score FROM query_log WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        total: int = row["total"]
        answered_count: int = row["answered_count"] or 0
        return DocumentStats(
            total_questions=total,
            answered_count=answered_count,
            answer_rate=(answered_count / total) if total else None,
            average_top_score=row["avg_score"],
        )
