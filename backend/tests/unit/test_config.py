from pathlib import Path

from app.config import BACKEND_DIR, Settings, get_settings


def test_env_file_is_anchored_to_backend_dir() -> None:
    env_file = Settings.model_config["env_file"]

    assert env_file == BACKEND_DIR / ".env"
    assert (BACKEND_DIR / "app" / "config.py").is_file()


def test_env_file_is_read(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TOP_K=9\n", encoding="utf-8")

    assert Settings(_env_file=env_file).top_k == 9


def test_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.ai_provider == "real"
    assert settings.google_api_key == ""
    assert settings.llm_model == "gemini-3.8-flash"
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
