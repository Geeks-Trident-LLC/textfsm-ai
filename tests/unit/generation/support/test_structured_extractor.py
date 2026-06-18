# tests/unit/generation/support/test_structured_extractor.py

from textfsm_ai.generation.core.models import StructuredResponse
from textfsm_ai.generation.support import structured_extractor


# ---------------------------------------------------------
# Helper mock response
# ---------------------------------------------------------
class MockResponse:
    def __init__(self, content, ready=True, reason=""):
        self.content = content
        self.ready = ready
        self.reason = reason


# ---------------------------------------------------------
# _strip_code_fence
# ---------------------------------------------------------
def test_strip_code_fence_json_block():
    raw = """```json
    {"a": 1}
    ```"""
    out = structured_extractor._strip_code_fence(raw)
    assert out == '{"a": 1}'


def test_strip_code_fence_plain_text():
    raw = '{"a": 1}'
    out = structured_extractor._strip_code_fence(raw)
    assert out == raw


def test_strip_code_fence_non_json_fence():
    raw = """```
    {"a": 1}
    ```"""
    out = structured_extractor._strip_code_fence(raw)
    assert out == '{"a": 1}'


# ---------------------------------------------------------
# extract() — response.ready = False
# ---------------------------------------------------------
def test_extract_not_ready():
    resp = MockResponse(content="", ready=False, reason="boom")
    result = structured_extractor.extract(resp)

    assert isinstance(result, StructuredResponse)
    assert result.ready is False
    assert result.template == ""
    assert result.records == []
    assert result.variables == {}
    assert result.handling == []
    assert result.reason == "boom"
    assert result.response is resp


# ---------------------------------------------------------
# extract() — invalid JSON
# ---------------------------------------------------------
def test_extract_invalid_json():
    resp = MockResponse(content="not json", ready=True)
    result = structured_extractor.extract(resp)

    assert result.ready is False
    assert "JSONDecodeError" in result.reason
    assert result.template == ""
    assert result.records == []
    assert result.variables == {}
    assert result.handling == []


# ---------------------------------------------------------
# extract() — valid JSON, full fields
# ---------------------------------------------------------
def test_extract_valid_json():
    data = {
        "template": "Value iface (\\S+)\nStart\n  ^interface ${iface} -> Record",
        "records": [{"iface": "Gi0/1"}],
        "variables": {"iface": "interface name"},
        "handling": ["parsed interface"],
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.ready is True
    assert result.template.startswith("Value iface")
    assert result.records == [{"iface": "Gi0/1"}]
    assert result.variables == {"iface": "interface name"}
    assert result.handling == ["parsed interface"]
    assert result.reason == ""


# ---------------------------------------------------------
# extract() — missing template
# ---------------------------------------------------------
def test_extract_missing_template():
    data = {
        "records": [{"iface": "Gi0/1"}],
        "variables": {},
        "handling": [],
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.ready is False
    assert "Template missing" in result.reason
    assert result.template == ""


# ---------------------------------------------------------
# extract() — empty template
# ---------------------------------------------------------
def test_extract_empty_template():
    data = {
        "template": "",
        "records": [{"iface": "Gi0/1"}],
        "variables": {},
        "handling": [],
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.ready is False
    assert "Template missing" in result.reason


# ---------------------------------------------------------
# extract() — records not a list
# ---------------------------------------------------------
def test_extract_records_wrong_type():
    data = {
        "template": "Value iface (\\S+)",
        "records": "not a list",
        "variables": {},
        "handling": [],
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.records == []


# ---------------------------------------------------------
# extract() — variables not a dict
# ---------------------------------------------------------
def test_extract_variables_wrong_type():
    data = {
        "template": "Value iface (\\S+)",
        "records": [],
        "variables": "oops",
        "handling": [],
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.variables == {}


# ---------------------------------------------------------
# extract() — handling not a list
# ---------------------------------------------------------
def test_extract_handling_wrong_type():
    data = {
        "template": "Value iface (\\S+)",
        "records": [],
        "variables": {},
        "handling": "oops",
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.handling == []


# ---------------------------------------------------------
# extract() — template ok but records empty
# ---------------------------------------------------------
def test_extract_empty_records_reason():
    data = {
        "template": "Value iface (\\S+)",
        "records": [],
        "variables": {},
        "handling": [],
    }
    resp = MockResponse(content=str(data).replace("'", '"'), ready=True)

    result = structured_extractor.extract(resp)

    assert result.ready is True  # template exists
    assert result.reason == "Empty parsed records"
