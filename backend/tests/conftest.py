from pathlib import Path

import pytest

from app.config import Settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def isolated_settings_env(monkeypatch) -> None:
    """Hide any DocuMind settings from the shell (e.g. CI's AI_PROVIDER=fake).

    Tests then see the code's defaults unless they set a variable explicitly.
    """
    for field in Settings.model_fields:
        monkeypatch.delenv(field.upper(), raising=False)


@pytest.fixture
def sample_pdf() -> Path:
    return FIXTURES_DIR / "sample_contract.pdf"


@pytest.fixture
def empty_pdf() -> Path:
    return FIXTURES_DIR / "empty.pdf"
