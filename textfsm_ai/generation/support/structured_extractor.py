# textfsm_ai/generation/engine/structured_extractor.py

import json
import re

from textfsm_ai.generation.core.models import StructuredResponse

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def _strip_code_fence(raw: str) -> str:
    """
    Removes ```json ... ``` or ``` ... ``` fences if present.
    """
    # Remove leading/trailing whitespace
    text = raw.strip()

    # Regex to match fenced code blocks
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    return text


# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------


def extract(response) -> StructuredResponse:
    if not response.ready:
        return StructuredResponse(
            template="",
            records=[],
            variables={},
            handling=[],
            response=response,
            reason=response.reason,
            ready=False,
        )

    cleaned = _strip_code_fence(response.content or "")

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as ex:
        return StructuredResponse(
            template="",
            records=[],
            variables={},
            handling=[],
            response=response,
            reason=f"{type(ex).__name__}: {ex}",
            ready=False,
        )

    # Extract fields with type validation
    template = data.get("template", "")

    records = data.get("records")
    if not isinstance(records, list):
        records = []

    variables = data.get("variables")
    if not isinstance(variables, dict):
        variables = {}

    handling = data.get("handling")
    if not isinstance(handling, list):
        handling = []

    # Determine readiness
    ready = bool(template)

    # Determine reason
    if not ready:
        reason = "Template missing or empty in JSON output"
    elif not records:
        reason = "Empty parsed records"
    else:
        reason = ""

    return StructuredResponse(
        template=template,
        records=records,
        variables=variables,
        handling=handling,
        response=response,
        reason=reason,
        ready=ready,
    )
