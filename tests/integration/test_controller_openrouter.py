# tests/integration/test_controller_openrouter.py

from textfsm_ai.core.utils.template import parse_to_lists
from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.controller.generation_controller import GenerationController
from textfsm_ai.models import model as MODEL


def test_real(openrouter_key):
    gen = GenerationController(
        provider_name="openrouter",
        api_key=openrouter_key,
        model=MODEL.openrouter.default,
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

    # ------------------------------------------------------------
    # 3. Canonicalizer checks
    # ------------------------------------------------------------
    llm_template = gen_pipeline.last_stage.template
    canonical_template = dsl_pipeline.dsl.canonical

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
    # 4. Readable DSL checks
    # ------------------------------------------------------------
    readable_dsl = dsl_pipeline.dsl.readable

    expected_readable = " start() interface mixed-word(var-"
    assert expected_readable in readable_dsl, (
        f"Readble DSL missing rule {expected_readable!r}\n"
        f"--- Readable DSL ---\n{readable_dsl}\n"
        f"--- Canonical Template ---\n{canonical_template}"
    )

    # ------------------------------------------------------------
    # 5. Recognizer checks
    # ------------------------------------------------------------
    recognizers = dsl_pipeline.dsl.recognizers

    expected_pattern = r"^interface\s+"
    assert expected_pattern in recognizers[0], (
        f"Recognizer missing expected pattern {expected_pattern!r}\n"
        f"--- Recognizer Patterns ---\n{recognizers}\n"
        f"--- Human DSL ---\n{readable_dsl}\n"
        f"--- Canonical Template ---\n{canonical_template}"
    )
