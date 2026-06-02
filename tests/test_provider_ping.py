from textfsm_ai.provider_ping import PING_MAP


def test_ping_map_contains_all_providers():
    assert set(PING_MAP.keys()) == {"openai", "anthropic", "gemini", "deepseek"}
