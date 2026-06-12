from textfsm_ai.delivery.core.modes import DeliveryMode


def test_modes_literal():
    m: DeliveryMode = "quiet"
    assert m == "quiet"
