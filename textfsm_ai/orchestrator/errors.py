# textfsm_ai/orchestrator/errors.py


class OrchestratorError(Exception):
    """Base class for orchestrator errors."""

    pass


class ProviderNotFoundError(OrchestratorError):
    """Raised when no provider can satisfy the request."""

    pass


class ProviderError(OrchestratorError):
    """Raised when a provider call fails."""

    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


class ProviderAuthError(ProviderError):
    pass


class ProviderModelNotSupportedError(ProviderError):
    pass
