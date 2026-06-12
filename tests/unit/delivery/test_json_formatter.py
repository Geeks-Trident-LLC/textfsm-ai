from textfsm_ai.delivery.core.package import (
    DeliveryPackage,
    DeliveryStatus,
    DeliveryTemplate,
)
from textfsm_ai.delivery.format.json import delivery_to_json_dict


def test_json_formatter():
    pkg = DeliveryPackage(
        mode="quiet",
        general=None,
        template=DeliveryTemplate("T", "DSL"),
        explanation=None,
        status=DeliveryStatus("complete"),
        usage=None,
        debug=None,
    )
    d = delivery_to_json_dict(pkg)
    assert d["template"]["canonical_template"] == "T"
