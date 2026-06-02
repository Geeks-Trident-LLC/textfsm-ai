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
