from .errors import ProviderNotFoundError
from .types import OrchestratorRequest, OrchestratorResponse


class Orchestrator:
    """
    High-level AI orchestration engine.
    Responsible for:
    - routing requests to providers
    - applying pre/post-processing
    - enforcing config rules
    - returning normalized responses
    """

    def __init__(self, providers, config):
        self.providers = providers
        self.config = config

    def _select_provider(self, request: OrchestratorRequest):
        # naive first version: match by model prefix
        for provider in self.providers:
            if provider.supports(request.model):
                return provider
        raise ProviderNotFoundError(f"No provider found for model: {request.model}")


def run(self, request: OrchestratorRequest) -> OrchestratorResponse:
    provider = self._select_provider(request)
    response = provider.generate(
        prompt=request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    return OrchestratorResponse(
        provider=provider.name,
        model=request.model,
        content=response["content"],
        raw=response,
    )
