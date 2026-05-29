from unittest.mock import patch, MagicMock

from textfsm_ai.providers.openai_provider import OpenAIProvider
from textfsm_ai.providers.claude_provider import ClaudeProvider
from textfsm_ai.providers.gemini_provider import GeminiProvider
from textfsm_ai.providers.deepseek_provider import DeepSeekProvider


# --- Helper: mock response ---
def mock_response(text):
    m = MagicMock()
    m.raise_for_status.return_value = None
    m.json.return_value = text
    return m


# --- OpenAI ---
@patch("requests.post")
def test_openai_provider(mock_post):
    mock_post.return_value = mock_response({"choices": [{"message": {"content": "ok"}}]})

    p = OpenAIProvider("key", "gpt-5-mini", 999999, 999999)
    out = p.generate("hello")
    assert out == "ok"


# --- Claude ---
@patch("requests.post")
def test_claude_provider(mock_post):
    mock_post.return_value = mock_response({"content": [{"text": "ok"}]})

    p = ClaudeProvider("key", "claude-3-haiku", 999999, 999999)
    out = p.generate("hello")
    assert out == "ok"


# --- Gemini ---
@patch("requests.post")
def test_gemini_provider(mock_post):
    mock_post.return_value = mock_response(
        {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
    )

    p = GeminiProvider("key", "gemini-2.5-flash", 999999, 999999)
    out = p.generate("hello")
    assert out == "ok"


# --- DeepSeek ---
@patch("requests.post")
def test_deepseek_provider(mock_post):
    mock_post.return_value = mock_response({"choices": [{"message": {"content": "ok"}}]})

    p = DeepSeekProvider("key", "deepseek-v3.2-exp", 999999, 999999)
    out = p.generate("hello")
    assert out == "ok"
