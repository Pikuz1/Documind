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
    assert settings.llm_model == "gemini-3.5-flash-lite"
    assert settings.llm_thinking_budget is None
    assert settings.embedding_model == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    assert settings.data_dir == BACKEND_DIR / "data"
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


def test_relative_data_dir_is_anchored_to_backend_dir() -> None:
    settings = Settings(_env_file=None, data_dir=Path("mydata"))

    assert settings.data_dir == BACKEND_DIR / "mydata"


def test_absolute_data_dir_is_kept(tmp_path) -> None:
    assert Settings(_env_file=None, data_dir=tmp_path).data_dir == tmp_path


def test_derived_paths_come_from_data_dir(tmp_path) -> None:
    settings = Settings(_env_file=None, data_dir=tmp_path)

    assert settings.chroma_dir == tmp_path / "chroma"
    assert settings.sqlite_path == tmp_path / "documind.db"


def test_get_settings_is_cached_singleton() -> None:
    assert get_settings() is get_settings()


def test_static_dir_defaults_to_none() -> None:
    assert Settings(_env_file=None).static_dir is None


def test_relative_static_dir_is_anchored_and_absolute_kept(tmp_path) -> None:
    assert Settings(_env_file=None, static_dir=Path("ui")).static_dir == BACKEND_DIR / "ui"
    assert Settings(_env_file=None, static_dir=tmp_path).static_dir == tmp_path
