from textfsm_ai.ai_router import MultiProviderRouter


class DummyProvider:
    def __init__(self, name, should_fail=False):
        self.name = name
        self.should_fail = should_fail

    def generate(self, prompt):
        if self.should_fail:
            raise RuntimeError(f"{self.name} failed")
        return f"{self.name} ok"


def test_router_fallback():
    router = MultiProviderRouter.__new__(MultiProviderRouter)

    router.gemini = DummyProvider("gemini", should_fail=True)
    router.deepseek = DummyProvider("deepseek", should_fail=True)
    router.openai = DummyProvider("openai", should_fail=False)
    router.claude = DummyProvider("claude", should_fail=False)

    router.providers = [
        router.gemini,
        router.deepseek,
        router.openai,
        router.claude,
    ]

    out = router.generate("hello")
    assert out == "openai ok"
