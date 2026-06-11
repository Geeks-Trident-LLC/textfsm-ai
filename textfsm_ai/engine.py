"""
High-level TextFSM Template Generation Engine.

This module exposes a single entry point:

    generate_template(api_key, model, sample)

It orchestrates the full generation pipeline:
  - one-pass
  - two-pass
  - fallback
  - cleaning + validation
  - structured extraction
  - final GenerationResult
"""

from textfsm_ai.generation.controller import Controller
from textfsm_ai.generation.generator import GenerationResult


def generate_template(api_key: str, model: str, sample: str) -> GenerationResult:
    """
    Runs the full template-generation pipeline on a single sample.

    Parameters
    ----------
    api_key : str
        Provider API key.
    model : str
        Model name (used to resolve provider).
    sample : str
        Raw CLI text to generate a TextFSM template for.

    Returns
    -------
    GenerationResult
        Contains:
          - final template (raw or cleaned)
          - status ("valid_raw", "cleaned", "invalid")
          - structured extraction (JSON + llm_run_result)
    """
    controller = Controller(api_key=api_key, model=model)
    return controller.run(sample)
