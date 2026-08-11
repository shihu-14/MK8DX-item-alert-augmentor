from mk8dx_item_alert.association import associate_items
from mk8dx_item_alert.config import AssociationConfig
from mk8dx_item_alert.inference import Detection


def test_item_is_associated_with_nearest_expanded_opponent_box() -> None:
    opponents = (
        Detection("Opponent", 0.9, 0, 0, 100, 100, track_id=1),
        Detection("Opponent", 0.9, 100, 0, 200, 100, track_id=2),
    )
    item = Detection("Boomerang", 0.8, 115, 45, 125, 55)

    associated = associate_items(opponents, (item,), AssociationConfig())

    assert len(associated) == 1
    assert associated[0].opponent_track_id == 2


def test_untracked_opponents_do_not_produce_held_alert_candidates() -> None:
    opponent = Detection("Opponent", 0.9, 0, 0, 100, 100)
    item = Detection("Boomerang", 0.8, 45, 45, 55, 55)

    assert associate_items((opponent,), (item,), AssociationConfig()) == ()
