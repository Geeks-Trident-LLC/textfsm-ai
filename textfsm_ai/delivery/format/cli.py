# textfsm_ai/delivery/format/cli.py

from typing import List

from ..core.modes import DeliveryMode
from ..core.package import DeliveryPackage


def _block(title: str, body: str) -> List[str]:
    """Helper to format a titled block with spacing."""
    lines = [f"=== {title} ==="]
    if body.strip():
        lines.extend(body.splitlines())
    else:
        lines.append("(empty)")
    lines.append("")
    return lines


def format_delivery_for_cli(pkg: DeliveryPackage) -> str:
    lines: List[str] = []

    # ------------------------------------------------------------
    # GENERAL (default/info/debug)
    # ------------------------------------------------------------
    if pkg.mode >= DeliveryMode.DEFAULT and pkg.general:
        lines.extend(
            _block(
                "General",
                "\n".join(
                    [
                        f"TextFSM:      {pkg.general.textfsm_version}",
                        f"textfsm-ai:   {pkg.general.textfsm_ai_version}",
                        f"Model:        {pkg.general.model}",
                        f"Created at:   {pkg.general.created_at}",
                    ]
                ),
            )
        )

    # ------------------------------------------------------------
    # TEMPLATE (always)
    # ------------------------------------------------------------
    lines.extend(_block("Template", pkg.template.canonical_template))

    lines.extend(_block("Human DSL", pkg.template.human_template_dsl))

    # ------------------------------------------------------------
    # EXPLANATION (default/info/debug)
    # ------------------------------------------------------------
    if pkg.mode >= DeliveryMode.DEFAULT and pkg.explanation:
        explanation_text = "\n".join(
            [
                pkg.explanation.variable_definitions,
                pkg.explanation.llm_parsing_explanation,
                pkg.explanation.template_generation_explanation,
            ]
        )
        lines.extend(_block("Explanation", explanation_text))

    # ------------------------------------------------------------
    # STATUS (always)
    # ------------------------------------------------------------
    status_lines = [f"State: {pkg.status.state}"]
    status_lines.extend([f"Warning: {w}" for w in pkg.status.warnings])
    status_lines.extend([f"Error:   {e}" for e in pkg.status.errors])
    lines.extend(_block("Status", "\n".join(status_lines)))

    # ------------------------------------------------------------
    # USAGE (info/debug)
    # ------------------------------------------------------------
    if pkg.mode >= DeliveryMode.INFO and pkg.usage:
        usage_lines = [
            f"Input tokens:   {pkg.usage.input_tokens}",
            f"Output tokens:  {pkg.usage.output_tokens}",
            f"Total tokens:   {pkg.usage.total_tokens}",
        ]
        if pkg.usage.estimated_cost is not None:
            usage_lines.append(f"Estimated cost: {pkg.usage.estimated_cost}")
        if pkg.usage.duration_ms is not None:
            usage_lines.append(f"Duration:       {pkg.usage.duration_ms} ms")

        lines.extend(_block("Usage", "\n".join(usage_lines)))

    # ------------------------------------------------------------
    # DEBUG (debug only)
    # ------------------------------------------------------------
    if pkg.mode == DeliveryMode.DEBUG and pkg.debug:
        debug_lines = []
        if pkg.debug.raw_llm_output:
            debug_lines.append("Raw LLM Output:")
            debug_lines.append(pkg.debug.raw_llm_output)
            debug_lines.append("")

        if pkg.debug.machine_dsl:
            debug_lines.append("Machine DSL:")
            debug_lines.append(str(pkg.debug.machine_dsl))
            debug_lines.append("")

        if pkg.debug.recognizer_dsl:
            debug_lines.append("Recognizer DSL:")
            debug_lines.extend(pkg.debug.recognizer_dsl)
            debug_lines.append("")

        lines.extend(_block("Debug", "\n".join(debug_lines)))

    return "\n".join(lines)
