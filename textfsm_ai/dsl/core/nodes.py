import re
from enum import Enum, auto
from typing import Optional

# from textfsm_ai.dsl.expression import keyword_expression_from
from textfsm_ai.dsl.core.patterns import PATTERNS

# ------------------------------------------------------------
# Keyword semantic groups
# ------------------------------------------------------------

WS = r"\s"
WSS = r"\s+"


class KeywordGroup(Enum):
    ATOMIC = auto()  # digit, letter, alnum, punct, non-ws
    ATOMIC_PLUS = auto()  # digits, puncts, non-wss
    WORDLIKE = auto()  # word, mixed-word, number, mixed-number
    ITEM = auto()  # words, word-item, puncts-item, etc.
    GROUP = auto()  # word-group, mixed-word-group, puncts-group, etc.


CUSTOM_KEYWORD_MAPPING = {
    "char": ".",
    "any": ".*",
    "some": ".+",
    "ws": WS,
    "wss": WSS,
    "whitespace": WS,
    "whitespaces": WSS,
}

KEYWORD_GROUP = {
    # -------------------------
    # atomic-group
    # -------------------------
    "digit": KeywordGroup.ATOMIC,
    "letter": KeywordGroup.ATOMIC,
    "alnum": KeywordGroup.ATOMIC,
    "punct": KeywordGroup.ATOMIC,
    "non-ws": KeywordGroup.ATOMIC,
    "char": KeywordGroup.ATOMIC,
    "ws": KeywordGroup.ATOMIC,
    "whitespace": KeywordGroup.ATOMIC,
    # -------------------------
    # atomic-plus-group
    # -------------------------
    "digits": KeywordGroup.ATOMIC_PLUS,
    "puncts": KeywordGroup.ATOMIC_PLUS,
    "non-wss": KeywordGroup.ATOMIC_PLUS,
    "any": KeywordGroup.ATOMIC_PLUS,
    "some": KeywordGroup.ATOMIC_PLUS,
    "wss": KeywordGroup.ATOMIC_PLUS,
    "whitespaces": KeywordGroup.ATOMIC_PLUS,
    # -------------------------
    # word-like-group
    # -------------------------
    "word": KeywordGroup.WORDLIKE,
    "mixed-word": KeywordGroup.WORDLIKE,
    "number": KeywordGroup.WORDLIKE,
    "mixed-number": KeywordGroup.WORDLIKE,
    # -------------------------
    # item-group
    # <base>(<wss><base>)*
    # -------------------------
    "words": KeywordGroup.ITEM,
    "mixed-words": KeywordGroup.ITEM,
    "numbers": KeywordGroup.ITEM,
    "mixed-numbers": KeywordGroup.ITEM,
    "word-item": KeywordGroup.ITEM,
    "mixed-word-item": KeywordGroup.ITEM,
    "number-item": KeywordGroup.ITEM,
    "mixed-number-item": KeywordGroup.ITEM,
    "puncts-item": KeywordGroup.ITEM,
    "non-wss-item": KeywordGroup.ITEM,
    # -------------------------
    # group-group
    # <base>(<wss><base>)+
    # -------------------------
    "word-group": KeywordGroup.GROUP,
    "mixed-word-group": KeywordGroup.GROUP,
    "number-group": KeywordGroup.GROUP,
    "mixed-number-group": KeywordGroup.GROUP,
    "puncts-group": KeywordGroup.GROUP,
    "non-wss-group": KeywordGroup.GROUP,
}


def keyword_group(name: str) -> KeywordGroup:
    return KEYWORD_GROUP.get(name, KeywordGroup.WORDLIKE)


def base_keyword(name: str) -> str:
    if name.endswith("-group"):
        return name[:-6]  # remove "-group"
    if name.endswith("-item"):
        return name[:-5]  # remove "-item"

    mapping = {
        "words": "word",
        "mixed-words": "mixed-word",
        "numbers": "number",
        "mixed-numbers": "mixed-number",
    }

    return mapping.get(name, name)


# ------------------------------------------------------------
# Base Node
# ------------------------------------------------------------


