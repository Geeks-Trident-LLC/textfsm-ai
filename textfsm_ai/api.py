# textfsm_ai/api.py

from __future__ import annotations

from textfsm_ai.orchestrator.factory import create_orchestrator_from_config
from textfsm_ai.orchestrator.types import OrchestratorRequest
from textfsm_ai.providers.config import load_config_from_env, load_config_from_file


def ask_ai(
    prompt: str,
    model: str,
    *,
    config_path: str | None = None,
    **kwargs,
):
    """
    High-level API for sending a prompt through the orchestrator.

    Parameters
    ----------
    prompt : str
        The user prompt.
    model : str
        Model name with prefix, e.g. "openai/gpt-4o-mini".
    config_path : str | None
        Optional path to a YAML config file. If omitted,
        environment variables are used.
    kwargs : dict
        Additional fields passed into OrchestratorRequest
        (temperature, max_tokens, etc.)

    Returns
    -------
    OrchestratorResponse
    """
    # Load config (YAML or env)
    if config_path:
        cfg = load_config_from_file(config_path)
    else:
        cfg = load_config_from_env()

    # Build orchestrator
    orch = create_orchestrator_from_config(cfg)

    # Build request
    req = OrchestratorRequest(
        model=model,
        prompt=prompt,
        **kwargs,
    )

    # Execute
    return orch.run(req)
