# textfsm_ai/delivery/assembly/validator.py

from ..core.modes import DeliveryMode
from ..core.package import DeliveryPackage


def validate_delivery_package(pkg: DeliveryPackage) -> None:
    # ------------------------------------------------------------
    # 1. Template must always exist
    # ------------------------------------------------------------

    if not pkg.template:
        raise ValueError("template section must not be None")

    if pkg.template.canonical_template and not pkg.template.canonical_template.strip():
        raise ValueError("canonical_template must not be empty")

    if pkg.template.human_template_dsl and not pkg.template.human_template_dsl.strip():
        raise ValueError("human_template_dsl must not be empty")

    # ------------------------------------------------------------
    # 2. Status must always exist
    # ------------------------------------------------------------
    if not pkg.status:
        raise ValueError("status section must not be None")

    if not pkg.status.state:
        raise ValueError("status.state must not be empty")

    # ------------------------------------------------------------
    # 3. DEFAULT, INFO, DEBUG require general + explanation
    # ------------------------------------------------------------
    if pkg.mode >= DeliveryMode.DEFAULT:
        if pkg.general is None:
            raise ValueError("general section required for DEFAULT/INFO/DEBUG modes")

        if pkg.explanation is None:
            raise ValueError(
                "explanation section required for DEFAULT/INFO/DEBUG modes"
            )

    # ------------------------------------------------------------
    # 4. INFO, DEBUG require usage (if tokens exist)
    # ------------------------------------------------------------
    if pkg.mode >= DeliveryMode.INFO:
        # usage may be None if no token info was provided
        if pkg.usage is not None:
            if pkg.usage.input_tokens is not None and pkg.usage.input_tokens < 0:
                raise ValueError("usage.input_tokens must be >= 0")
            if pkg.usage.output_tokens is not None and pkg.usage.output_tokens < 0:
                raise ValueError("usage.output_tokens must be >= 0")
            if pkg.usage.total_tokens is not None and pkg.usage.total_tokens < 0:
                raise ValueError("usage.total_tokens must be >= 0")

    # ------------------------------------------------------------
    # 5. DEBUG requires debug section
    # ------------------------------------------------------------
    if pkg.mode == DeliveryMode.DEBUG:
        if pkg.debug is None:
            raise ValueError("debug mode requires debug section")

        # Optional but helpful: ensure debug fields are structurally valid
        if pkg.debug.machine_dsl is not None and not isinstance(
            pkg.debug.machine_dsl, dict
        ):
            raise ValueError("debug.machine_dsl must be a dict")

        if pkg.debug.recognizer_pattern is not None and not isinstance(
            pkg.debug.recognizer_pattern, list
        ):
            raise ValueError("debug.recognizer_dsl must be a list")
