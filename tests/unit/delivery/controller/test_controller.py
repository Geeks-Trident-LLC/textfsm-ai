from unittest.mock import MagicMock, patch

from textfsm_ai.delivery.controller.controller import DeliveryController
from textfsm_ai.delivery.core.modes import DeliveryMode


def _patched_controller(**init_kwargs):
    """Construct a DeliveryController with GenerationController, DSLController,
    and DeliveryEngine all mocked out, returning (controller, mocks)."""
    with (
        patch(
            "textfsm_ai.delivery.controller.controller.GenerationController"
        ) as mock_gen_cls,
        patch(
            "textfsm_ai.delivery.controller.controller.DSLController"
        ) as mock_dsl_cls,
        patch(
            "textfsm_ai.delivery.controller.controller.DeliveryEngine"
        ) as mock_engine_cls,
    ):
        controller = DeliveryController(
            provider_name=init_kwargs.get("provider_name", "openai"),
            api_key=init_kwargs.get("api_key", "sk-test"),
            model=init_kwargs.get("model", "gpt-4o-mini"),
            endpoint=init_kwargs.get("endpoint", ""),
            api_version=init_kwargs.get("api_version", ""),
            region=init_kwargs.get("region", ""),
            project=init_kwargs.get("project", ""),
            compartment_id=init_kwargs.get("compartment_id", ""),
            max_tries=init_kwargs.get("max_tries", 1),
        )
    return controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls


def test_init_builds_model_info_and_constructs_gen_controller():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller(
        provider_name="anthropic",
        api_key="sk-abc",
        model="claude-sonnet-4-5",
        endpoint="https://example.com",
        api_version="2024-01-01",
        max_tries=3,
    )

    assert controller._model_info == {
        "provider_name": "anthropic",
        "api_key": "sk-abc",
        "model": "claude-sonnet-4-5",
        "endpoint": "https://example.com",
        "api_version": "2024-01-01",
        "region": "",
        "project": "",
        "compartment_id": "",
    }

    mock_gen_cls.assert_called_once_with(
        provider_name="anthropic",
        api_key="sk-abc",
        model="claude-sonnet-4-5",
        endpoint="https://example.com",
        api_version="2024-01-01",
        region="",
        project="",
        compartment_id="",
        max_retries=3,
    )
    mock_dsl_cls.assert_called_once_with()
    mock_engine_cls.assert_called_once_with()


def test_init_builds_model_info_with_bedrock_region():
    controller, mock_gen_cls, _mock_dsl_cls, _mock_engine_cls = _patched_controller(
        provider_name="bedrock",
        api_key="",
        model="anthropic.claude-haiku-4-5-v1:0",
        region="us-east-1",
    )

    assert controller._model_info == {
        "provider_name": "bedrock",
        "api_key": "",
        "model": "anthropic.claude-haiku-4-5-v1:0",
        "endpoint": "",
        "api_version": "",
        "region": "us-east-1",
        "project": "",
        "compartment_id": "",
    }

    mock_gen_cls.assert_called_once_with(
        provider_name="bedrock",
        api_key="",
        model="anthropic.claude-haiku-4-5-v1:0",
        endpoint="",
        api_version="",
        region="us-east-1",
        project="",
        compartment_id="",
        max_retries=1,
    )


def test_init_builds_model_info_with_vertexai_project_and_region():
    controller, mock_gen_cls, _mock_dsl_cls, _mock_engine_cls = _patched_controller(
        provider_name="vertexai",
        api_key="",
        model="gemini-2.5-flash",
        region="us-central1",
        project="my-gcp-project",
    )

    assert controller._model_info == {
        "provider_name": "vertexai",
        "api_key": "",
        "model": "gemini-2.5-flash",
        "endpoint": "",
        "api_version": "",
        "region": "us-central1",
        "project": "my-gcp-project",
        "compartment_id": "",
    }

    mock_gen_cls.assert_called_once_with(
        provider_name="vertexai",
        api_key="",
        model="gemini-2.5-flash",
        endpoint="",
        api_version="",
        region="us-central1",
        project="my-gcp-project",
        compartment_id="",
        max_retries=1,
    )


def test_init_builds_model_info_with_oci_compartment_id_and_region():
    controller, mock_gen_cls, _mock_dsl_cls, _mock_engine_cls = _patched_controller(
        provider_name="oci",
        api_key="",
        model="meta.llama-3.3-70b-instruct",
        region="us-chicago-1",
        compartment_id="ocid1.compartment.oc1..fake",
    )

    assert controller._model_info == {
        "provider_name": "oci",
        "api_key": "",
        "model": "meta.llama-3.3-70b-instruct",
        "endpoint": "",
        "api_version": "",
        "region": "us-chicago-1",
        "project": "",
        "compartment_id": "ocid1.compartment.oc1..fake",
    }

    mock_gen_cls.assert_called_once_with(
        provider_name="oci",
        api_key="",
        model="meta.llama-3.3-70b-instruct",
        endpoint="",
        api_version="",
        region="us-chicago-1",
        project="",
        compartment_id="ocid1.compartment.oc1..fake",
        max_retries=1,
    )


def test_run_wires_gen_output_into_dsl_input():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller()

    gen_instance = mock_gen_cls.return_value
    dsl_instance = mock_dsl_cls.return_value
    engine_instance = mock_engine_cls.return_value

    gen_pipeline_sentinel = MagicMock(name="gen_pipeline")
    dsl_pipeline_sentinel = MagicMock(name="dsl_pipeline")
    gen_instance.run.return_value = gen_pipeline_sentinel
    dsl_instance.run.return_value = dsl_pipeline_sentinel

    controller.run("raw sample text", mode="default")

    gen_instance.run.assert_called_once_with("raw sample text")
    # DSL must be called with exactly what generation produced
    dsl_instance.run.assert_called_once_with(gen_pipeline_sentinel)

    engine_instance.assemble.assert_called_once()
    _, kwargs = engine_instance.assemble.call_args
    assert kwargs["generation_pipeline"] is gen_pipeline_sentinel
    assert kwargs["dsl_pipeline"] is dsl_pipeline_sentinel


def test_run_converts_mode_string_to_enum():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller()
    engine_instance = mock_engine_cls.return_value

    controller.run("sample", mode="info")

    _, kwargs = engine_instance.assemble.call_args
    assert kwargs["mode"] is DeliveryMode.INFO


def test_run_passes_model_info_and_as_json_through():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller(
        provider_name="openai", api_key="sk-x", model="gpt-4o-mini"
    )
    engine_instance = mock_engine_cls.return_value

    controller.run("sample", mode="debug", as_json=True)

    _, kwargs = engine_instance.assemble.call_args
    assert kwargs["model_info"] == controller._model_info
    assert kwargs["as_json"] is True
    assert kwargs["mode"] is DeliveryMode.DEBUG


def test_run_computes_non_negative_integer_duration():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller()
    engine_instance = mock_engine_cls.return_value

    controller.run("sample", mode="quiet")

    _, kwargs = engine_instance.assemble.call_args
    assert isinstance(kwargs["duration_ms"], int)
    assert kwargs["duration_ms"] >= 0


def test_run_returns_engine_assemble_result():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller()
    engine_instance = mock_engine_cls.return_value
    engine_instance.assemble.return_value = "the-delivery-output"

    result = controller.run("sample", mode="quiet")

    assert result == "the-delivery-output"


def test_run_invalid_mode_raises():
    controller, mock_gen_cls, mock_dsl_cls, mock_engine_cls = _patched_controller()

    try:
        controller.run("sample", mode="not-a-real-mode")
        assert False, "expected ValueError"
    except ValueError:
        pass
