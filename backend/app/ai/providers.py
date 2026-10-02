from langchain_core.embeddings import DeterministicFakeEmbedding, Embeddings
from langchain_core.language_models import BaseChatModel, FakeListChatModel

from app.config import Settings

EMBEDDING_DIM = 384  # dimension of paraphrase-multilingual-MiniLM-L12-v2
FAKE_ANSWER = "According to the document, the notice period is three months (p. 1)."


def build_embeddings(settings: Settings) -> Embeddings:
    """Return the embedding model that turns text into vectors."""
    if settings.ai_provider == "fake":
        return DeterministicFakeEmbedding(size=EMBEDDING_DIM)
    from langchain_huggingface import HuggingFaceEmbeddings  # heavy import: only when needed

    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        encode_kwargs={"normalize_embeddings": True},  # unit-length vectors → cosine works best
    )


def build_llm(settings: Settings) -> BaseChatModel:
    """Return the chat model that writes answers."""
    if settings.ai_provider == "fake":
        return FakeListChatModel(responses=[FAKE_ANSWER])
    if not settings.google_api_key:
        # Fail at startup with a fix, instead of the SDK's long validation traceback.
        raise ValueError(
            "GOOGLE_API_KEY is not set. Add it to backend/.env, "
            "or set AI_PROVIDER=fake to run without real answers."
        )
    from langchain_google_genai import ChatGoogleGenerativeAI

    thinking = (
        {}
        if settings.llm_thinking_budget is None
        else {"thinking_budget": settings.llm_thinking_budget}
    )
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0,  # deterministic, factual answers (lite models use fixed sampling)
        max_output_tokens=1024,
        **thinking,
    )
