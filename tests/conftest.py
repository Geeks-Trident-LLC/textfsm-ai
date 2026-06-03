# tests/conftest.py
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def reset_test_real_session():
    original = os.environ.get("TEST_REAL", "false")
    yield
    os.environ["TEST_REAL"] = original
