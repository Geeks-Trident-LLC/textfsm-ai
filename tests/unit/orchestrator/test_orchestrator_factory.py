import pytest

from textfsm_ai.orchestrator.factory import create_orchestrator_from_config
from textfsm_ai.orchestrator.orchestrator import Orchestrator
from textfsm_ai.providers.config import OrchestratorConfig, ProviderConfig


def test_create_orchestrator_from_config_success():
    cfg = OrchestratorConfig(
        providers={
            "openai": ProviderConfig(
                name="openai",
                type="openai",
                params={"api_key": "sk-test", "default_model": "gpt-4o-mini"},
            )
        }
    )

    orch = create_orchestrator_from_config(cfg)

    assert isinstance(orch, Orchestrator)
    assert "openai" in orch._providers
    assert orch._providers["openai"].name == "openai"


def test_create_orchestrator_from_config_multiple_providers():
    cfg = OrchestratorConfig(
        providers={
            "openai": ProviderConfig(
                name="openai",
                type="openai",
                params={"api_key": "sk-openai", "default_model": "gpt-4o-mini"},
            ),
            "anthropic": ProviderConfig(
                name="anthropic",
                type="anthropic",
                params={
                    "api_key": "sk-anthropic",
                    "default_model": "claude-sonnet-4-5",
                },
            ),
        }
    )

    orch = create_orchestrator_from_config(cfg)

    assert set(orch._providers.keys()) == {"openai", "anthropic"}


def test_create_orchestrator_from_config_sets_instance_name_from_entry():
    # entry.name can differ from the provider type/class default; the
    # factory must stamp instance.name = entry.name, not leave the class default.
    cfg = OrchestratorConfig(
        providers={
            "my-custom-openai": ProviderConfig(
                name="my-custom-openai",
                type="openai",
                params={"api_key": "sk-test", "default_model": "gpt-4o-mini"},
            )
        }
    )

    orch = create_orchestrator_from_config(cfg)

    instance = orch._providers["my-custom-openai"]
    assert instance.name == "my-custom-openai"


def test_create_orchestrator_from_config_empty_providers():
    cfg = OrchestratorConfig(providers={})
    orch = create_orchestrator_from_config(cfg)

    assert isinstance(orch, Orchestrator)
    assert orch._providers == {}


def test_create_orchestrator_from_config_invalid_entry_type_raises():
    cfg = OrchestratorConfig(providers={"bad": {"not": "a ProviderConfig"}})

    with pytest.raises(ValueError, match="Invalid provider entry"):
        create_orchestrator_from_config(cfg)


def test_create_orchestrator_from_config_unknown_provider_type_raises_valueerror():
    # Regression test: registry.get() raises KeyError on unmatched
    # providers, it never returns None. The old `if provider_cls is None`
    # check was unreachable dead code, so an unknown provider type
    # leaked a raw KeyError instead of this intended ValueError.
    cfg = OrchestratorConfig(
        providers={
            "bogus": ProviderConfig(name="bogus", type="not-a-real-provider", params={})
        }
    )

    with pytest.raises(ValueError, match="Unknown provider type: not-a-real-provider"):
        create_orchestrator_from_config(cfg)
