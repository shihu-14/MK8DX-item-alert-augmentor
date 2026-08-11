from mk8dx_item_alert.association import AssociatedItem
from mk8dx_item_alert.config import AlertConfig
from mk8dx_item_alert.inference import Detection
from mk8dx_item_alert.tracking import AlertTracker


def _association(track_id: int, label: str = "Boomerang") -> AssociatedItem:
    opponent = Detection(
        "Opponent",
        0.9,
        100,
        100,
        300,
        400,
        track_id=track_id,
    )
    item = Detection(label, 0.8, 250, 250, 280, 280)
    return AssociatedItem(track_id, opponent, item, 0.5)


def test_track_alert_requires_three_of_five_observations() -> None:
    tracker = AlertTracker()
    config = AlertConfig()

    tracker.update_associations((_association(1),), 1.0, config)
    tracker.update_associations((), 2.0, config)
    tracker.update_associations((_association(1),), 3.0, config)
    assert tracker.visible(3.0) == ()

    tracker.update_associations((_association(1),), 4.0, config)
    assert tracker.visible(4.0)[0].track_id == 1


def test_same_item_class_is_tracked_for_multiple_opponents() -> None:
    tracker = AlertTracker()
    config = AlertConfig(confirmation_required=1)

    tracker.update_associations(
        (_association(1), _association(2)),
        1.0,
        config,
    )
    assert {alert.track_id for alert in tracker.visible(1.0)} == {1, 2}


def test_confirmed_alert_expires_after_ttl() -> None:
    tracker = AlertTracker()
    config = AlertConfig(confirmation_required=1, duration_sec=2.5)
    tracker.update_associations((_association(1),), 1.0, config)

    assert tracker.visible(3.5)
    assert tracker.visible(3.6) == ()


def test_ttl_alert_uses_current_opponent_geometry_without_new_item() -> None:
    tracker = AlertTracker()
    config = AlertConfig(confirmation_required=1, proximity_ema_alpha=0.5)
    association = _association(7)
    tracker.update_associations((association,), 1.0, config)
    current_opponent = Detection(
        "Opponent",
        0.9,
        50,
        50,
        350,
        500,
        track_id=7,
    )

    tracker.update_associations(
        (),
        2.0,
        config,
        opponents=(current_opponent,),
    )
    alert = tracker.visible(2.0)[0]

    assert alert.opponent_bbox == (50, 50, 350, 500)
    assert alert.bbox_height == 375.0
    assert alert.bbox_bottom == 500
    assert alert.item_bbox == (250, 250, 280, 280)
    assert alert.item_observed is False


def test_ttl_alert_keeps_last_geometry_when_no_opponent_is_observed() -> None:
    tracker = AlertTracker()
    config = AlertConfig(confirmation_required=1)
    tracker.update_associations((_association(7),), 1.0, config)

    tracker.update_associations((), 2.0, config, opponents=())
    alert = tracker.visible(2.0)[0]

    assert alert.opponent_bbox == (100, 100, 300, 400)
    assert alert.item_observed is False
