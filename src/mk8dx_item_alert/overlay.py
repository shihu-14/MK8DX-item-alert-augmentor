"""Alert overlay placement and drawing helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OverlayBounds:
    frame_x1: int
    frame_y1: int
    frame_x2: int
    frame_y2: int
    icon_x1: int
    icon_y1: int
    icon_x2: int
    icon_y2: int


def clip_top_left(
    x: int,
    y: int,
    frame_size: tuple[int, int],
    overlay_size: tuple[int, int],
) -> tuple[int, int]:
    frame_width, frame_height = frame_size
    overlay_width, overlay_height = overlay_size
    max_x = max(0, frame_width - overlay_width)
    max_y = max(0, frame_height - overlay_height)
    return max(0, min(max_x, x)), max(0, min(max_y, y))


def calculate_alert_position(
    center_x: float,
    frame_width: int,
    frame_height: int,
    alert_size: tuple[int, int],
    bottom_margin: int = 10,
) -> tuple[int, int]:
    alert_width, alert_height = alert_size
    x = int(center_x - alert_width // 2)
    y = frame_height - alert_height - bottom_margin
    return clip_top_left(x, y, (frame_width, frame_height), alert_size)


def apply_velocity_slide(
    position: tuple[int, int],
    velocity_x: float,
    elapsed_sec: float,
    frame_width: int,
    alert_size: tuple[int, int],
) -> tuple[int, int]:
    x, y = position
    dx = int(velocity_x * elapsed_sec)
    max_x = max(0, frame_width - alert_size[0])
    return max(0, min(max_x, x + dx)), y


def calculate_overlay_bounds(
    position: tuple[int, int],
    frame_size: tuple[int, int],
    overlay_size: tuple[int, int],
) -> OverlayBounds | None:
    x, y = position
    frame_width, frame_height = frame_size
    overlay_width, overlay_height = overlay_size

    frame_x1 = max(0, x)
    frame_y1 = max(0, y)
    frame_x2 = min(frame_width, x + overlay_width)
    frame_y2 = min(frame_height, y + overlay_height)

    if frame_x2 <= frame_x1 or frame_y2 <= frame_y1:
        return None

    icon_x1 = frame_x1 - x
    icon_y1 = frame_y1 - y
    icon_x2 = icon_x1 + (frame_x2 - frame_x1)
    icon_y2 = icon_y1 + (frame_y2 - frame_y1)
    return OverlayBounds(
        frame_x1=frame_x1,
        frame_y1=frame_y1,
        frame_x2=frame_x2,
        frame_y2=frame_y2,
        icon_x1=icon_x1,
        icon_y1=icon_y1,
        icon_x2=icon_x2,
        icon_y2=icon_y2,
    )


def draw_icon(
    frame,
    icon,
    position: tuple[int, int],
    alert_size: tuple[int, int],
) -> None:
    import cv2

    x, y = position
    x, y = clip_top_left(x, y, (frame.shape[1], frame.shape[0]), alert_size)
    bounds = calculate_overlay_bounds((x, y), (frame.shape[1], frame.shape[0]), alert_size)
    if bounds is None:
        return

    resized = cv2.resize(icon, alert_size)
    frame[
        bounds.frame_y1 : bounds.frame_y2,
        bounds.frame_x1 : bounds.frame_x2,
    ] = resized[
        bounds.icon_y1 : bounds.icon_y2,
        bounds.icon_x1 : bounds.icon_x2,
    ]
