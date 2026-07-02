from mk8dx_item_alert.config import AlertConfig
from mk8dx_item_alert.smoothing import AlertStateTracker


def test_alert_state_updates_position_and_velocity() -> None:
    tracker = AlertStateTracker(("Boomerang",))
    config = AlertConfig()

    tracker.update_detection("Boomerang", 100.0, 10.0, 1920, 1080, config)
    first_state = tracker.states["Boomerang"]

    assert first_state.active is True
    assert first_state.pos == (25, 920)
    assert first_state.vx == 0.0

    tracker.update_detection("Boomerang", 300.0, 10.5, 1920, 1080, config)
    second_state = tracker.states["Boomerang"]

    assert second_state.pos == (225, 920)
    assert second_state.vx == 400.0


def test_visible_alerts_expire_and_reset_previous_detection_state() -> None:
    tracker = AlertStateTracker(("Boomerang",))
    config = AlertConfig()

    tracker.update_detection("Boomerang", 100.0, 10.0, 1920, 1080, config)

    assert tracker.visible_alerts(11.0, 1920, config)
    assert tracker.visible_alerts(12.6, 1920, config) == []

    state = tracker.states["Boomerang"]
    assert state.active is False
    assert state.prev_x is None
    assert state.prev_t is None
    assert state.vx == 0.0
