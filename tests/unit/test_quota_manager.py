import time
from pathlib import Path

from textfsm_ai.quota_manager import QuotaManager


def test_quota_allows_within_limits(tmp_path, monkeypatch):
    # Redirect usage file to temp directory
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    qm = QuotaManager("openai", daily_limit=100, monthly_limit=500)

    assert qm.allowed(50) is True
    qm.add_tokens(50)
    assert qm.allowed(40) is True
    assert qm.allowed(60) is False  # would exceed daily limit


def test_quota_daily_reset(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    qm = QuotaManager("openai", daily_limit=100, monthly_limit=500)

    qm.add_tokens(80)
    assert qm.allowed(30) is False  # would exceed daily limit

    # Simulate next day
    monkeypatch.setattr(
        time, "strftime", lambda fmt: "2099-01-02" if fmt == "%Y-%m-%d" else "2099-01"
    )

    assert qm.allowed(100) is True  # daily reset happened


def test_quota_monthly_reset(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    qm = QuotaManager("openai", daily_limit=100, monthly_limit=200)

    qm.add_tokens(150)
    assert qm.allowed(100) is False  # would exceed monthly limit

    # Simulate next month
    def fake_strftime(fmt):
        if fmt == "%Y-%m":
            return "2099-02"
        if fmt == "%Y-%m-%d":
            return "2099-02-01"
        return time.strftime(fmt)  # fallback for other formats

    monkeypatch.setattr(time, "strftime", fake_strftime)

    assert qm.allowed(150) is True  # monthly reset happened

    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    qm = QuotaManager("openai", daily_limit=100, monthly_limit=200)

    qm.add_tokens(150)
    assert qm.allowed(100) is False  # would exceed monthly limit

    # Simulate next month
    monkeypatch.setattr(
        time, "strftime", lambda fmt: "2099-03" if fmt == "%Y-%m" else "2099-03-01"
    )

    assert qm.allowed(150) is True  # monthly reset happened


def test_quota_persists_usage(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    qm1 = QuotaManager("openai", daily_limit=100, monthly_limit=500)
    qm1.add_tokens(60)

    # Reload manager to ensure persistence
    qm2 = QuotaManager("openai", daily_limit=100, monthly_limit=500)

    assert qm2.allowed(30) is True
    assert qm2.allowed(50) is False  # would exceed daily limit
