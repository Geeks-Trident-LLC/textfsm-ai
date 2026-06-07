# tests/integration/test_controller_deepseek.py

from textfsm_ai.generation.controller import Controller
from textfsm_ai.models import model as MODEL


def test_real(deepseek_key):
    controller = Controller(api_key=deepseek_key, model=MODEL.deepseek.default)
    result = controller.run("interface GigabitEthernet0/1")

    # Must return a GenerationResult
    assert hasattr(result, "is_success")
    assert hasattr(result, "template")

    # Must be successful (valid_raw or cleaned)
    assert result.is_success(), f"Generation failed with status={result.status}"

    # Template must not be empty
    assert isinstance(result.template, str)
    assert result.template.strip()
