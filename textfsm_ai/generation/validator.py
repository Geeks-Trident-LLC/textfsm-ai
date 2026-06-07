# textfsm_ai/generation/validator.py

from io import StringIO

import textfsm

# -------------------------------
# Template validation
# -------------------------------


class TemplateValidator:
    """Validate TextFSM template syntax."""

    @staticmethod
    def is_valid_template(template: str) -> bool:
        if not isinstance(template, str) or not template.strip():
            return False

        # Must contain a Start state
        if "Start" not in template:
            return False

        try:
            textfsm.TextFSM(StringIO(template))
            return True
        except Exception:
            return False


def validate_template(template: str) -> bool:
    """Convenience wrapper used by controller + generator."""
    return TemplateValidator.is_valid_template(template)


# -------------------------------
# parsed_result validation
# -------------------------------


class ParsedResultValidator:
    """Validate parsed_result is a list of dictionaries."""

    @staticmethod
    def is_valid(parsed_result) -> bool:
        if not isinstance(parsed_result, list):
            return False

        return all(isinstance(item, dict) for item in parsed_result)


# -------------------------------
# ASCII-only helpers
# -------------------------------


def is_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return True
    except Exception:
        return False


# -------------------------------
# variable_explanation validation
# -------------------------------


class VariableExplanationValidator:
    """Validate variable_explanation is a dict of ASCII-only strings."""

    @staticmethod
    def is_valid(expl: dict) -> bool:
        if not isinstance(expl, dict):
            return False

        for key, value in expl.items():
            if not isinstance(key, str) or not key.strip():
                return False
            if not isinstance(value, str) or not value.strip():
                return False
            if not is_ascii(key) or not is_ascii(value):
                return False

        return True


# -------------------------------
# llm_handling_template validation
# -------------------------------


class HandlingTemplateValidator:
    """Validate llm_handling_template is a list of ASCII-only sentences."""

    @staticmethod
    def is_valid(lines) -> bool:
        if not isinstance(lines, list):
            return False

        for line in lines:
            if not isinstance(line, str) or not line.strip():
                return False
            if not is_ascii(line):
                return False

        return True
