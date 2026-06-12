from typing import List

from ..core.package import DeliveryPackage


def format_delivery_for_cli(pkg: DeliveryPackage) -> str:
    lines: List[str] = []

    if pkg.general:
        lines.append("=== General ===")
        lines.append(f"TextFSM:      {pkg.general.textfsm_version}")
        lines.append(f"textfsm-ai:   {pkg.general.textfsm_ai_version}")
        lines.append(f"Model:        {pkg.general.model}")
        lines.append(f"Created at:   {pkg.general.created_at}")
        lines.append("")

    lines.append("=== Template ===")
    lines.append(pkg.template.canonical_template)
    lines.append("")
    lines.append("--- Human DSL ---")
    lines.append(pkg.template.human_template_dsl)
    lines.append("")

    if pkg.explanation:
        lines.append("=== Explanation ===")
        lines.append(pkg.explanation.variable_definitions)
        lines.append(pkg.explanation.llm_parsing_explanation)
        lines.append(pkg.explanation.template_generation_explanation)
        lines.append("")

    lines.append("=== Status ===")
    lines.append(f"State: {pkg.status.state}")
    for w in pkg.status.warnings:
        lines.append(f"Warning: {w}")
    for e in pkg.status.errors:
        lines.append(f"Error: {e}")
    lines.append("")

    if pkg.usage:
        lines.append("=== Usage ===")
        lines.append(f"Input tokens:   {pkg.usage.input_tokens}")
        lines.append(f"Output tokens:  {pkg.usage.output_tokens}")
        lines.append(f"Total tokens:   {pkg.usage.total_tokens}")
        if pkg.usage.estimated_cost is not None:
            lines.append(f"Estimated cost: {pkg.usage.estimated_cost}")
        if pkg.usage.duration_ms is not None:
            lines.append(f"Duration:       {pkg.usage.duration_ms} ms")
        lines.append("")

    if pkg.debug:
        lines.append("=== Debug ===")
        if pkg.debug.raw_llm_output:
            lines.append(pkg.debug.raw_llm_output)
        lines.append("")

    return "\n".join(lines)
