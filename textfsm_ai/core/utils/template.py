# textfsm_ai/core/utils/template.py

from io import StringIO
from typing import Dict, List

from textfsm import TextFSM


def _create_parser(template: str) -> TextFSM:
    """Create a TextFSM parser from a template string."""
    return TextFSM(StringIO(template))


def parse_to_lists(template: str, sample: str) -> List[List[str]]:
    parser = _create_parser(template)
    return parser.ParseText(sample)


def parse_to_dicts(template: str, sample: str) -> List[Dict[str, str]]:
    parser = _create_parser(template)
    return parser.ParseTextToDicts(sample)
