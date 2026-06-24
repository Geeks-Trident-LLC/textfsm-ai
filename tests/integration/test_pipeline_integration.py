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
