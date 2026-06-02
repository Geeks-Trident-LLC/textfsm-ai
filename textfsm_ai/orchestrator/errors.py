class OrchestratorError(Exception):
    """Base class for orchestrator errors."""

    pass


class ProviderNotFoundError(OrchestratorError):
    """Raised when no provider can satisfy the request."""

    pass
