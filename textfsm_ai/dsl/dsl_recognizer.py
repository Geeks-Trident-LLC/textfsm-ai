from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from textfsm_ai.dsl.dsl_extractor import extract_machine_dsl
from textfsm_ai.dsl.infer import infer_base_keyword
from textfsm_ai.dsl.patterns import PATTERNS_MAPPING

PUNCTS_GROUP = PATTERNS_MAPPING.get("puncts-group")
DIGITS = PATTERNS_MAPPING.get("digits")
NUMBER = PATTERNS_MAPPING.get("number", r"\S+")


def _build_literal_regex(txt: str, *, debug: bool = False) -> str:
    """
    Build recognizer regex for literal matched text according to DSL rules.

    Workflow:
      - If txt contains a puncts-group sequence, split into pre/mid/post:
            pre  -> recurse
            mid  -> PUNCTS_GROUP
            post -> recurse
      - Otherwise tokenize with:
            r"\\s+|\\s\\+|[^\\s\\]+|\\"
      - For each token:
            * whitespace or '\\s+' → '\\s+'
            * keyword in letter/word/mixed-word (no digits) → escaped literal
            * keyword in punct/puncts → escaped literal
            * keyword in digit/digits/number → NUMBER pattern
            * else → NUMBER fallback
    """
    if not txt:
        return ""

    # 1) puncts-group detection on the *text* itself
    if PUNCTS_GROUP:
        m = re.search(PUNCTS_GROUP, txt)
        if m:
            pre = txt[: m.start()]
            mid = txt[m.start() : m.end()]
            post = txt[m.end() :]

            if debug:
                print(f"  [literal] puncts-group match: {mid!r}")
                print(f"    pre:  {pre!r}")
                print(f"    post: {post!r}")

            parts: List[str] = []
            if pre:
                parts.append(_build_literal_regex(pre, debug=debug))
            parts.append(PUNCTS_GROUP)
            if post:
                parts.append(_build_literal_regex(post, debug=debug))
            return "".join(parts)

    # 2) Tokenize
    tokens = re.findall(r"\s+|\\s\+|[^\s\\]+|\\", txt)

    if debug:
        print(f"  [literal] tokens: {tokens!r}")

    out: List[str] = []

    for tok in tokens:
        if tok.isspace() or tok == r"\s+":
            if debug:
                print(f"    token={tok!r} -> '\\s+' (whitespace)")
            out.append(r"\s+")
            continue

        keyword = infer_base_keyword([tok])

        if keyword in ("letter", "word", "mixed-word") and (
            not DIGITS or not re.search(DIGITS, tok)
        ):
            pat = re.escape(tok)
            if debug:
                print(
                    f"    token={tok!r} keyword={keyword} -> {pat!r} (escaped literal)"
                )
            out.append(pat)
            continue

        if keyword in ("punct", "puncts"):
            pat = re.escape(tok)
            if debug:
                print(f"    token={tok!r} keyword={keyword} -> {pat!r} (escaped punct)")
            out.append(pat)
            continue

        if keyword in ("digit", "digits", "number"):
            if debug:
                print(f"    token={tok!r} keyword={keyword} -> {NUMBER!r} (number)")
            out.append(NUMBER)
            continue

        pat = PATTERNS_MAPPING.get(keyword, r"\S+")
        if debug:
            print(f"    token={tok!r} keyword={keyword} -> {pat!r}")
        out.append(pat)

    return "".join(out)


