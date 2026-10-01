from langchain_core.language_models import FakeListChatModel


class ExplodingLLM(FakeListChatModel):
    """Fails the test if the chain ever reaches the model."""

    def invoke(self, *args, **kwargs):
        raise AssertionError("LLM should not be called when nothing is relevant")


class QuotaExceededLLM(FakeListChatModel):
    """Simulates a provider error such as Gemini's 429 RESOURCE_EXHAUSTED."""

    def invoke(self, *args, **kwargs):
        raise RuntimeError("429 RESOURCE_EXHAUSTED")
