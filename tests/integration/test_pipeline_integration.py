# tests/integration/test_pipeline_integration.py


import json

import pytest

from textfsm_ai.core.dotdict import DotDict
from textfsm_ai.delivery.controller.controller import DeliveryController
from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.models import model as MODEL

SAMPLE = """
Interface  Status  Protocol
Gi0/1      up      up
Gi0/2      down    down
"""


@pytest.fixture(scope="module")
def delivery_controller(deepseek_key) -> DeliveryController:
    # Use a real API key in CI or a fake/mock provider in tests
    api_key = deepseek_key
    model = MODEL.deepseek.default
    return DeliveryController(provider_name="deepseek", api_key=api_key, model=model)


def assert_contains(output: str, items: list[str]):
    """Assert each item appears in output."""
    for item in items:
        assert item in output, f"Missing: {item}\nOutput:\n{output}"


def assert_keys(required: list[str], mapping: dict):
    if not isinstance(mapping, dict):
        raise TypeError(f"Expected dict, got {type(mapping)}")

    missing = [key for key in required if key not in mapping]
    if missing:
        raise AssertionError(f"Missing keys: {missing}\nMapping:\n{mapping}")


# ---------------------------------------------------------------------------
# DEFAULT MODE
# ---------------------------------------------------------------------------


def test_default_mode_output_as_plain(delivery_controller: DeliveryController):
    mode = "default"

    pkg = delivery_controller.run(SAMPLE, mode=mode)

    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    expected = [
        "==== Output ====",
        "++ Raw Template ++",
        "Value ",
        "\n\nStart\n",
        "++ END Raw Template ++",
        "++ Template ++",
        "Value ",
        "\n\nStart\n",
        "++ END Template ++",
        "++ Readable DSL ++",
        "state Start:",
        "++ END Readable DSL ++",
        "++ Recognizers ++",
        "++ END Recognizers ++",
        "==== END Output ====",
    ]

    assert_contains(pkg.output, expected)


def test_default_mode_output_as_json(delivery_controller: DeliveryController):
    mode = "default"
    pkg = delivery_controller.run(SAMPLE, mode=mode, as_json=True)

    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    node = DotDict(json.loads(pkg.output))
    keys = ["output", "status"]
    assert_keys(keys, node)

    assert node.status.state == "render-recognizer-patterns"

    keys = ["raw_template", "readable_dsl", "recognizers", "template"]
    assert_keys(keys, node.output)

    output_node = node.output
    assert "Value " in output_node.raw_template
    assert "\n\nStart\n" in output_node.raw_template

    assert "Value " in output_node.template
    assert "\n\nStart\n" in output_node.template

    assert "state Start:" in output_node.readable_dsl
    assert "\n  start() " in output_node.readable_dsl


# ---------------------------------------------------------------------------
# QUIET MODE
# ---------------------------------------------------------------------------


def test_quiet_mode_output_as_plain(delivery_controller: DeliveryController):
    mode = "quiet"
    pkg = delivery_controller.run(SAMPLE, mode=mode)

    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    expected = [
        "Value ",
        "\n\nStart\n",
    ]

    assert_contains(pkg.output, expected)


def test_quiet_mode_output_as_json(delivery_controller: DeliveryController):
    mode = "quiet"
    pkg = delivery_controller.run(SAMPLE, mode=mode, as_json=True)

    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    node = DotDict(json.loads(pkg.output))
    keys = ["status", "template"]
    assert_keys(keys, node)

    assert node.status.state == "render-recognizer-patterns"

    template = node.template
    assert "Value " in template
    assert "\n\nStart\n" in template


# ---------------------------------------------------------------------------
# INFO MODE
# ---------------------------------------------------------------------------