_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _build_variable_pattern(
    pattern: str, var_map: Dict[str, str], *, debug: bool = False
) -> str:
    """
    Variable case:
      - prematch: keep as-is (literal pattern, including '\\s+')
      - match: replace ${var} with its expression_regex
      - remaining: keep as-is
      - if final ends with $$, convert to $
    """
    out: List[str] = []
    pos = 0

    for m in _VAR_RE.finditer(pattern):
        var_name = m.group(1)
        prematch = pattern[pos : m.start()]
        out.append(prematch)

        if var_name not in var_map:
            raise KeyError(f"Variable '{var_name}' not found in DSL variables.")

        var_regex = var_map[var_name]
        if debug:
            print(f"  [variable] {var_name} -> {var_regex!r}")
        out.append(var_regex)
        pos = m.end()

    tail = pattern[pos:]
    out.append(tail)

    final = "".join(out)
    if final.endswith("$$"):
        final = final[:-2] + "$"

    if debug:
        print(f"  [variable] final: {final!r}")

    return final


def _build_variable_map(dsl: Dict[str, Any]) -> Dict[str, str]:
    return {v["name"]: v["expression_regex"] for v in dsl.get("variables", [])}


def visualize_pattern_matches(pattern: str, sample: str, max_matches: int = 3) -> str:
    try:
        regex = re.compile(pattern, re.MULTILINE)
    except re.error as exc:
        return f"[INVALID REGEX] {pattern!r}: {exc}"

    lines: List[str] = [f"Pattern: {pattern}"]
    count = 0

    for m in regex.finditer(sample):
        if count >= max_matches:
            lines.append("  ... (more matches omitted)")
            break
        start, end = m.span()
        snippet = sample[start:end].replace("\n", "\\n")
        lines.append(f"  Match {count + 1}: span=({start}, {end}) text={snippet!r}")
        count += 1

    if count == 0:
        lines.append("  (no matches)")
    return "\n".join(lines)


def visualize_literal_transformation(txt: str, regex: str) -> str:
    return f"Literal: {txt!r}\nRegex:   {regex!r}"


def recognize_dsl_patterns(
    dsl: Optional[Dict[str, Any]],
    template: Optional[str],
    sample: str,
    *,
    debug: bool = False,
) -> str:
    """
    DSL recognizer:

    - Inputs: dsl, template, sample
    - If dsl is None: dsl = extract_machine_dsl(template)
    - For each transition.pattern:
        * if contains ${var}: variable case (no sample needed)
        * else: literal case (must match sample; use matched text)
    - Returns newline-joined unique recognizer patterns.
    """
    if dsl is None:
        if template is None:
            raise ValueError("Either 'dsl' or 'template' must be provided.")
        dsl = extract_machine_dsl(template)

    var_map = _build_variable_map(dsl)
    seen: List[str] = []
    out: List[str] = []

    for state in dsl.get("states", []):
        state_name = state.get("name", "<unknown>")

        for trans in state.get("transitions", []):
            pattern = trans["pattern"]

            if debug:
                print(f"\n[STATE {state_name}] pattern: {pattern!r}")

            # variable case
            if "${" in pattern:
                final = _build_variable_pattern(pattern, var_map, debug=debug)
                if final not in seen:
                    seen.append(final)
                    out.append(final)
                continue

            # literal case
            try:
                regex = re.compile(pattern, re.MULTILINE)
            except re.error as exc:
                if debug:
                    print(f"  [literal] invalid pattern {pattern!r}: {exc}")
                continue

            m = regex.search(sample)
            if not m:
                if debug:
                    print("  [literal] no match in sample; skipping")
                continue

            matched_text = m.group(0)
            if debug:
                print(f"  [literal] matched text: {matched_text!r}")

            body = _build_literal_regex(matched_text, debug=debug)

            prefix = "^" if pattern.lstrip().startswith("^") else ""
            stripped = pattern.rstrip()
            suffix = ""
            if stripped.endswith("$$"):
                suffix = "$"
            elif stripped.endswith("$"):
                suffix = "$"

            final = f"{prefix}{body}{suffix}"

            if debug:
                print(visualize_literal_transformation(matched_text, final))
                print(visualize_pattern_matches(final, sample, max_matches=2))

            if final not in seen:
                seen.append(final)
                out.append(final)

    return "\n".join(out)
