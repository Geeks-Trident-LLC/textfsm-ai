from typing import Optional

from .base import BaseNode
from .groups import KEYWORD_GROUP, WSS, KeywordGroup, base_keyword

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
        from .factory import create_node

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
        from .factory import create_node

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
        from .factory import create_node

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
        from .factory import create_node

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
        from .factory import create_node

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
