# tests/unit/core/test_dotdict.py

import pytest

from textfsm_ai.core.dotdict import DotDict


# ---------------------------------------------------------
# Construction / wrapping
# ---------------------------------------------------------
def test_construct_from_dict_wraps_nested_dict():
    dd = DotDict({"a": 1, "nested": {"b": 2}})

    assert isinstance(dd["nested"], DotDict)
    assert dd.nested.b == 2


def test_construct_from_dict_wraps_nested_list_of_dicts():
    dd = DotDict({"entries": [{"x": 1}, {"x": 2}, "plain"]})

    assert isinstance(dd.entries, list)
    assert isinstance(dd.entries[0], DotDict)
    assert dd.entries[0].x == 1
    assert dd.entries[1].x == 2
    assert dd.entries[2] == "plain"


def test_construct_from_kwargs():
    dd = DotDict(a=1, b=2)

    assert dd.a == 1
    assert dd.b == 2


def test_construct_empty():
    dd = DotDict()

    assert dict(dd) == {}


# ---------------------------------------------------------
# Dot access: __getattr__
# ---------------------------------------------------------
def test_getattr_returns_value_for_existing_key():
    dd = DotDict({"name": "leaf"})

    assert dd.name == "leaf"


def test_getattr_missing_key_raises_attribute_error():
    dd = DotDict({"name": "leaf"})

    with pytest.raises(AttributeError, match="No such attribute"):
        dd.missing


def test_getattr_trailing_underscore_accesses_shadowed_key():
    dd = DotDict({"update": "custom-value"})

    assert dd.update_ == "custom-value"


def test_getattr_trailing_underscore_missing_key_raises_attribute_error():
    dd = DotDict({"name": "leaf"})

    with pytest.raises(AttributeError, match="No such attribute"):
        dd.missing_


# ---------------------------------------------------------
# Dot access: __setattr__
# ---------------------------------------------------------
def test_setattr_sets_plain_value():
    dd = DotDict()
    dd.name = "leaf"

    assert dd["name"] == "leaf"
    assert dd.name == "leaf"


def test_setattr_wraps_nested_dict_value():
    dd = DotDict()
    dd.nested = {"x": 1}

    assert isinstance(dd["nested"], DotDict)
    assert dd.nested.x == 1


def test_setattr_trailing_underscore_sets_shadowed_key():
    dd = DotDict()
    dd.update_ = "custom-value"

    assert dd["update"] == "custom-value"


# ---------------------------------------------------------
# Dot access: __delattr__
# ---------------------------------------------------------
def test_delattr_removes_existing_key():
    dd = DotDict({"name": "leaf"})
    del dd.name

    assert "name" not in dd
    with pytest.raises(AttributeError):
        dd.name


def test_delattr_trailing_underscore_removes_shadowed_key():
    dd = DotDict({"update": "custom-value"})
    del dd.update_

    assert "update" not in dd


def test_delattr_missing_key_raises_attribute_error():
    dd = DotDict()

    with pytest.raises(AttributeError, match="No such attribute"):
        del dd.missing
