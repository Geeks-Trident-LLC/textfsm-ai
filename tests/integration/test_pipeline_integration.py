# tests/integration/test_pipeline_integration.py


import pytest

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


@pytest.mark.parametrize(
    "mode",
    [
        # "quiet",
        "default",
        # "info",
        # "debug"
    ],
)
def test_pipeline_runs_without_error(
    delivery_controller: DeliveryController, mode: str
):
    pkg = delivery_controller.run(SAMPLE, mode=mode)

    # basic invariants
    assert pkg.mode == DeliveryMode.from_str(mode)
    assert pkg.template.canonical_template.strip()
    assert pkg.template.human_template_dsl.strip()
    assert pkg.status.state

    # mode-specific expectations
    if pkg.mode >= DeliveryMode.DEFAULT:
        assert pkg.general is not None
        assert pkg.explanation is not None

    if pkg.mode >= DeliveryMode.INFO:
        # usage may be None if provider doesn't return tokens,
        # but if present it must be sane
        if pkg.usage is not None:
            assert pkg.usage.input_tokens >= 0
            assert pkg.usage.total_tokens >= pkg.usage.input_tokens

    if pkg.mode == DeliveryMode.DEBUG:
        assert pkg.debug is not None


# def test_pipeline_cli_formatting(delivery_controller: DeliveryController):
#     pkg = delivery_controller.run(SAMPLE, mode="debug")
#     cli_output = format_delivery_for_cli(pkg)

#     assert "=== Template ===" in cli_output
#     assert "=== Status ===" in cli_output
#     assert "=== Debug ===" in cli_output
#     assert pkg.template.canonical_template.splitlines()[0] in cli_output


# def test_pipeline_json_formatting(delivery_controller: DeliveryController):
#     pkg = delivery_controller.run(SAMPLE, mode="info")
#     data = delivery_to_json_dict(pkg)

#     # top-level keys
#     assert "mode" in data
#     assert "template" in data
#     assert "status" in data

#     # mode-aware: info should include usage if available
#     if "usage" in data:
#         assert data["usage"]["input_tokens"] >= 0

#     # JSON-serializable
#     json_str = json.dumps(data)
#     assert isinstance(json_str, str)


# def test_pipeline_duration_is_reasonable(delivery_controller: DeliveryController):
#     start = time.perf_counter()
#     pkg = delivery_controller.run(SAMPLE, mode="info")
#     elapsed_ms = (time.perf_counter() - start) * 1000

#     # if duration_ms is present, it should be in the same ballpark
#     if pkg.usage and pkg.usage.duration_ms is not None:
#         assert 0 <= pkg.usage.duration_ms <= elapsed_ms * 5  # generous bound
