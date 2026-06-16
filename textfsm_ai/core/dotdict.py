class DotDict(dict):
    """
    A safe, predictable dot-access dictionary.

    Features:
      - dot access for valid identifiers
      - trailing underscore to access keys that shadow dict attributes
      - recursive wrapping of dicts and lists
      - no recursion risk
      - no mutation during iteration
    """

    __slots__ = ()

    # ----------------------------
    # Construction
    # ----------------------------
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.update(*args, **kwargs)

    # ----------------------------
    # Internal wrapping
    # ----------------------------
    @staticmethod
    def _wrap(value):
        if isinstance(value, dict):
            return DotDict(value)
        if isinstance(value, list):
            return [DotDict._wrap(v) for v in value]
        return value

    # ----------------------------
    # Override update
    # ----------------------------
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            super().__setitem__(k, self._wrap(v))

    # ----------------------------
    # Dot access
    # ----------------------------
    def __getattr__(self, name):
        # shadowing: foo_ → key "foo"
        key = name[:-1] if name.endswith("_") else name

        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"No such attribute: {name!r}")

    def __setattr__(self, name, value):
        key = name[:-1] if name.endswith("_") else name
        super().__setitem__(key, self._wrap(value))

    def __delattr__(self, name):
        key = name[:-1] if name.endswith("_") else name
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"No such attribute: {name!r}")
