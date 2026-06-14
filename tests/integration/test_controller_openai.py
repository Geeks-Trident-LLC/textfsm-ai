# tests/integration/test_controller_openai.py

from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.models import model as MODEL


def test_real(openai_key):
    controller = GenerationController(api_key=openai_key, model=MODEL.openai.default)
    result = controller.run("interface GigabitEthernet0/1")

    # Must return a GenerationResult
    assert hasattr(result, "is_success")
    assert hasattr(result, "template")
    assert hasattr(result, "status")
    assert hasattr(result, "structured")

    # Must be successful (valid_raw or cleaned)
    assert result.is_success(), f"Generation failed with status={result.status}"

    # Template must not be empty
    assert isinstance(result.template, str)
    assert result.template.strip()
