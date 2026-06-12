from dataclasses import asdict

from ..core.package import DeliveryPackage


def delivery_to_json_dict(pkg: DeliveryPackage) -> dict:
    return asdict(pkg)
