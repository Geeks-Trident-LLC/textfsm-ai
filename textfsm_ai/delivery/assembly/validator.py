from ..core.package import DeliveryPackage


def validate_delivery_package(pkg: DeliveryPackage) -> None:
    if not pkg.template.canonical_template:
        raise ValueError("canonical_template must not be empty")

    if pkg.mode == "debug" and pkg.debug is None:
        raise ValueError("debug mode requires debug section")
