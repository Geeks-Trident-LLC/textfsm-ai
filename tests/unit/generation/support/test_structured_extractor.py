# tests/unit/generation/support/test_structured_extractor.py

import json

from textfsm_ai.generation.core.models import LLMRunResult, StructuredResult
from textfsm_ai.generation.support.structured_extractor import (
    _extract_json_block,
    _strip_code_fence,
    parse_from_response,
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def make_llm_result():
    return LLMRunResult(
        provider="deepseek",
        model="deepseek-chat",
        sample="sample text",
        prompt="prompt text",
        response="response text",
    )


# ------------------------------------------------------------
# _strip_code_fence tests
# ------------------------------------------------------------


def test_strip_code_fence_json_block():
    raw = """```json
{
  "textfsm_template": "TEMPLATE"
}
```"""
    cleaned = _strip_code_fence(raw)
    assert cleaned.strip().startswith("{")
    assert cleaned.strip().endswith("}")


def test_strip_code_fence_plain_text():
    raw = "no fences here"
    cleaned = _strip_code_fence(raw)
    assert cleaned == raw


def test_strip_code_fence_non_json_fence():
    raw = """```
{
  "textfsm_template": "TEMPLATE"
}
```"""
    cleaned = _strip_code_fence(raw)
    assert cleaned.strip().startswith("{")
    assert cleaned.strip().endswith("}")


# ------------------------------------------------------------
# _extract_json_block tests
# ------------------------------------------------------------


def test_extract_json_block_valid():
    raw = 'prefix {"a": 1} suffix'
    json_str = _extract_json_block(raw)
    assert json.loads(json_str) == {"a": 1}


def test_extract_json_block_no_json():
    raw = "just text"
    json_str = _extract_json_block(raw)
    data = json.loads(json_str)
    assert data == {"textfsm_template": "just text"}


def test_extract_json_block_malformed_json():
    raw = "{invalid json"
    json_str = _extract_json_block(raw)
    # Should wrap raw as template-only
    data = json.loads(json_str)
    assert data == {"textfsm_template": raw}


# ------------------------------------------------------------
# parse_from_response tests
# ------------------------------------------------------------


def test_parse_from_response_pure_json():
    raw = json.dumps(
        {
            "textfsm_template": "TEMPLATE",
            "parsed_result": [],
            "variable_explanation": {},
            "llm_handling_template": [],
        }
    )

    llm_result = make_llm_result()
    structured = parse_from_response(raw, llm_result)

    assert isinstance(structured, StructuredResult)
    assert structured.template == "TEMPLATE"
    assert structured.data["textfsm_template"] == "TEMPLATE"
    assert structured.llm_run_result is llm_result


def test_parse_from_response_fenced_json():
    raw = """```json
{
  "textfsm_template": "TEMPLATE2",
  "parsed_result": [],
  "variable_explanation": {},
  "llm_handling_template": []
}
```"""

    llm_result = make_llm_result()
    structured = parse_from_response(raw, llm_result)

    assert structured.template == "TEMPLATE2"
    assert structured.data["textfsm_template"] == "TEMPLATE2"


def test_parse_from_response_malformed_json():
    raw = """```json
{ invalid json
```"""

    llm_result = make_llm_result()
    structured = parse_from_response(raw, llm_result)

    # After stripping code fences, this is the cleaned raw
    cleaned = "{ invalid json"

    # Fallback: template should equal cleaned version
    assert structured.template == cleaned
    assert structured.data == {"textfsm_template": cleaned}


def test_parse_from_response_no_json():
    raw = "just a template"

    llm_result = make_llm_result()
    structured = parse_from_response(raw, llm_result)

    assert structured.template == "just a template"
    assert structured.data == {"textfsm_template": "just a template"}


def test_parse_from_response_extracts_template_key():
    raw = json.dumps({"textfsm_template": "MY_TEMPLATE", "parsed_result": [{"a": 1}]})

    llm_result = make_llm_result()
    structured = parse_from_response(raw, llm_result)

    assert structured.template == "MY_TEMPLATE"
    assert structured.data["parsed_result"] == [{"a": 1}]
