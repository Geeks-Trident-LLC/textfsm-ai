# tests/unit/generation/support/test_generator.py


from textfsm_ai.generation.core.models import (
    GenerationResult,
)
from textfsm_ai.generation.support import generator


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
class DummyStructured:
    """Simple mock for StructuredResponse."""

    def __init__(self, template, records, ready=True, reason=""):
        self.template = template
        self.records = records
        self.ready = ready
        self.reason = reason
        self.response = None  # not used by generator


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
def test_generate_not_ready():
    structured = DummyStructured(
        template="ignored",
        records=[["x"]],
        ready=False,
        reason="parse error",
    )

    result = generator.generate(structured)

    assert isinstance(result, GenerationResult)
    assert result.ready is False
    assert result.template == ""
    assert result.records == []
    assert result.reason == "parse error"
    assert result.metadata is structured


def test_generate_ready_valid_template():
    template = """
Value iface (\\S+)

Start
  ^interface ${iface} -> Record
""".strip()
    structured = DummyStructured(
        template=template,
        records=[["Gi0/1"]],
        ready=True,
    )

    result = generator.generate(structured)

    assert isinstance(result, GenerationResult)
    assert result.ready is True
    assert result.template == template
    assert result.records == [["Gi0/1"]]
    assert result.metadata is structured
    assert result.reason == ""  # validator.reason should be empty for valid template


def test_generate_ready_invalid_template():
    # Missing parentheses in Value definition → invalid
    template = """
Value iface \\S+

Start
  ^interface ${iface} -> Record
"""
    structured = DummyStructured(
        template=template,
        records=[["Gi0/1"]],
        ready=True,
    )

    result = generator.generate(structured)

    assert isinstance(result, GenerationResult)
    assert result.ready is False
    assert result.template == template
    assert result.records == [["Gi0/1"]]
    assert result.metadata is structured
    assert "FSMTemplateError" in result.reason or "Error" in result.reason
