from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Anchored to backend/ so the app finds .env no matter which directory it's started from.
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    ai_provider: Literal["real", "fake"] = "real"
    google_api_key: str = ""
    llm_model: str = "gemini-3.8-flash"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    data_dir: Path = Path("data")
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 4
    min_relevance_score: float = 0.3
    max_upload_mb: int = 10
    static_dir: Path | None = None  # built frontend to serve at "/" (set in the Docker image)

    @field_validator("data_dir", "static_dir")
    @classmethod
    def _anchor_relative_paths(cls, value: Path | None) -> Path | None:
        # Same reason as env_file: relative paths must not depend on the working directory.
        if value is None or value.is_absolute():
            return value
        return BACKEND_DIR / value

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def sqlite_path(self) -> Path:
        return self.data_dir / "documind.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
