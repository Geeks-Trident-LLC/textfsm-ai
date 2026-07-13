# tests/unit/test_api.py

from __future__ import annotations

from textfsm_ai.api import (
    DSLResult,
    LLMResult,
    compile_dsl,
    generate,
    run_pipeline,
    to_ast,
    to_canonical,
    to_dsl_result,
    to_llm_handling,
    to_llm_records,
    to_llm_result,
    to_llm_template,
    to_llm_variables,
    to_readable,
    to_recognizers,
)
from textfsm_ai.delivery.core.package import DeliveryOutput
from textfsm_ai.dsl.ast.nodes import TemplateAST
from textfsm_ai.generation.core.models import (
    GenerationPipeline,
    GenerationStage,
    StructuredResponse,
)

VALID_TEMPLATE = "Value Required v1 (\\S+)\n\nStart\n  ^foo ${v1} -> Record"
VALID_RECORDS = [{"v1": "abc"}]


def _make_pipeline(metadata: StructuredResponse | None, ready: bool, reason: str = ""):
    stage = GenerationStage(template="", records=[], metadata=metadata, ready=ready)
    return GenerationPipeline(last_stage=stage, ready=ready, reason=reason)


def _patch_generation_controller(monkeypatch, pipeline):
    class FakeController:
        def __init__(self, **kwargs):
            pass

        def run(self, sample, **kwargs):
            return pipeline

    monkeypatch.setattr("textfsm_ai.api.GenerationController", FakeController)


# ---------------------------------------------------------
# generate() — verb_target
# ---------------------------------------------------------
def test_generate_returns_api_llm_exact_result_on_success(monkeypatch):
    metadata = StructuredResponse(
        template="Value v1 (\\S+)",
        records=[{"v1": "abc"}],
        variables={"v1": "the first token"},
        handling=["matched greedily"],
        response=None,
        ready=True,
    )
    _patch_generation_controller(monkeypatch, _make_pipeline(metadata, ready=True))

    result = generate("sample", "openai", "key", "gpt-4")

    assert isinstance(result, LLMResult)
    assert result.ready is True
    assert result.template == "Value v1 (\\S+)"
    assert result.records == [{"v1": "abc"}]
    assert result.variables == {"v1": "the first token"}
    assert result.handling == ["matched greedily"]


def test_generate_does_not_raise_on_failure_and_returns_reason(monkeypatch):
    _patch_generation_controller(
        monkeypatch, _make_pipeline(None, ready=False, reason="retries exhausted")
    )

    result = generate("sample", "openai", "key", "gpt-4")

    assert isinstance(result, LLMResult)
    assert result.ready is False
    assert result.reason == "retries exhausted"
    assert result.template == ""
    assert result.records == []
    assert result.variables == {}
    assert result.handling == []


def test_generate_uses_pipeline_status_not_nested_metadata_status(monkeypatch):
    """
    The pipeline-level ready/reason are authoritative (they account for
    retries and template validation); the nested StructuredResponse's own
    ready/reason only reflect whether the raw LLM JSON had a template field.
    """
    metadata = StructuredResponse(
        template="bad $$$ template",
        records=[],
        variables={},
        handling=[],
        response=None,
        reason="",
        ready=True,  # JSON had a template field...
    )
    # ...but the pipeline failed overall (e.g. syntax validation after retries).
    _patch_generation_controller(
        monkeypatch,
        _make_pipeline(metadata, ready=False, reason="template_syntax_error"),
    )

    result = generate("sample", "openai", "key", "gpt-4")

    assert result.ready is False
    assert result.reason == "template_syntax_error"


# ---------------------------------------------------------
# to_llm_result() — alias of generate()
# ---------------------------------------------------------
def test_to_llm_result_is_alias_of_generate(monkeypatch):
    metadata = StructuredResponse(
        template="Value v1 (\\S+)",
        records=[],
        variables={},
        handling=[],
        response=None,
        ready=True,
    )
    _patch_generation_controller(monkeypatch, _make_pipeline(metadata, ready=True))

    assert to_llm_result("sample", "openai", "key", "gpt-4") == generate(
        "sample", "openai", "key", "gpt-4"
    )


# ---------------------------------------------------------
# to_llm_template/records/variables/handling — to_target shortcuts
# ---------------------------------------------------------
def test_to_llm_shortcuts_on_success(monkeypatch):
    metadata = StructuredResponse(
        template="Value v1 (\\S+)",
        records=[{"v1": "abc"}],
        variables={"v1": "explained"},
        handling=["note"],
        response=None,
        ready=True,
    )
    _patch_generation_controller(monkeypatch, _make_pipeline(metadata, ready=True))

    assert to_llm_template("sample", "openai", "key", "gpt-4") == "Value v1 (\\S+)"
    assert to_llm_records("sample", "openai", "key", "gpt-4") == [{"v1": "abc"}]
    assert to_llm_variables("sample", "openai", "key", "gpt-4") == {"v1": "explained"}
    assert to_llm_handling("sample", "openai", "key", "gpt-4") == ["note"]


