from textfsm_ai.delivery.core.package import (
    DeliveryPackage,
    DeliveryStatus,
    DeliveryTemplate,
)
from textfsm_ai.delivery.format.cli import format_delivery_for_cli


def test_cli_formatter_basic():
    pkg = DeliveryPackage(
        mode="quiet",
        general=None,
        template=DeliveryTemplate("T", "DSL"),
        explanation=None,
        status=DeliveryStatus("complete"),
        usage=None,
        debug=None,
    )
    out = format_delivery_for_cli(pkg)
    assert "T" in out