class BaseNode:
    name: str

    def to_regex(self, include_var: bool = False) -> str:
        raise NotImplementedError

    def to_expression(self) -> str:
        raise NotImplementedError

    def to_expression_regex(self) -> str:
        return self.to_regex(include_var=False)

    # def as_keyword_expression(self):
    #     return keyword_expression_from(self.to_expression())

    def __str__(self):
        return self.to_expression()


# ------------------------------------------------------------
# Literal
# ------------------------------------------------------------


class LiteralNode(BaseNode):
    def __init__(self, text: str):
        self.text = text
        self.name = "literal"
        self.regex = re.escape(self.text)

    def to_regex(self, include_var=False):
        return self.regex

    def to_expression(self):
        return self.text


# ------------------------------------------------------------
# Keyword
# ------------------------------------------------------------


class KeywordNode(BaseNode):
    def __init__(self, keyword: str, generalize: bool = False):
        self.keyword = keyword
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = PATTERNS[self.name].regex

    def _generalized_keyword(self):
        if not self.generalize:
            return self.keyword

        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"

        return self.keyword

    def to_regex(self, include_var=False):
        return self.regex

    def to_expression(self):
        return f"{self.name}()"


# ------------------------------------------------------------
# Variable Keyword
# ------------------------------------------------------------


class VariableKeywordNode(BaseNode):
    def __init__(self, keyword: str, varname: str, generalize: bool = False):
        self.keyword = keyword
        self.varname = varname
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = PATTERNS[self.name].regex

    def _generalized_keyword(self):
        if not self.generalize:
            return self.keyword

        if self.keyword == "digit":
            return "digits"
        if self.keyword == "letter":
            return "word"
        if self.keyword == "punct":
            return "puncts"

        return self.keyword

    def to_regex(self, include_var=False):
        if include_var:
            return f"(?P<{self.varname}>{self.regex})"
        return self.regex

    def to_expression(self):
        return f"{self.name}(var-{self.varname})"

    def to_expression_regex(self):
        return self.regex


def check_custom_keyword(keyword):
    return keyword in CUSTOM_KEYWORD_MAPPING


class CustomKeywordNode(BaseNode):
    def __init__(
        self, keyword: str, varname: Optional[str] = None, generalize: bool = False
    ):
        if not check_custom_keyword(keyword):
            custom_keywords = list(CUSTOM_KEYWORD_MAPPING)
            raise ValueError(
                f"Unknown custom keyword: {keyword}.  Must be {custom_keywords}"
            )
        self.keyword = keyword
        self.varname = varname
        self.generalize = generalize
        self.name = self._generalized_keyword()
        self.regex = CUSTOM_KEYWORD_MAPPING[self.name]

    def _generalized_keyword(self):
        if not self.generalize:
            return self.keyword

        if self.keyword == "char":
            return "any"
        if self.keyword == "ws":
            return "wss"
        if self.keyword == "whitespace":
            return "whitespaces"

        return self.keyword

    def to_regex(self, include_var=False):
        if self.varname and include_var:
            return f"(?P<{self.varname}>{self.regex})"
        return self.regex

    def to_expression(self):
        if self.varname:
            return f"{self.name}(var-{self.varname})"
        return f"{self.name}()"

    def to_expression_regex(self):
        return self.regex


# ------------------------------------------------------------
# Optional
# ------------------------------------------------------------


class OptionalNode(BaseNode):
    def __init__(self, keyword_node: BaseNode):
        self.keyword_node = keyword_node
        self.name = f"optional-{keyword_node.name}"

    def to_regex(self, include_var=False):
        base = self.keyword_node.to_regex(include_var)
        g = keyword_group(self.keyword_node.name)

        if g == KeywordGroup.ATOMIC:
            return f"{base}?"

        if g == KeywordGroup.ATOMIC_PLUS:
            return f"{base[:-1]}*"

        return f"(?:{base})?"

    def to_expression(self):
        return f"optional-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# Maybe (alias for optional)
# ------------------------------------------------------------


class MaybeNode(OptionalNode):
    def __init__(self, keyword_node: BaseNode):
        super().__init__(keyword_node)
        self.name = f"maybe-{keyword_node.name}"

    def to_expression(self):
        return f"maybe-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# Negative Lookahead
# ------------------------------------------------------------


