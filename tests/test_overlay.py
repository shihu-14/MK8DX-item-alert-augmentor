from mk8dx_item_alert.overlay import (
    OverlayBounds,
    apply_velocity_slide,
    calculate_overlay_bounds,
    calculate_alert_position,
    clip_top_left,
)


def test_alert_position_uses_bottom_margin_and_center_x() -> None:
    assert calculate_alert_position(100, 1920, 1080, (150, 150)) == (25, 920)


def test_alert_position_clips_to_frame_edges() -> None:
    assert calculate_alert_position(10, 1920, 1080, (150, 150)) == (0, 920)
    assert calculate_alert_position(2000, 1920, 1080, (150, 150)) == (1770, 920)


def test_clip_top_left_handles_overlay_larger_than_frame() -> None:
    assert clip_top_left(50, 50, (100, 100), (150, 150)) == (0, 0)


def test_velocity_slide_clips_horizontal_motion() -> None:
    assert apply_velocity_slide((1770, 920), 400.0, 2.0, 1920, (150, 150)) == (
        1770,
        920,
    )
    assert apply_velocity_slide((25, 920), -400.0, 2.0, 1920, (150, 150)) == (
        0,
        920,
    )


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
