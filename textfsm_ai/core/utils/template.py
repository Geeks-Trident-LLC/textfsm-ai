# textfsm_ai/core/utils/template.py

from io import StringIO
from typing import Dict, List

from textfsm import TextFSM

from ..models import ValidationResult


def _create_parser(template: str) -> TextFSM:
    """Create a TextFSM parser from a template string."""
    return TextFSM(StringIO(template))


def parse_to_lists(template: str, sample: str) -> List[List[str]]:
    """Parse `sample` with a TextFSM `template`, returning rows of raw values."""
    parser = _create_parser(template)
    return parser.ParseText(sample)


def parse_to_dicts(template: str, sample: str) -> List[Dict[str, str]]:
    """Parse `sample` with a TextFSM `template`, returning rows as dicts."""
    parser = _create_parser(template)
    return parser.ParseTextToDicts(sample)


def validate_template(template: str) -> ValidationResult:
    """Validate that a TextFSM template is non-empty and syntactically valid."""

    text = template.strip()
    if not text:
        return ValidationResult(
            data=template,
            reason="template_empty",
            ready=False,
        )

    try:
        _create_parser(text)
        return ValidationResult(data=template, ready=True)
    except Exception as ex:
        return ValidationResult(
            data=template,
            reason=f"template_syntax_error: {type(ex).__name__}: {ex}",
            ready=False,
        )
