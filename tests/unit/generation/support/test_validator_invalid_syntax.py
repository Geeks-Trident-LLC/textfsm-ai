# tests/unit/generation/support/test_validator_invalid_syntax.py


from textfsm_ai.generation.support.validator import check_illegal_dollar


def run(lines):
    """Helper to run validator and return findings."""
    return check_illegal_dollar(lines)


def test_illegal_dollar_simple_cases():
    lines = [
        "^invalid case 1 - abc xyz$",
        "^invalid case 2 - abc xyz $",
        "^invalid case 3 - abc x$yz",
    ]
    findings = run(lines)

    assert len(findings) == 3
    assert all("illegal_dollar" in f for f in findings)


def test_illegal_dollar_variable_suffix_cases():
    lines = [
        "^invalid case 4 - name:\\s+${name}$",
        "^invalid case 5 - name:\\s+${name} $",
        "^invalid case 6 - name:\\s+${name} a$b",
    ]
    findings = run(lines)

    assert len(findings) == 3
    assert all("illegal_dollar" in f for f in findings)


def test_illegal_dollar_double_dollar_not_at_end():
    lines = [
        "^invalid case 7 - abc $$ xyz",
        "^invalid case 8 - name:\\s+$$\\s+${name}",
    ]
    findings = run(lines)

    # Both should be flagged because $$ is only valid at end-of-line
    assert len(findings) == 2
    assert all("illegal_double_dollar" in f for f in findings)


def test_valid_dollar_patterns_are_not_flagged():
    lines = [
        r"^valid literal dollar: price is \$5",  # literal dollar
        r"^valid end anchor $$",  # $$ at end
        r"^valid variable ${name}",  # variable
        r"^valid variable with regex ${name}",  # variable with regex
        r"^no dollar here",  # no dollar
    ]
    findings = run(lines)

    assert findings == []


def test_illegal_var_regex_pattern():
    lines = [r"^foo ${name:\d+}"]
    findings = run(lines)

    assert any("illegal_var_regex" in f for f in findings)


def test_mixed_valid_and_invalid():
    lines = [
        r"^ok1 ${var}",  # valid
        r"^bad1 abc$x",  # invalid
        r"^ok2 price is \$10",  # valid
        r"^bad2 ${name}$",  # invalid
    ]
    findings = run(lines)

    assert len(findings) == 2
    assert "bad1" in findings[0]
    assert "bad2" in findings[1]
