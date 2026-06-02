# e.g. textfsm_ai/orchestrator/default_hooks.py
from .types import OrchestratorRequest, OrchestratorResponse


def trim_prompt_hook(request: OrchestratorRequest) -> OrchestratorRequest:
    request.prompt = request.prompt.strip()
    return request


def strip_response_hook(response: OrchestratorResponse) -> OrchestratorResponse:
    response.content = response.content.strip()
    return response
