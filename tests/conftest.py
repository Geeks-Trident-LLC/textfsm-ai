# tests/conftest.py

import os

import pytest


# ------------------------------------------------------------
# Global flag: only run real tests when --real is passed
# ------------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--real",
        action="store_true",
        default=False,
        help="Run real provider tests (requires API keys)",
    )


@pytest.fixture(scope="session")
def require_real_tests(pytestconfig):
    if not pytestconfig.getoption("--real"):
        pytest.skip("Real provider tests require --real")
    return True


# ------------------------------------------------------------
# Helper for environment variables
# ------------------------------------------------------------
def _require_env(var: str):
    value = os.getenv(var)
    if not value:
        pytest.skip(f"{var} must be set for real provider tests")
    return value


# ------------------------------------------------------------
# Provider fixtures
# ------------------------------------------------------------
@pytest.fixture(scope="session")
def deepseek_key(require_real_tests):
    return _require_env("DEEPSEEK_API_KEY")


@pytest.fixture(scope="session")
def openai_key(require_real_tests):
    return _require_env("OPENAI_API_KEY")


@pytest.fixture(scope="session")
def gemini_key(require_real_tests):
    return _require_env("GEMINI_API_KEY")


@pytest.fixture(scope="session")
def anthropic_key(require_real_tests):
    return _require_env("ANTHROPIC_API_KEY")


@pytest.fixture(scope="session")
def groq_key(require_real_tests):
    return _require_env("GROQ_API_KEY")


@pytest.fixture(scope="session")
def xai_key(require_real_tests):
    return _require_env("XAI_API_KEY")


@pytest.fixture(scope="session")
def together_key(require_real_tests):
    return _require_env("TOGETHER_API_KEY")


@pytest.fixture(scope="session")
def fireworks_key(require_real_tests):
    return _require_env("FIREWORKS_API_KEY")


@pytest.fixture(scope="session")
def cerebras_key(require_real_tests):
    return _require_env("CEREBRAS_API_KEY")


@pytest.fixture(scope="session")
def perplexity_key(require_real_tests):
    return _require_env("PERPLEXITY_API_KEY")


@pytest.fixture(scope="session")
def azure_key(require_real_tests):
    return _require_env("AZURE_OPENAI_API_KEY")


@pytest.fixture(scope="session")
def azure_endpoint(require_real_tests):
    return _require_env("AZURE_OPENAI_ENDPOINT")


@pytest.fixture(scope="session")
def azure_api_version(require_real_tests):
    return os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
