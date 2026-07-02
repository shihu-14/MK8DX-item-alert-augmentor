"""Class-level alert state tracking used by the current prototype."""

from __future__ import annotations

from dataclasses import dataclass

from .config import AlertConfig
from .overlay import apply_velocity_slide, calculate_alert_position


@dataclass
class AlertState:
    active: bool = False
    start_time: float = 0.0
    pos: tuple[int, int] = (0, 0)
    scale: float = 1.0
    prev_x: float | None = None
    prev_t: float | None = None
    vx: float = 0.0

    def expire(self) -> None:
        self.active = False
        self.prev_x = None
        self.prev_t = None
        self.vx = 0.0


@dataclass(frozen=True)
class VisibleAlert:
    label: str
    position: tuple[int, int]


class AlertStateTracker:
    def __init__(self, labels: tuple[str, ...]) -> None:
        self.states: dict[str, AlertState] = {label: AlertState() for label in labels}

    def update_detection(
        self,
        label: str,
        center_x: float,
        now: float,
        frame_width: int,
        frame_height: int,
        config: AlertConfig,
    ) -> None:
        state = self.states[label]
        if state.prev_x is not None and state.prev_t is not None:
            dt = max(now - state.prev_t, 1e-3)
            velocity = (center_x - state.prev_x) / dt
            state.vx = max(
                -config.max_horizontal_velocity,
                min(config.max_horizontal_velocity, velocity),
            )
        else:
            state.vx = 0.0

        state.prev_x = center_x
        state.prev_t = now
        state.active = True
        state.start_time = now
        state.pos = calculate_alert_position(
            center_x,
            frame_width,
            frame_height,
            config.size,
            config.bottom_margin,
        )
        state.scale = 1.0

    def visible_alerts(
        self,
        now: float,
        frame_width: int,
        config: AlertConfig,
    ) -> list[VisibleAlert]:
        visible: list[VisibleAlert] = []
        for label, state in self.states.items():
            if not state.active:
                continue

            elapsed = now - state.start_time
            if elapsed <= config.duration_sec:
                position = apply_velocity_slide(
                    state.pos,
                    state.vx,
                    elapsed,
                    frame_width,
                    config.size,
                )
                visible.append(VisibleAlert(label=label, position=position))
            else:
                state.expire()

        return visible
