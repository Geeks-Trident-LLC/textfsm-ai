# tests/integration/test_controller_anthropic.py

from textfsm_ai.core.utils.template import parse_to_lists
from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.models import model as MODEL


def test_real(anthropic_key):
    controller = GenerationController(
        api_key=anthropic_key, model=MODEL.anthropic.default, max_retries=2
    )
    result = controller.run("interface GigabitEthernet0/1")

    assert result.ready

    for row in parse_to_lists(result.last_stage.template, result.sample):
        assert "GigabitEthernet0/1" in row
