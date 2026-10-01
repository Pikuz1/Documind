import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from app.db.repository import DocumentRecord, Repository


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def repo(db_path: Path) -> Repository:
    return Repository(db_path)


def make_doc(doc_id: str = "doc-1") -> DocumentRecord:
    return DocumentRecord(id=doc_id, filename="contract.pdf", page_count=2, chunk_count=5)


def run_sql(db_path: Path, sql: str) -> list[tuple]:
    """Raw access for arranging and asserting state the Repository API doesn't expose."""
    with closing(sqlite3.connect(db_path)) as conn, conn:
        return conn.execute(sql).fetchall()


def test_add_document_returns_stored_record(repo: Repository) -> None:
    added = repo.add_document(make_doc())

    assert added.id == "doc-1"
    assert added.filename == "contract.pdf"
    assert added.page_count == 2
    assert added.chunk_count == 5
    assert added.created_at != ""  # filled in by the database default


def test_get_document_returns_added_record(repo: Repository) -> None:
    added = repo.add_document(make_doc())

    assert repo.get_document("doc-1") == added


def test_get_document_returns_none_for_unknown_id(repo: Repository) -> None:
    assert repo.get_document("missing") is None


def test_add_document_rejects_duplicate_id(repo: Repository) -> None:
    repo.add_document(make_doc())

    with pytest.raises(sqlite3.IntegrityError):
        repo.add_document(make_doc())


def test_list_documents_orders_newest_first(repo: Repository, db_path: Path) -> None:
    repo.add_document(make_doc("doc-older"))
    repo.add_document(make_doc("doc-newer"))
    # Force distinct timestamps instead of relying on wall-clock gaps between inserts.
    run_sql(db_path, "UPDATE documents SET created_at = '2026-01-01' WHERE id = 'doc-older'")
    run_sql(db_path, "UPDATE documents SET created_at = '2026-06-01' WHERE id = 'doc-newer'")

    assert [d.id for d in repo.list_documents()] == ["doc-newer", "doc-older"]


def test_list_documents_empty(repo: Repository) -> None:
    assert repo.list_documents() == []


def test_delete_document_returns_true_and_removes_row(repo: Repository) -> None:
    repo.add_document(make_doc())

    assert repo.delete_document("doc-1") is True
    assert repo.get_document("doc-1") is None


def test_delete_document_returns_false_for_unknown_id(repo: Repository) -> None:
    assert repo.delete_document("missing") is False


def test_delete_document_cascades_to_query_log(repo: Repository, db_path: Path) -> None:
    repo.add_document(make_doc())
    repo.log_query("doc-1", "What is the notice period?", 0.9, True, 120)

    repo.delete_document("doc-1")

    assert run_sql(db_path, "SELECT COUNT(*) FROM query_log") == [(0,)]


def test_document_stats_with_no_queries(repo: Repository) -> None:
    repo.add_document(make_doc())

    stats = repo.document_stats("doc-1")

    assert stats.total_questions == 0
    assert stats.answered_count == 0
    assert stats.answer_rate is None
    assert stats.average_top_score is None


def test_document_stats_aggregates_query_log(repo: Repository) -> None:
    repo.add_document(make_doc())
    repo.log_query("doc-1", "What is the notice period?", 0.9, True, 100)
    repo.log_query("doc-1", "What is my salary?", 0.8, True, 150)
    repo.log_query("doc-1", "Does it cover dental?", None, False, 90)

    stats = repo.document_stats("doc-1")

    assert stats.total_questions == 3
    assert stats.answered_count == 2
    assert stats.answer_rate == pytest.approx(2 / 3)
    assert stats.average_top_score == pytest.approx(0.85)  # AVG ignores the NULL score


def test_document_stats_only_counts_its_own_document(repo: Repository) -> None:
    repo.add_document(make_doc("doc-1"))
    repo.add_document(make_doc("doc-2"))
    repo.log_query("doc-1", "q1", 0.9, True, 100)
    repo.log_query("doc-2", "q2", 0.5, False, 100)

    assert repo.document_stats("doc-1").total_questions == 1
