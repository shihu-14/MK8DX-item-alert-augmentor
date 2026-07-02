"""Frame-region helpers for gate detection and item masking."""

from __future__ import annotations

from dataclasses import dataclass

from .config import GateRegionConfig, ItemMaskConfig


@dataclass(frozen=True)
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)


def clip_rectangle(rect: Rect, frame_width: int, frame_height: int) -> Rect:
    return Rect(
        x1=max(0, min(frame_width, rect.x1)),
        y1=max(0, min(frame_height, rect.y1)),
        x2=max(0, min(frame_width, rect.x2)),
        y2=max(0, min(frame_height, rect.y2)),
    )


def compute_gate_region(
    frame_width: int,
    frame_height: int,
    config: GateRegionConfig,
) -> Rect:
    center_x = frame_width // 2 + config.center_x_offset
    center_y = frame_height // 2 + config.center_y_offset
    rect = Rect(
        x1=center_x - config.width // 2,
        y1=center_y - config.height // 2,
        x2=center_x + config.width // 2,
        y2=center_y + config.height // 2,
    )
    return clip_rectangle(rect, frame_width, frame_height)


def compute_item_mask_bounds(
    frame_height: int,
    config: ItemMaskConfig,
) -> tuple[int, int]:
    return int(frame_height * config.upper_ratio), int(frame_height * config.lower_ratio)


def ignored_regions(gate_region: Rect) -> tuple[Rect, ...]:
    return (gate_region,)
