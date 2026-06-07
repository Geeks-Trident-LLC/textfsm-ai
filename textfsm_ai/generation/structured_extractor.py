# textfsm_ai/generation/structured_extractor.py

import json
import re
from dataclasses import dataclass

from textfsm_ai.core.serializable import Serializable

from .extractor import LLMRunResult


@dataclass
class StructuredResult(Serializable):
    template: str  # extracted textfsm_template
    data: dict  # full parsed JSON dict
    llm_run_result: LLMRunResult

    def to_dict(self):
        return {
            "template": self.template,
            "data": self.data,
            "llm_run_result": self.llm_run_result,
        }


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

    return raw


def _extract_json_block(raw: str) -> str:
    """
    Extracts the first {...} JSON block.
    If none found, wraps raw as {"textfsm_template": raw}.
    """
    text = raw.strip()

    # Find first '{' and last '}'
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        # No JSON found → treat raw as template-only
        return json.dumps({"textfsm_template": raw})

    return text[start : end + 1]


# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------


def parse_from_response(raw: str, llm_run_result: LLMRunResult) -> StructuredResult:
    """
    Converts raw LLM output into a structured dict.
    Handles:
    - pure JSON
    - fenced ```json blocks
    - malformed JSON (fallback to template-only)
    """

    # Step 1 — strip code fences
    cleaned = _strip_code_fence(raw)

    # Step 2 — extract JSON block
    json_str = _extract_json_block(cleaned)

    # Step 3 — parse JSON safely
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # fallback: treat raw as template-only
        data = {"textfsm_template": raw}

    # Step 4 — extract template
    template = data.get("textfsm_template", "")

    return StructuredResult(
        template=template,
        data=data,
        llm_run_result=llm_run_result,
    )
