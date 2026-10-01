from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_pdf() -> Path:
    return FIXTURES_DIR / "sample_contract.pdf"


@pytest.fixture
def empty_pdf() -> Path:
    return FIXTURES_DIR / "empty.pdf"
