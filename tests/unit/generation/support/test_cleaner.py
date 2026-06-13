# tests/unit/generation/support/test_cleaner.py

from textfsm_ai.generation.support.cleaner import clean_template, validate_template


def test_fast_path_valid_template():
    template = """
Value NAME (\\S+)

Start
  ^${NAME} -> Record
"""
    cleaned = clean_template(template)
    assert validate_template(cleaned)
    assert "Start" in cleaned


def test_drift_cleanup_removes_invalid_state():
    template = """
Value NAME (\\S+)

Start
  ^foo -> Record

BogusState
"""
    cleaned = clean_template(template)
    assert "BogusState" not in cleaned
    assert validate_template(cleaned)


def test_full_cleanup_fixes_missing_start():
    template = """
Value NAME (\\S+)
  ^foo -> Record
"""
    cleaned = clean_template(template)
    assert "Start" in cleaned
    assert validate_template(cleaned)


def test_action_normalization():
    template = """
Value NAME (\\S+)

Start
  ^foo -> next.record
"""
    cleaned = clean_template(template)
    assert "Next.Record" in cleaned
    assert validate_template(cleaned)


def test_value_normalization():
    template = """
Value required,list NAME (\\S+)

Start
  ^foo -> Record
"""
    cleaned = clean_template(template)
    assert "Value Required,List name" in cleaned
    assert validate_template(cleaned)


def test_idempotency():
    template = """
Value NAME (\\S+)

Start
  ^foo -> Record
"""
    cleaned1 = clean_template(template)
    cleaned2 = clean_template(cleaned1)
    assert cleaned1 == cleaned2


def test_round_trip_stability():
    template = """
Value NAME (\\S+)

Start
  ^foo -> Record
"""
    cleaned = clean_template(template)
    assert validate_template(cleaned)
    assert "Value NAME" in cleaned