def test_to_llm_template_returns_reason_string_on_failure(monkeypatch):
    _patch_generation_controller(
        monkeypatch, _make_pipeline(None, ready=False, reason="rate limited")
    )

    assert to_llm_template("sample", "openai", "key", "gpt-4") == "rate limited"


def test_to_llm_records_variables_handling_return_empty_on_failure(monkeypatch):
    _patch_generation_controller(
        monkeypatch, _make_pipeline(None, ready=False, reason="rate limited")
    )

    assert to_llm_records("sample", "openai", "key", "gpt-4") == []
    assert to_llm_variables("sample", "openai", "key", "gpt-4") == {}
    assert to_llm_handling("sample", "openai", "key", "gpt-4") == []


# ---------------------------------------------------------
# compile_dsl() — verb_target
# ---------------------------------------------------------
def test_compile_dsl_returns_api_dsl_result_on_success():
    result = compile_dsl(VALID_TEMPLATE, VALID_RECORDS)

    assert isinstance(result, DSLResult)
    assert result.ready is True
    assert isinstance(result.ast, TemplateAST)
    assert result.canonical
    assert result.readable
    assert result.recognizers


def test_compile_dsl_does_not_raise_on_failure(monkeypatch):
    monkeypatch.setattr(
        "textfsm_ai.dsl.engine.dsl_engine.parse_textfsm",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("bad template")),
    )

    result = compile_dsl("garbage", [])

    assert isinstance(result, DSLResult)
    assert result.ready is False
    assert "BUILD-AST-ERROR" in result.reason
    assert result.ast == TemplateAST()
    assert result.canonical == ""
    assert result.readable == ""
    assert result.recognizers == []


# ---------------------------------------------------------
# to_dsl_result() — alias of compile_dsl()
# ---------------------------------------------------------
def test_to_dsl_result_is_alias_of_compile_dsl():
    assert to_dsl_result(VALID_TEMPLATE, VALID_RECORDS) == compile_dsl(
        VALID_TEMPLATE, VALID_RECORDS
    )


# ---------------------------------------------------------
# to_ast/to_canonical/to_readable/to_recognizers — to_target shortcuts
# ---------------------------------------------------------
def test_to_dsl_shortcuts_on_success():
    assert isinstance(to_ast(VALID_TEMPLATE, VALID_RECORDS), TemplateAST)
    assert to_canonical(VALID_TEMPLATE, VALID_RECORDS)
    assert to_readable(VALID_TEMPLATE, VALID_RECORDS)
    assert to_recognizers(VALID_TEMPLATE, VALID_RECORDS)


def test_to_canonical_and_to_readable_return_reason_string_on_failure(monkeypatch):
    monkeypatch.setattr(
        "textfsm_ai.dsl.engine.dsl_engine.parse_textfsm",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("bad template")),
    )

    canonical = to_canonical("garbage", [])
    readable = to_readable("garbage", [])

    assert "BUILD-AST-ERROR" in canonical
    assert "BUILD-AST-ERROR" in readable


def test_to_ast_and_to_recognizers_return_empty_datatype_on_failure(monkeypatch):
    monkeypatch.setattr(
        "textfsm_ai.dsl.engine.dsl_engine.parse_textfsm",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("bad template")),
    )

    assert to_ast("garbage", []) == TemplateAST()
    assert to_recognizers("garbage", []) == []


# ---------------------------------------------------------
# run_pipeline()
# ---------------------------------------------------------
def test_run_pipeline_delegates_to_delivery_controller(monkeypatch):
    expected = DeliveryOutput(mode=1, output="Value v1 (\\S+)", passed=True, error="")

    class FakeDeliveryController:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self, sample, mode, as_json):
            return expected

    monkeypatch.setattr("textfsm_ai.api.DeliveryController", FakeDeliveryController)

    result = run_pipeline("sample", "openai", "key", "gpt-4")

    assert result is expected
    assert result.passed is True


def test_run_pipeline_does_not_raise_on_failure(monkeypatch):
    expected = DeliveryOutput(mode=1, output="", passed=False, error="something failed")

    class FakeDeliveryController:
        def __init__(self, **kwargs):
            pass

        def run(self, sample, mode, as_json):
            return expected

    monkeypatch.setattr("textfsm_ai.api.DeliveryController", FakeDeliveryController)

    result = run_pipeline("sample", "openai", "key", "gpt-4")

    assert result.passed is False
    assert result.error == "something failed"
