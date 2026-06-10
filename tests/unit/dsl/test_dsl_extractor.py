from textfsm_ai.dsl.dsl_extractor import extract_machine_dsl


def test_extract_machine_dsl_basic():
    template = """Value interface ([!-~]*[0-9A-Za-z][!-~]*)
Value mtu ([0-9]+)

Start
  ^interface\\s+${interface} -> Continue.Record
  ^\\s+mtu\\s+${mtu}
"""

    dsl = extract_machine_dsl(template)

    vars = dsl["variables"]
    states = dsl["states"]

    # variable ordering preserved
    assert vars[0]["name"] == "interface"
    assert vars[1]["name"] == "mtu"

    # options default to ""
    assert vars[0]["options"] == ""
    assert vars[1]["options"] == ""

    # expression field
    assert vars[0]["expression"] == "mixed-word(var-interface)"
    assert vars[1]["expression"] == "digits(var-mtu)"

    # state ordering preserved
    assert states[0]["name"] == "Start"

    # transitions preserved
    assert states[0]["transitions"][0]["pattern"].startswith("^interface")
    assert states[0]["transitions"][0]["action"] == "Continue.Record"
    assert states[0]["transitions"][1]["pattern"].startswith("^\\s+mtu")
    assert states[0]["transitions"][1]["action"] is None
