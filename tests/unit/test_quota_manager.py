# tests/unit/test_quota_manager.py

from __future__ import annotations

from textfsm_ai.quota_manager import QuotaManager


def test_quota_allows_within_limit():
    q = QuotaManager(max_requests_per_minute=3)

    assert q.allowed()
    assert q.allowed()
    assert q.allowed()


def test_quota_blocks_over_limit():
    q = QuotaManager(max_requests_per_minute=2)

    assert q.allowed()
    assert q.allowed()
    assert not q.allowed()  # third request should be blocked


def test_quota_resets_after_60_seconds(monkeypatch):
    q = QuotaManager(max_requests_per_minute=2)

    # Use up the quota
    assert q.allowed()
    assert q.allowed()
    assert not q.allowed()

    # Patch monotonic() inside the module, not time.time
    monkeypatch.setattr(
        "textfsm_ai.quota_manager.monotonic",
        lambda: q.window_start + 61,
    )

    # Should reset and allow again
    assert q.allowed()
