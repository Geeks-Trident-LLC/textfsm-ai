import pytest

from textfsm_ai.delivery.assembly.validator import validate_delivery_package
from textfsm_ai.delivery.core.package import (
    DeliveryPackage,
    DeliveryStatus,
    DeliveryTemplate,
)


def test_validator_rejects_empty_template():
    pkg = DeliveryPackage(
        mode="quiet",
        general=None,
        template=DeliveryTemplate("", "DSL"),
        explanation=None,
        status=DeliveryStatus("complete"),
        usage=None,
        debug=None,
    )
    with pytest.raises(ValueError):
        validate_delivery_package(pkg)
