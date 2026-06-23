# tests/integration/test_controller_azure.py

from textfsm_ai.core.utils.template import parse_to_lists
from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.models import model as MODEL


def test_real(azure_key):
    controller = GenerationController(
        provider_name="azure",
        api_key=azure_key,
        model=MODEL.azure.default,
        max_retries=2,
    )

    gen_pipeline = controller.run("interface GigabitEthernet0/1")
    assert gen_pipeline.ready, f"Azure generation failed: {gen_pipeline.reason}"

    # Template must parse and include the interface name
    for row in parse_to_lists(gen_pipeline.last_stage.template, gen_pipeline.sample):
        assert "GigabitEthernet0/1" in row

    # Now run DSL pipeline
    controller = DSLController()
    dsl_pipeline = controller.run(gen_pipeline)

    assert dsl_pipeline.ready
    assert len(dsl_pipeline.stages) == 4

    canonicalizer_stage = dsl_pipeline.stages[0]
    machine_dsl_stage = dsl_pipeline.stages[1]
    human_dsl_stage = dsl_pipeline.stages[2]
    recognizer_stage = dsl_pipeline.stages[3]

    # Canonicalizer should produce a normalized template
    assert " ([!-~]*[0-9A-Za-z][!-~]*)" in canonicalizer_stage.result.template

    # Machine DSL should contain keyword classification
    assert " 'keyword': 'mixed-word'," in str(machine_dsl_stage.result.dsl.variables)

    # Human DSL should contain a readable rule
    assert "  start() interface mixed-word(var-" in human_dsl_stage.result.human_dsl

    # Recognizer should produce a valid regex
    assert r"^interface\s+" in recognizer_stage.result.patterns