class NotNode(BaseNode):
    def __init__(self, keyword_node: BaseNode):
        self.keyword_node = keyword_node
        self.name = f"not-{keyword_node.name}"

    def to_regex(self, include_var=False):
        return f"(?!{self.keyword_node.to_regex(include_var)})"

    def to_expression(self):
        return f"not-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# Zero-or-more
# ------------------------------------------------------------


class ZeroOrMoreNode(BaseNode):
    """
    ZeroOrMoreNode = zero-or-more of the underlying keyword node,
    following the DSL semantics for each keyword group.
    """

    def __init__(self, keyword_node):
        self.keyword_node = keyword_node
        self.group = KEYWORD_GROUP[keyword_node.keyword]

    def to_regex(self, include_var=False) -> str:
        base = self.keyword_node.to_regex(include_var=include_var)

        if self.group == KeywordGroup.ATOMIC:
            return f"{base}*"

        if self.group == KeywordGroup.ATOMIC_PLUS:
            if base.endswith("+"):
                base = base[:-1]
            return f"{base}*"

        # -----------------------------------------
        # word-like-group => normalize to <base-item>
        # <base-item> = <base>(<wss><base>)*
        # then apply '*'
        # -----------------------------------------
        if self.group == KeywordGroup.WORDLIKE:
            item_node = create_node(f"{self.keyword_node.keyword}-item")
            item_regex = item_node.to_regex(include_var=include_var)
            return f"(?:{item_regex})*"

        if self.group == KeywordGroup.ITEM:
            return f"(?:{base})*"

        if self.group == KeywordGroup.GROUP:
            return f"(?:{base})*"

        raise ValueError(f"Unknown keyword group: {self.group}")

    def to_expression(self):
        return f"zero_or_more-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# One-or-more
# ------------------------------------------------------------


class OneOrMoreNode(BaseNode):
    """
    OneOrMoreNode = one-or-more of the underlying keyword node,
    following the DSL semantics for each keyword group.
    """

    def __init__(self, keyword_node):
        self.keyword_node = keyword_node
        self.group = KEYWORD_GROUP[keyword_node.keyword]

    def to_regex(self, include_var=False) -> str:
        base = self.keyword_node.to_regex(include_var=include_var)

        if self.group == KeywordGroup.ATOMIC:
            return f"{base}+"

        if self.group == KeywordGroup.ATOMIC_PLUS:
            return base

        # -----------------------------------------
        # word-like-group => normalize to <base-item>
        # <base-item> = <base>(<wss><base>)*
        # -----------------------------------------
        if self.group == KeywordGroup.WORDLIKE:
            item_node = create_node(f"{self.keyword_node.keyword}-item")
            return item_node.to_regex(include_var=include_var)

        if self.group in [KeywordGroup.ITEM, KeywordGroup.GROUP]:
            return base

        raise ValueError(f"Unknown keyword group: {self.group}")

    def to_expression(self):
        return f"one_or_more-{self.keyword_node.to_expression()}"


class AnyNode(BaseNode):
    """
    AnyNode wraps another keyword node and converts it into an optional
    or zero-or-more form depending on the keyword group classification.
    """

    def __init__(self, keyword_node):
        self.keyword_node = keyword_node
        self.group = KEYWORD_GROUP[keyword_node.keyword]

    def to_regex(self, include_var=False) -> str:
        base = self.keyword_node.to_regex(include_var=include_var)

        # -----------------------------
        # atomic-group => <base>?
        # -----------------------------
        if self.group == KeywordGroup.ATOMIC:
            return f"{base}?"

        if self.group == KeywordGroup.ATOMIC_PLUS:
            if base.endswith("+"):
                base = base[:-1]
            return f"{base}*"

        if self.group in [KeywordGroup.WORDLIKE, KeywordGroup.ITEM, KeywordGroup.GROUP]:
            return f"(?:{base})?"

        raise ValueError(f"Unknown keyword group: {self.group}")

    def to_expression(self):
        return f"any-{self.keyword_node.to_expression()}"


