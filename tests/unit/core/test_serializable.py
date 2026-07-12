# tests/unit/core/test_serializable.py

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

import pytest

from textfsm_ai.core.serializable import Serializable, is_llm_response, to_dict


# ---------------------------------------------------------
# Fixtures: dataclasses built on top of Serializable
# ---------------------------------------------------------
class Color(Enum):
    RED = 1
    GREEN = 2


@dataclass
class Inner(Serializable):
    name: str
    color: Color


@dataclass
class Outer(Serializable):
    label: str
    inner: Inner
    tags: List[str] = field(default_factory=list)
    meta: Optional[dict] = None


class ChatCompletionLike:
    """Mimics an OpenAI v1 ChatCompletion object shape."""

    def __init__(
        self,
        choices,
        usage,
        id_="cmpl-1",
        object_="chat.completion",
        created=123,
        model="gpt-x",
    ):
        self.id = id_
        self.object = object_
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage


class Choice:
    def __init__(self, index, message, finish_reason):
        self.index = index
        self.message = message
        self.finish_reason = finish_reason


class BadChoice:
    """A choice entry whose attributes raise once accessed."""

    @property
    def index(self):
        raise RuntimeError("boom")


class BrokenChatCompletionLike:
    """Has choices/usage but raises while building the choices list."""

    def __init__(self):
        self.usage = {"total_tokens": 1}
        self.choices = [BadChoice()]

    def __repr__(self):
        return "<BrokenChatCompletionLike>"


class PydanticV2Like:
    def model_dump(self):
        return {"v2": True}


class PydanticV1Like:
    def dict(self):
        return {"v1": True}


class GenericToDictLike:
    def to_dict(self):
        return {"generic": True}


class Opaque:
    """No recognized conversion protocol at all."""

    def __repr__(self):
        return "<Opaque>"


# ---------------------------------------------------------
# Serializable.to_dict() / normalize()
# ---------------------------------------------------------
def test_to_dict_handles_enum_nested_dataclass_and_list():
    outer = Outer(
        label="root",
        inner=Inner(name="leaf", color=Color.GREEN),
        tags=["a", "b"],
        meta={"k": "v"},
    )

    d = outer.to_dict()

    assert d["label"] == "root"
    assert d["inner"] == {"name": "leaf", "color": "GREEN"}
    assert d["tags"] == ["a", "b"]
    assert d["meta"] == {"k": "v"}


def test_to_dict_normalizes_chat_completion_like_object():
    @dataclass
    class Wrapper(Serializable):
        response: object

    completion = ChatCompletionLike(
        choices=[Choice(0, {"role": "assistant", "content": "hi"}, "stop")],
        usage={"total_tokens": 5},
    )
    wrapper = Wrapper(response=completion)

    d = wrapper.to_dict()

    assert d["response"]["id"] == "cmpl-1"
    assert d["response"]["object"] == "chat.completion"
    assert d["response"]["created"] == 123
    assert d["response"]["model"] == "gpt-x"
    assert d["response"]["choices"] == [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "hi"},
            "finish_reason": "stop",
        }
    ]
    assert d["response"]["usage"] == {"total_tokens": 5}


def test_to_dict_chat_completion_like_exception_falls_back_to_str():
    @dataclass
    class Wrapper(Serializable):
        response: object

    wrapper = Wrapper(response=BrokenChatCompletionLike())

    d = wrapper.to_dict()

    assert d["response"] == "<BrokenChatCompletionLike>"


def test_to_dict_normalizes_opaque_object_via_str_fallback():
    @dataclass
    class Wrapper(Serializable):
        value: object

    wrapper = Wrapper(value=Opaque())

    d = wrapper.to_dict()

    assert d["value"] == "<Opaque>"


def test_to_dict_normalizes_list_with_unconvertible_items_via_fallback():
    @dataclass
    class Wrapper(Serializable):
        items: list

    wrapper = Wrapper(items=[Opaque(), "ok"])

    d = wrapper.to_dict()

    assert d["items"] == ["<Opaque>", "ok"]


def test_to_dict_normalizes_primitives_and_none():
    @dataclass
    class Wrapper(Serializable):
        a: object
        b: object
        c: object
        d: object
        e: object

    wrapper = Wrapper(a="str", b=1, c=1.5, d=True, e=None)

    result = wrapper.to_dict()

    assert result == {"a": "str", "b": 1, "c": 1.5, "d": True, "e": None}


# ---------------------------------------------------------
# to_dot_dict() / list()
# ---------------------------------------------------------
def test_to_dot_dict_allows_attribute_access():
    inner = Inner(name="leaf", color=Color.RED)

    dd = inner.to_dot_dict()

    assert dd.name == "leaf"
    assert dd.color == "RED"


def test_list_returns_field_names():
    inner = Inner(name="leaf", color=Color.RED)

    assert inner.list() == ["name", "color"]


def test_to_json_produces_sorted_indented_json():
    inner = Inner(name="leaf", color=Color.RED)

    text = inner.to_json()

    assert '"color": "RED"' in text
    assert '"name": "leaf"' in text
    assert text.index('"color"') < text.index('"name"')


# ---------------------------------------------------------
# from_dict()
# ---------------------------------------------------------
def test_from_dict_reconstructs_enum_and_nested_dataclass():
    data = {
        "label": "root",
        "inner": {"name": "leaf", "color": "GREEN"},
        "tags": ["x"],
        "meta": None,
    }

    outer = Outer.from_dict(data)

    assert outer.label == "root"
    assert isinstance(outer.inner, Inner)
    assert outer.inner.color is Color.GREEN
    assert outer.tags == ["x"]


def test_from_dict_plain_field_passthrough():
    data = {"name": "leaf", "color": "RED"}

    inner = Inner.from_dict(data)

    assert inner.name == "leaf"
    assert inner.color is Color.RED


# ---------------------------------------------------------
# module-level to_dict()
# ---------------------------------------------------------
def test_module_to_dict_primitive_passthrough():
    assert to_dict("s") == "s"
    assert to_dict(1) == 1
    assert to_dict(None) is None


def test_module_to_dict_dict_and_list_recursion():
    assert to_dict({"a": 1, "b": [1, 2]}) == {"a": 1, "b": [1, 2]}
    assert to_dict([1, "x", None]) == [1, "x", None]


def test_module_to_dict_pydantic_v2():
    assert to_dict(PydanticV2Like()) == {"v2": True}


def test_module_to_dict_pydantic_v1():
    assert to_dict(PydanticV1Like()) == {"v1": True}


def test_module_to_dict_generic_to_dict():
    assert to_dict(GenericToDictLike()) == {"generic": True}


def test_module_to_dict_unknown_type_raises_type_error():
    with pytest.raises(TypeError, match="Don't know how to convert"):
        to_dict(Opaque())


# ---------------------------------------------------------
# is_llm_response()
# ---------------------------------------------------------
def test_is_llm_response_false_for_dict_and_list():
    assert is_llm_response({"a": 1}) is False
    assert is_llm_response([1, 2]) is False


def test_is_llm_response_true_for_pydantic_v2():
    assert is_llm_response(PydanticV2Like()) is True


def test_is_llm_response_true_for_pydantic_v1():
    assert is_llm_response(PydanticV1Like()) is True


def test_is_llm_response_true_for_generic_to_dict():
    assert is_llm_response(GenericToDictLike()) is True


def test_is_llm_response_false_for_opaque_object():
    assert is_llm_response(Opaque()) is False
