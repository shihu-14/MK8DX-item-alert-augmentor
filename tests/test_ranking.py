from mk8dx_item_alert.ranking import rank_nearest
from mk8dx_item_alert.tracking import TrackAlert


def test_rank_uses_opponent_height_then_bottom_and_limits_output() -> None:
    alerts = (
        TrackAlert(1, "FB", 100, 100, 500, 0.8, (0, 0, 100, 500), None, False),
        TrackAlert(
            2,
            "Boomerang",
            200,
            150,
            450,
            0.7,
            (0, 0, 100, 450),
            None,
            False,
        ),
        TrackAlert(
            3,
            "Super-Horn",
            300,
            100,
            600,
            0.9,
            (0, 0, 100, 600),
            None,
            False,
        ),
    )

    ranked = rank_nearest(alerts, max_visible=2)

    assert [(alert.rank, alert.track_id) for alert in ranked] == [(1, 2), (2, 3)]
