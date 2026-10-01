class DocumentNotFoundError(Exception):
    pass


class EmptyDocumentError(Exception):
    pass


class LLMUnavailableError(Exception):
    """The chat model failed (quota, network, provider outage), not the user's request."""