class SomeNode(BaseNode):
    """
    SomeNode = one-or-more of the underlying keyword node,
    following the DSL semantics for each keyword group.
    """

    def __init__(self, keyword_node):
        self.keyword_node = keyword_node
        self.group = KEYWORD_GROUP[keyword_node.keyword]

    def to_regex(self, include_var=False) -> str:
        base = self.keyword_node.to_regex(include_var=include_var)

        # -----------------------------------------
        # atomic-group => <base>+
        # -----------------------------------------
        if self.group == KeywordGroup.ATOMIC:
            return f"{base}+"

        # -----------------------------------------
        # atomic-plus-group => <base>
        # (already means one-or-more)
        # -----------------------------------------
        if self.group == KeywordGroup.ATOMIC_PLUS:
            return base

        # -----------------------------------------
        # word-like-group => normalize to <base-item>
        # <base-item> = <base>(<wss><base>)*
        # -----------------------------------------
        if self.group == KeywordGroup.WORDLIKE:
            item_node = create_node(f"{self.keyword_node.keyword}-item")
            return item_node.to_regex(include_var=include_var)

        # -----------------------------------------
        # item-group => <item-regex>
        # <item-regex> = <base>(<wss><base>)*
        # BUT: KeywordNode for item-group already returns correct regex
        # -----------------------------------------
        if self.group in [KeywordGroup.ITEM, KeywordGroup.GROUP]:
            return base

        raise ValueError(f"Unknown keyword group: {self.group}")

    def to_expression(self):
        return f"some-{self.keyword_node.to_expression()}"


class ExactCountNode(BaseNode):
    """
    ExactCountNode = exact N occurrences of the underlying keyword node,
    following DSL semantics for each keyword group.
    """

    def __init__(self, keyword_node, count):
        self.keyword_node = keyword_node
        self.count = count
        self.group = KEYWORD_GROUP[keyword_node.keyword]

    def _base_token_regex(self, include_var):
        """
        Extract the underlying single-token regex.
        word-item  -> word
        word-group -> word
        number-item -> number
        etc.
        """
        base_kw = base_keyword(self.keyword_node.name)
        node = create_node(
            base_kw,
            varname=getattr(self.keyword_node, "varname", None),
            generalize=self.keyword_node.generalize,
        )
        return node.to_regex(include_var=include_var)

    def to_regex(self, include_var=False):
        n = self.count
        full = self.keyword_node.to_regex(include_var=include_var)

        # ------------------------------------------------------------
        # count == 0 → empty string
        # ------------------------------------------------------------
        if n == 0:
            return ""

        # ------------------------------------------------------------
        # count == 1
        # ------------------------------------------------------------
        if n == 1:
            if self.group == KeywordGroup.ATOMIC:
                return full

            if self.group == KeywordGroup.ATOMIC_PLUS:
                if not full.endswith("+"):
                    raise ValueError("atomic-plus regex must end with '+'")
                return full[:-1]

            if self.group == KeywordGroup.WORDLIKE:
                return full  # already a single token

            if self.group == KeywordGroup.ITEM:
                return self._base_token_regex(include_var)

            if self.group == KeywordGroup.GROUP:
                return full  # one phrase

            raise ValueError(f"Unknown keyword group: {self.group}")

        # ------------------------------------------------------------
        # count > 1
        # ------------------------------------------------------------

        # atomic-group → <base>{n}
        if self.group == KeywordGroup.ATOMIC:
            return f"{full}{{{n}}}"

        # atomic-plus-group → strip '+' then {n}
        if self.group == KeywordGroup.ATOMIC_PLUS:
            if not full.endswith("+"):
                raise ValueError("atomic-plus regex must end with '+'")
            atom = full[:-1]
            return f"{atom}{{{n}}}"

        # word-like-group → base_token (wss base_token){n-1}
        if self.group == KeywordGroup.WORDLIKE:
            base = self._base_token_regex(include_var)
            return f"{base}(?:{WSS}{base}){{{n - 1}}}"

        # item-group → base_token (wss base_token){n-1}
        if self.group == KeywordGroup.ITEM:
            base = self._base_token_regex(include_var)
            return f"{base}(?:{WSS}{base}){{{n - 1}}}"

        # group-group → phrase (wss phrase){n-1}
        if self.group == KeywordGroup.GROUP:
            phrase = full  # <base>(<wss><base>)+
            return f"{phrase}(?:{WSS}{phrase}){{{n - 1}}}"

        raise ValueError(f"Unknown keyword group: {self.group}")

    def to_expression(self):
        return f"exact-{self.count}-{self.keyword_node.to_expression()}"


