import sqlite3

import pytest

from app.db.repository import DocumentRecord, Repository


@pytest.fixture
def repo(tmp_path):
    return Repository(tmp_path / "test.db")


def make_doc(doc_id: str = "doc-1") -> DocumentRecord:
    return DocumentRecord(id=doc_id, filename="contract.pdf", page_count=2, chunk_count=5)


def test_add_and_get_document(repo: Repository) -> None:
    added = repo.add_document(make_doc())

    assert added.id == "doc-1"
    assert added.filename == "contract.pdf"
    assert added.created_at != ""

    fetched = repo.get_document("doc-1")
    assert fetched == added


def test_get_document_returns_none_for_unknown_id(repo: Repository) -> None:
    assert repo.get_document("missing") is None


def test_list_documents_orders_newest_first(repo: Repository) -> None:
    repo.add_document(make_doc("doc-older"))
    repo.add_document(make_doc("doc-newer"))

    # Force distinct, known timestamps instead of relying on wall-clock gaps between inserts.
    with sqlite3.connect(repo._db_path) as conn:
        conn.execute("UPDATE documents SET created_at = '2026-01-01' WHERE id = 'doc-older'")
        conn.execute("UPDATE documents SET created_at = '2026-06-01' WHERE id = 'doc-newer'")

    documents = repo.list_documents()

    assert [d.id for d in documents] == ["doc-newer", "doc-older"]


def test_list_documents_empty(repo: Repository) -> None:
    assert repo.list_documents() == []


def test_delete_document_returns_true_and_removes_row(repo: Repository) -> None:
    repo.add_document(make_doc())

    assert repo.delete_document("doc-1") is True
    assert repo.get_document("doc-1") is None


def test_delete_document_returns_false_for_unknown_id(repo: Repository) -> None:
    assert repo.delete_document("missing") is False


def test_delete_document_cascades_to_query_log(repo: Repository) -> None:
    repo.add_document(make_doc())
    repo.log_query("doc-1", "What is the notice period?", 0.9, True, 120)

    repo.delete_document("doc-1")

    with sqlite3.connect(repo._db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM query_log WHERE document_id = 'doc-1'"
        ).fetchone()[0]
    assert count == 0


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
    assert stats.average_top_score == pytest.approx(0.85)
