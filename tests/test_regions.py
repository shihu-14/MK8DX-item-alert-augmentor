from mk8dx_item_alert.config import GateRegionConfig, ItemMaskConfig
from mk8dx_item_alert.regions import (
    Rect,
    clip_rectangle,
    compute_gate_region,
    compute_item_mask_bounds,
    ignored_regions,
)


def test_gate_region_matches_current_1080p_calculation() -> None:
    rect = compute_gate_region(1920, 1080, GateRegionConfig())

    assert rect == Rect(x1=845, y1=560, x2=1275, y2=920)


def test_item_mask_bounds_match_current_ratios() -> None:
    assert compute_item_mask_bounds(1080, ItemMaskConfig()) == (248, 864)


def test_clip_rectangle_keeps_bounds_inside_frame() -> None:
    rect = clip_rectangle(Rect(-10, 5, 30, 200), frame_width=20, frame_height=100)

    assert rect == Rect(x1=0, y1=5, x2=20, y2=100)


def test_ignored_regions_describes_gate_region() -> None:
    gate = Rect(1, 2, 3, 4)

    assert ignored_regions(gate) == (gate,)