class RangeQuantityNode(BaseNode):
    """
    RangeQuantityNode = match between lo and hi occurrences of the underlying
    keyword node, following DSL semantics for each keyword group.

    - lo: int >= 0
    - hi: int >= lo, or None for INF
    - keyword_node: the underlying keyword node (word, word-item, word-group,
      digit, digits, ...)
    """

    def __init__(self, keyword_node, lo: int, hi: Optional[int]):
        self.keyword_node = keyword_node
        self.lo = lo
        self.hi = hi  # None means INF
        self.group = KEYWORD_GROUP[keyword_node.keyword]

    # ---------- helpers ----------

    def _base_token_regex(self, include_var: bool) -> str:
        """
        Extract the underlying single-token regex.

        word-item       -> word
        word-group      -> word
        number-item     -> number
        mixed-word-item -> mixed-word
        etc.
        """

        base_kw = base_keyword(self.keyword_node.name)
        node = create_node(
            base_kw,
            varname=getattr(self.keyword_node, "varname", None),
            generalize=self.keyword_node.generalize,
        )
        return node.to_regex(include_var=include_var)

    def _phrase_regex(self, include_var: bool) -> str:
        """
        Phrase unit for group-group (e.g. word-group):
        keyword_node.to_regex() already returns:
            WORD (?:WSS WORD)+
        We treat that as a single PHRASE unit.
        """
        return self.keyword_node.to_regex(include_var=include_var)

    # ---------- main ----------

    def to_regex(self, include_var: bool = False) -> str:
        lo = self.lo
        hi = self.hi  # None means INF
        full = self.keyword_node.to_regex(include_var=include_var)

        # ------------------------------------------------------------
        # lo == hi == 0 → empty
        # ------------------------------------------------------------
        if lo == 0 and hi == 0:
            return ""

        # ------------------------------------------------------------
        # lo == hi != 0 → exact count
        # ------------------------------------------------------------
        if hi is not None and lo == hi and lo > 0:
            return ExactCountNode(self.keyword_node, lo).to_regex(
                include_var=include_var
            )

        # ------------------------------------------------------------
        # atomic / atomic-plus are simple quantifiers
        # ------------------------------------------------------------
        if self.group in (KeywordGroup.ATOMIC, KeywordGroup.ATOMIC_PLUS):
            if self.group == KeywordGroup.ATOMIC_PLUS:
                if not full.endswith("+"):
                    raise ValueError("atomic-plus regex must end with '+'")
                base = full[:-1]
            else:
                base = full

            if hi is None:
                # lo..INF
                return f"{base}{{{lo},}}"
            else:
                # lo..hi
                return f"{base}{{{lo},{hi}}}"

        # ------------------------------------------------------------
        # word-like / item-group → unit = WORD
        # ------------------------------------------------------------
        if self.group in (KeywordGroup.WORDLIKE, KeywordGroup.ITEM):
            base = self._base_token_regex(include_var)  # WORD

            # lo == 0
            if lo == 0:
                if hi is None:
                    # 0..INF words → optional sequence of words
                    # WORD (WSS WORD)* is "one or more words"
                    # 0..INF → optional
                    return f"(?:{base}(?:{WSS}{base})*)?"
                else:
                    # 0..hi words
                    # 0 words OR 1..hi words
                    # 1..hi words = base (WSS base){0,hi-1}
                    # wrap as optional
                    return f"(?:{base}(?:{WSS}{base}){{0,{hi - 1}}})?"
            else:
                # lo > 0
                if hi is None:
                    # lo..INF words
                    # base (WSS base){lo-1,}
                    return f"{base}(?:{WSS}{base}){{{lo - 1},}}"
                else:
                    # lo..hi words
                    # base (WSS base){lo-1,hi-1}
                    return f"{base}(?:{WSS}{base}){{{lo - 1},{hi - 1}}}"

        # ------------------------------------------------------------
        # group-group → unit = PHRASE (≥2 words)
        # PHRASE = WORD (WSS WORD)+
        # ------------------------------------------------------------
        if self.group == KeywordGroup.GROUP:
            phrase = self._phrase_regex(include_var)

            # lo == 0
            if lo == 0:
                if hi is None:
                    # 0..INF phrases → optional sequence of phrases
                    # PHRASE (WSS PHRASE)* is "one or more phrases"
                    # 0..INF → optional
                    return f"(?:{phrase}(?:{WSS}{phrase})*)?"
                else:
                    # 0..hi phrases
                    # 0 phrases OR 1..hi phrases
                    # 1..hi phrases = phrase (WSS phrase){0,hi-1}
                    return f"(?:{phrase}(?:{WSS}{phrase}){{0,{hi - 1}}})?"
            else:
                # lo > 0
                if hi is None:
                    # lo..INF phrases
                    # phrase (WSS phrase){lo-1,}
                    return f"{phrase}(?:{WSS}{phrase}){{{lo - 1},}}"
                else:
                    # lo..hi phrases
                    # phrase (WSS phrase){lo-1,hi-1}
                    return f"{phrase}(?:{WSS}{phrase}){{{lo - 1},{hi - 1}}}"

        raise ValueError(f"Unknown keyword group: {self.group}")

    def to_expression(self):
        if self.hi is None:
            return f"range-{self.lo}-inf-{self.keyword_node.to_expression()}"
        return f"range-{self.lo}-{self.hi}-{self.keyword_node.to_expression()}"


