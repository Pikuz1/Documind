from pathlib import Path

from app.config import Settings, get_settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.ai_provider == "real"
    assert settings.anthropic_api_key == ""
    assert settings.llm_model == "claude-haiku-4-5"
    assert settings.embedding_model == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    assert settings.data_dir == Path("data")
    assert settings.chunk_size == 800
    assert settings.chunk_overlap == 120
    assert settings.top_k == 4
    assert settings.min_relevance_score == 0.3
    assert settings.max_upload_mb == 10


def test_env_vars_override_defaults(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "fake")
    monkeypatch.setenv("TOP_K", "6")
    monkeypatch.setenv("CHUNK_SIZE", "500")

    settings = Settings(_env_file=None)

    assert settings.ai_provider == "fake"
    assert settings.top_k == 6
    assert settings.chunk_size == 500


def test_derived_paths_come_from_data_dir() -> None:
    settings = Settings(_env_file=None, data_dir=Path("mydata"))

    assert settings.chroma_dir == Path("mydata/chroma")
    assert settings.sqlite_path == Path("mydata/documind.db")
    assert settings.upload_dir == Path("mydata/uploads")


def test_get_settings_is_cached_singleton() -> None:
    assert get_settings() is get_settings()
