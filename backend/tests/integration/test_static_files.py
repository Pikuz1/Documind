from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def built_frontend(tmp_path: Path) -> Path:
    static = tmp_path / "static"
    (static / "assets").mkdir(parents=True)
    (static / "index.html").write_text("<title>DocuMind</title>", encoding="utf-8")
    (static / "assets" / "app.js").write_text("console.log('ui')", encoding="utf-8")
    return static


def client_for(static_dir: Path | None) -> TestClient:
    # No `with`: the lifespan (which builds the AI services) isn't needed for these checks.
    return TestClient(create_app(Settings(_env_file=None, static_dir=static_dir)))


def test_serves_index_html_at_root(built_frontend: Path) -> None:
    response = client_for(built_frontend).get("/")

    assert response.status_code == 200
    assert "<title>DocuMind</title>" in response.text


def test_serves_built_assets(built_frontend: Path) -> None:
    response = client_for(built_frontend).get("/assets/app.js")

    assert response.status_code == 200
    assert response.text == "console.log('ui')"


def test_api_routes_still_win_over_the_static_mount(built_frontend: Path) -> None:
    assert client_for(built_frontend).get("/api/health").json() == {"status": "ok"}


def test_no_static_dir_means_api_only() -> None:
    assert client_for(None).get("/").status_code == 404


def test_missing_static_dir_is_ignored(tmp_path: Path) -> None:
    assert client_for(tmp_path / "not-built-yet").get("/").status_code == 404
