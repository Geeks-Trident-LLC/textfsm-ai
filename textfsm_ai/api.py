# textfsm_ai/api.py

from __future__ import annotations

from textfsm_ai.orchestrator.factory import create_orchestrator_from_config
from textfsm_ai.orchestrator.types import OrchestratorRequest
from textfsm_ai.providers.config import load_config_from_env, load_config_from_file


async def ask_ai(
    prompt: str,
    model: str,
    *,
    config_path: str | None = None,
    **kwargs,
):
    if config_path:
        cfg = load_config_from_file(config_path)
    else:
        cfg = load_config_from_env()

    orch = create_orchestrator_from_config(cfg)

    req = OrchestratorRequest(
        model=model,
        prompt=prompt,
        **kwargs,
    )

    return await orch.run(req)
