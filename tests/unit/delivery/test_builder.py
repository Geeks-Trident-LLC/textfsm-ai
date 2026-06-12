from textfsm_ai.delivery.assembly.builder import build_delivery_package


def test_builder_quiet_mode():
    pkg = build_delivery_package(
        mode="quiet",
        textfsm_version="1.1.0",
        textfsm_ai_version="0.3.7",
        model="test-model",
        canonical_template="Value X (.*)",
        human_template_dsl="X: (.*)",
        status_state="complete",
    )
    assert pkg.mode == "quiet"
    assert pkg.template.canonical_template == "Value X (.*)"
