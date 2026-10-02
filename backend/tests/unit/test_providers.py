import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models import FakeListChatModel

from app.ai.providers import FAKE_ANSWER, build_embeddings, build_llm
from app.config import Settings


def fake_settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_build_embeddings_returns_fake_in_fake_mode() -> None:
    embeddings = build_embeddings(fake_settings(ai_provider="fake"))

    assert isinstance(embeddings, DeterministicFakeEmbedding)


def test_build_embeddings_returns_real_model_with_expected_args(monkeypatch) -> None:
    captured: dict = {}

    class FakeHuggingFaceEmbeddings:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("langchain_huggingface.HuggingFaceEmbeddings", FakeHuggingFaceEmbeddings)

    settings = fake_settings(ai_provider="real", embedding_model="some/model")
    build_embeddings(settings)

    assert captured["model_name"] == "some/model"
    assert captured["encode_kwargs"] == {"normalize_embeddings": True}


def test_build_llm_returns_fake_in_fake_mode() -> None:
    llm = build_llm(fake_settings(ai_provider="fake"))

    assert isinstance(llm, FakeListChatModel)
    assert llm.responses == [FAKE_ANSWER]


def test_build_llm_returns_real_model_with_expected_args(monkeypatch) -> None:
    captured: dict = {}

    class FakeChatGoogleGenerativeAI:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", FakeChatGoogleGenerativeAI)

    settings = fake_settings(
        ai_provider="real", llm_model="gemini-3.5-flash-lite", google_api_key="test-key"
    )
    build_llm(settings)

    assert captured["model"] == "gemini-3.5-flash-lite"
    assert captured["google_api_key"] == "test-key"
    assert captured["temperature"] == 0
    assert "thinking_budget" not in captured  # lite models reject it


def test_build_llm_requires_an_api_key_in_real_mode() -> None:
    with pytest.raises(ValueError, match="GOOGLE_API_KEY is not set.*AI_PROVIDER=fake"):
        build_llm(fake_settings(ai_provider="real", google_api_key=""))


def test_build_llm_passes_thinking_budget_when_configured(monkeypatch) -> None:
    captured: dict = {}

    class FakeChatGoogleGenerativeAI:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", FakeChatGoogleGenerativeAI)

    build_llm(
        fake_settings(
            ai_provider="real",
            llm_model="gemini-3.8-flash",
            llm_thinking_budget=0,
            google_api_key="test-key",
        )
    )

    assert captured["thinking_budget"] == 0
