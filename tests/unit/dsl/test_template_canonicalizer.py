# tests/unit/dsl/test_template_canonicalizer.py

from textfsm_ai.dsl.patterns import PATTERNS
from textfsm_ai.dsl.template_canonicalizer import TemplateCanonicalizer


def test_single_variable_mixed_word():
    template = """Value interface (\\S+)

Start
  ^interface\\s+${interface} -> Record
"""

    records = [
        {"interface": "GigE1.0.1"},
        {"interface": "GigE1.0/2"},
    ]

    canon = TemplateCanonicalizer()
    out = canon.canonicalize(template, records)

    expected_regex = PATTERNS["mixed-word"].regex

    assert f"Value interface ({expected_regex})" in out
    assert "^interface\\s+${interface}" in out


def test_multi_variable():
    template = """Value interface (\\S+)
Value mtu (\\S+)

Start
  ^interface\\s+${interface} -> Continue.Record
  ^\\s+mtu\\s+${mtu}
"""

    records = [
        {"interface": "GigE1.0.1", "mtu": "1500"},
        {"interface": "GigE1.0/2", "mtu": "9000"},
    ]

    canon = TemplateCanonicalizer()
    out = canon.canonicalize(template, records)

    iface_regex = PATTERNS["mixed-word"].regex
    mtu_regex = PATTERNS["digits"].regex

    assert f"Value interface ({iface_regex})" in out
    assert f"Value mtu ({mtu_regex})" in out


def test_multi_line_block_preserved():
    template = """Value name (\\S+)
Value speed (\\S+)

Start
  ^interface\\s+${name} -> Continue.Record
  ^\\s+speed\\s+${speed}
  ^\\s+duplex\\s+auto
"""

    records = [
        {"name": "Eth1/1", "speed": "1000"},
        {"name": "Eth1/2", "speed": "10000"},
    ]

    canon = TemplateCanonicalizer()
    out = canon.canonicalize(template, records)

    name_regex = PATTERNS["mixed-word"].regex
    speed_regex = PATTERNS["digits"].regex

    assert f"Value name ({name_regex})" in out
    assert f"Value speed ({speed_regex})" in out

    # ensure non-Value lines are untouched
    assert "duplex\\s+auto" in out


def test_group_patterns():
    template = """Value desc (.+)

Start
  ^description\\s+${desc} -> Record
"""

    records = [
        {"desc": "Uplink to core"},
        {"desc": "Downlink to agg"},
    ]

    canon = TemplateCanonicalizer()
    out = canon.canonicalize(template, records)

    # desc contains multiple words → DSL should infer "words"
    desc_regex = PATTERNS["word-group"].regex

    assert f"Value desc ({desc_regex})" in out