# ------------------------------------------------------------
# Node Factory
# ------------------------------------------------------------


def create_node(
    keyword: str,
    varname: Optional[str] = None,
    generalize: bool = False,
    literal: bool = False,
) -> BaseNode:
    if literal:
        return LiteralNode(keyword)

    if check_custom_keyword(keyword):
        return CustomKeywordNode(keyword, varname=varname, generalize=generalize)

    # ------------------------------------------------------------
    # range-lo-hi-keyword
    # range-lo-inf-keyword
    # ------------------------------------------------------------
    if keyword.startswith("range-"):
        # pattern: range-<lo>-<hi>-<keyword>
        m = re.match(r"range-(\d+)-(inf|\d+)-(.+)", keyword)
        if not m:
            raise ValueError(f"Invalid range syntax: {keyword}")

        lo = int(m.group(1))
        hi_raw = m.group(2)
        hi = None if hi_raw == "inf" else int(hi_raw)
        inner_kw = m.group(3)

        inner_node = create_node(inner_kw, varname, generalize)
        return RangeQuantityNode(inner_node, lo, hi)

    # ------------------------------------------------------------
    # exact-n-keyword
    # ------------------------------------------------------------
    if keyword.startswith("exact-"):
        # pattern: exact-<n>-<keyword>
        m = re.match(r"exact-(\d+)-(.+)", keyword)
        if not m:
            raise ValueError(f"Invalid exact syntax: {keyword}")

        count = int(m.group(1))
        inner_kw = m.group(2)

        inner_node = create_node(inner_kw, varname, generalize)
        return ExactCountNode(inner_node, count)

    # ------------------------------------------------------------
    # any-<keyword>  → zero-or-more
    # ------------------------------------------------------------
    if keyword.startswith("any-"):
        inner_kw = keyword[len("any-") :]
        return ZeroOrMoreNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # some-<keyword> → one-or-more
    # ------------------------------------------------------------
    if keyword.startswith("some-"):
        inner_kw = keyword[len("some-") :]
        return OneOrMoreNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # maybe-<keyword> → optional
    # ------------------------------------------------------------
    if keyword.startswith("maybe-"):
        inner_kw = keyword[len("maybe-") :]
        return OptionalNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # optional-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("optional-"):
        inner_kw = keyword[len("optional-") :]
        return OptionalNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # zero-or-more-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("zero-or-more-"):
        inner_kw = keyword[len("zero-or-more-") :]
        return ZeroOrMoreNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # one-or-more-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("one-or-more-"):
        inner_kw = keyword[len("one-or-more-") :]
        return OneOrMoreNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # not-<keyword>
    # ------------------------------------------------------------
    if keyword.startswith("not-"):
        inner_kw = keyword[len("not-") :]
        return NotNode(create_node(inner_kw, varname, generalize))

    # ------------------------------------------------------------
    # variable keyword
    # ------------------------------------------------------------
    if varname is not None:
        return VariableKeywordNode(keyword, varname, generalize)

    # ------------------------------------------------------------
    # plain keyword
    # ------------------------------------------------------------
    return KeywordNode(keyword, generalize)
