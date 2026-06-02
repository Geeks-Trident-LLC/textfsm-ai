from textfsm_ai.ai_router import AIRouter


class DummyProvider:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def send(self, prompt, model=None, lang="en", **kwargs):
        return f"dummy:{prompt}:{model}:{lang}"


def test_router_calls_correct_provider():
    # Create an uninitialized AIRouter instance
    r = AIRouter.__new__(AIRouter)

    # Inject dummy provider class
    r._provider_classes = {"openai": DummyProvider}
    r._providers = {}

    out = r.ask(
        "hello",
        provider="openai",
        model="gpt-test",
        api_key="abc123",
        lang="en",
    )

    assert out == "dummy:hello:gpt-test:en"