def test_info_mode_output_as_plain(delivery_controller: DeliveryController):
    mode = "info"
    pkg = delivery_controller.run(SAMPLE, mode=mode)

    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    expected = [
        "==== Info ====",
        "Status : ",
        "==== END Info ====",
        "==== Versions ====",
        "Python     :",
        "TextFSM    :",
        "TextFSM-AI :",
        "==== END Versions ====",
        "==== LLM Info ====",
        "API Key     :",
        "Provider    :",
        "Model       :",
        "==== END LLM Info ====",
        "==== LLM Usage ====",
        "Input Tokens       :",
        "Output Tokens      :",
        "Total Tokens       :",
        "==== END LLM Usage ====",
        "==== LLM Structured Response ====",
        "++ Template ++",
        "Value ",
        "\n\nStart\n",
        "++ END Template ++",
        "++ Records ++",
        "++ END Records ++",
        "++ Variables ++",
        "++ END Variables ++",
        "++ Handling ++",
        "++ END Handling ++",
        "==== END LLM Structured Response ====",
        "==== Output ====",
        "++ Raw Template ++",
        "Value ",
        "\n\nStart\n",
        "++ END Raw Template ++",
        "++ Template ++",
        "Value ",
        "\n\nStart\n",
        "++ END Template ++",
        "++ Readable DSL ++",
        "state Start:",
        "\n  start() ",
        "++ END Readable DSL ++",
        "++ Recognizers ++",
        "++ END Recognizers ++",
        "==== END Output ====",
    ]

    assert_contains(pkg.output, expected)


def test_info_mode_output_as_json(delivery_controller: DeliveryController):
    mode = "info"
    pkg = delivery_controller.run(SAMPLE, mode=mode, as_json=True)
    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    node = DotDict(json.loads(pkg.output))
    keys = [
        "llm_info",
        "llm_structured_response",
        "output",
        "status",
        "usage",
        "version",
    ]
    assert_keys(keys, node)

    assert node.status.state == "render-recognizer-patterns"

    keys = ["python_version", "textfsm_version", "textfsm_ai_version"]
    assert_keys(keys, node.version)

    keys = ["api_key", "api_version", "endpoint", "model", "provider_name"]
    assert_keys(keys, node.llm_info)

    keys = ["handling", "records", "template", "variables"]
    assert_keys(keys, node.llm_structured_response)

    keys = [
        "currency",
        "estimated_cost",
        "input_per_million",
        "input_tokens",
        "llm_duration_ms",
        "output_per_million",
        "output_tokens",
        "total_tokens",
    ]
    assert_keys(keys, node.usage)

    keys = ["raw_template", "readable_dsl", "recognizers", "template"]
    assert_contains(keys, node.output)


# ---------------------------------------------------------------------------
# DEBUG MODE
# ---------------------------------------------------------------------------


def test_debug_mode_output_as_plain(delivery_controller: DeliveryController):
    mode = "debug"
    pkg = delivery_controller.run(SAMPLE, mode=mode)

    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    expected = [
        "==== Debug ====",
        "==== END Debug ====",
        "==== Versions ====",
        "==== END Versions ====",
        "==== LLM Info ====",
        "==== END LLM Info ====",
        "==== LLM Response ====",
        "==== END LLM Response ====",
        "==== LLM Usage ====",
        "==== END LLM Usage ====",
        "++ Generation Pipeline ++",
        "++ END Generation Pipeline ++",
        "++ DSL Pipeline ++",
        "++ END DSL Pipeline ++",
    ]

    assert_contains(pkg.output, expected)


def test_debug_mode_output_as_json(delivery_controller: DeliveryController):
    mode = "debug"
    pkg = delivery_controller.run(SAMPLE, mode=mode, as_json=True)
    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.passed is True

    node = DotDict(json.loads(pkg.output))

    keys = [
        "dsl_pipeline",
        "duration_ms",
        "generation_pipeline",
        "llm_info",
        "llm_response",
        "status",
        "usage",
        "version",
    ]
    assert_keys(keys, node)

    assert node.status.state == "render-recognizer-patterns"

    keys = ["python_version", "textfsm_version", "textfsm_ai_version"]
    assert_keys(keys, node.version)

    keys = ["api_key", "api_version", "endpoint", "model", "provider_name"]
    assert_keys(keys, node.llm_info)

    keys = ["duration_ms", "max_retries", "raw"]
    assert_keys(keys, node.llm_response)

    keys = [
        "currency",
        "estimated_cost",
        "input_per_million",
        "input_tokens",
        "llm_duration_ms",
        "output_per_million",
        "output_tokens",
        "total_tokens",
    ]
    assert_keys(keys, node.usage)

    keys = [
        "attempts",
        "last_stage",
        "max_retries",
        "model",
        "ready",
        "reason",
        "sample",
        "stages",
    ]
    assert_contains(keys, node.generation_pipeline)

    keys = ["dsl", "ready", "reason"]
    assert_contains(keys, node.dsl_pipeline)
