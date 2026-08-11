from mk8dx_item_alert.overlay import (
    OverlayBounds,
    calculate_overlay_bounds,
    calculate_ranked_positions,
    clip_top_left,
)


def test_clip_top_left_handles_overlay_larger_than_frame() -> None:
    assert clip_top_left(50, 50, (100, 100), (150, 150)) == (0, 0)


def test_ranked_positions_are_centered_and_bottom_aligned() -> None:
    assert calculate_ranked_positions(
        3,
        (600, 400),
        (96, 96),
        gap=12,
        bottom_margin=10,
    ) == ((144, 294), (252, 294), (360, 294))


def test_ranked_positions_clip_when_frame_is_narrow() -> None:
    positions = calculate_ranked_positions(3, (200, 100), (96, 96), gap=12)
    assert positions == ((0, 0), (104, 0), (104, 0))


def test_overlay_bounds_clip_visible_frame_and_icon_regions() -> None:
    assert calculate_overlay_bounds((-10, -20), (100, 80), (40, 50)) == OverlayBounds(
        frame_x1=0,
        frame_y1=0,
        frame_x2=30,
        frame_y2=30,
        icon_x1=10,
        icon_y1=20,
        icon_x2=40,
        icon_y2=50,
    )
