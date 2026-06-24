# tests/integration/test_controller_openai.py

from textfsm_ai.core.utils.template import parse_to_lists
from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.models import model as MODEL


def test_real(openai_key):
    gen = GenerationController(
        provider_name="openai",
        api_key=openai_key,
        model=MODEL.openai.default,
        max_retries=2,
    )

    gen_pipeline = gen.run("interface GigabitEthernet0/1")
    assert gen_pipeline.ready, f"Generation failed: {gen_pipeline.reason}"

    # Template must parse the sample and include the interface name
    rows = parse_to_lists(gen_pipeline.last_stage.template, gen_pipeline.sample)
    for row in rows:
        assert "GigabitEthernet0/1" in row, (
            f"Expected interface name missing in parsed row.\nRow: {row}\n"
            f"Template:\n{gen_pipeline.last_stage.template}"
        )

    # ------------------------------------------------------------
    # 2. Run DSL controller
    # ------------------------------------------------------------
    dsl = DSLController()
    dsl_pipeline = dsl.run(gen_pipeline)

    assert dsl_pipeline.ready, f"DSL pipeline failed: {dsl_pipeline.reason}"
    assert (
        len(dsl_pipeline.stages) == 4
    ), f"Expected 4 DSL stages, got {len(dsl_pipeline.stages)}"

    canonicalizer_stage = dsl_pipeline.stages[0]
    machine_stage = dsl_pipeline.stages[1]
    human_stage = dsl_pipeline.stages[2]
    recognizer_stage = dsl_pipeline.stages[3]

    # ------------------------------------------------------------
    # 3. Canonicalizer checks
    # ------------------------------------------------------------
    llm_template = gen_pipeline.last_stage.template
    canonical_template = canonicalizer_stage.result.template

    expected_substrings = [
        "Value ",
        " ([!-~]*[0-9A-Za-z][!-~]*)",
        "\n\nStart",
        " ^interface\\s+",
    ]

    for expected in expected_substrings:
        assert expected in canonical_template, (
            f"Missing expected canonical substring {expected!r}\n"
            f"--- Canonical Template ---\n{canonical_template}\n"
            f"--- LLM Template ---\n{llm_template}"
        )

    # ------------------------------------------------------------
    # 4. Machine DSL checks
    # ------------------------------------------------------------
    machine_vars = str(machine_stage.result.dsl.variables)
    expected_keyword = " 'keyword': 'mixed-word',"

    assert expected_keyword in machine_vars, (
        f"Machine DSL missing keyword classification {expected_keyword!r}\n"
        f"--- Machine DSL Variables ---\n{machine_vars}\n"
        f"--- Canonical Template ---\n{canonical_template}"
    )

    # ------------------------------------------------------------
    # 5. Human DSL checks
    # ------------------------------------------------------------
    human_dsl = human_stage.result.human_dsl
    repr_machine_dsl = machine_stage.result.dsl.to_json()

    expected_human = " start() interface mixed-word(var-"
    assert expected_human in human_dsl, (
        f"Human DSL missing readable rule {expected_human!r}\n"
        f"--- Human DSL ---\n{human_dsl}\n"
        f"--- Machine DSL ---\n{repr_machine_dsl}\n"
        f"--- Canonical Template ---\n{canonical_template}"
    )

    # ------------------------------------------------------------
    # 6. Recognizer checks
    # ------------------------------------------------------------
    recognizer_patterns = recognizer_stage.result.patterns
    expected_pattern = r"^interface\s+"

    assert expected_pattern in recognizer_patterns, (
        f"Recognizer missing expected pattern {expected_pattern!r}\n"
        f"--- Recognizer Patterns ---\n{recognizer_patterns}\n"
        f"--- Human DSL ---\n{human_dsl}\n"
        f"--- Machine DSL ---\n{repr_machine_dsl}\n"
        f"--- Canonical Template ---\n{canonical_template}"
    )
