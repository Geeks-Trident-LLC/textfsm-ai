from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from textfsm_ai.dsl.core.models import DSLExtractorResult
from textfsm_ai.dsl.core.patterns import PATTERNS_MAPPING
from textfsm_ai.dsl.engine.parse.dsl_extractor import extract_machine_dsl
from textfsm_ai.dsl.engine.parse.infer import infer_base_keyword

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
    Build a regex pattern by replacing ${var} with its expression_regex.

    Improvements:
      - Use fullmatch to extract prefix (^), body, suffix ($ or $$)
      - Apply variable substitution only to the body
      - Normalize literal segments using _build_literal_regex()
      - Convert final $$ → $ (TextFSM escaping rule)
    """
    # 1. Extract prefix (^), body, suffix ($ or $$)
    match = re.fullmatch(r"(\^)?(.+?)(\$\$|\$)?", pattern.strip())
    if not match:
        raise ValueError(f"Invalid pattern format: {pattern!r}")

    prefix, body, suffix = match.groups()

    if debug:
        print(f"[pattern] prefix={prefix!r}, body={body!r}, suffix={suffix!r}")

    out: List[str] = []
    pos = 0

    # 2. Replace ${var} inside the body
    for m in _VAR_RE.finditer(body):
        var_name = m.group(1)
        prematch = body[pos : m.start()]

        # Normalize literal prematch
        out.append(_build_literal_regex(prematch, debug=debug))

        if var_name not in var_map:
            raise KeyError(f"Variable '{var_name}' not found in DSL variables.")

        var_regex = var_map[var_name]
        if debug:
            print(f"  [variable] {var_name} -> {var_regex!r}")

        out.append(var_regex)
        pos = m.end()

    # 3. Append tail (literal)
    tail = body[pos:]
    out.append(_build_literal_regex(tail, debug=debug))

    # 4. Reassemble prefix + substituted body + suffix
    final = ""
    if prefix:
        final += prefix
    final += "".join(out)
    if suffix:
        final += suffix

    # 5. Convert final $$ → $ (TextFSM escaping rule)
    if final.endswith("$$"):
        final = final[:-2] + "$"

    if debug:
        print(f"  [variable] final: {final!r}")

    return final


def _build_variable_map(dsl: DSLExtractorResult) -> Dict[str, str]:
    return {v["name"]: v["expression_regex"] for v in dsl.variables or []}


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
    dsl: Optional[DSLExtractorResult],
    template: Optional[str],
    sample: str,
    *,
    debug: bool = False,
):
    if dsl is None:
        if template is None:
            raise ValueError("Either 'dsl' or 'template' must be provided.")
        dsl = extract_machine_dsl(template)

    var_map = _build_variable_map(dsl)
    seen: List[str] = []
    out: List[str] = []

    all_debug = []

    for state in dsl.states or []:
        state_name = state.get("name", "<unknown>")

        debug_lst = []
        for trans in state.get("transitions", []):
            pattern = trans["pattern"] if isinstance(trans, dict) else trans

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

            debug_info: dict[str, str] = {}
            if debug:
                literal_trans = visualize_literal_transformation(matched_text, final)
                pat_matches = visualize_pattern_matches(final, sample, max_matches=2)
                debug_info.update(
                    literal_transformation=literal_trans, pattern_matches=pat_matches
                )
                debug_lst.append(debug_info)
                print(literal_trans)
                print(pat_matches)

            if final not in seen:
                seen.append(final)
                out.append(final)

        if debug_lst:
            all_debug.append({state_name: debug_lst})

    debug_msg = (
        json.dumps(all_debug, indent=2, sort_keys=True, ensure_ascii=False)
        if all_debug
        else ""
    )

    return "\n".join(out), debug_msg if debug else ""
