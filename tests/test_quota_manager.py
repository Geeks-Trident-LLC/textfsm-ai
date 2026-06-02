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

    # Advance time by 61 seconds
    monkeypatch.setattr("textfsm_ai.quota_manager.time", lambda: q.window_start + 61)

    # Should reset and allow again
    assert q.allowed()
