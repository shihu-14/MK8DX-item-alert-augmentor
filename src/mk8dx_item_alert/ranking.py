"""Estimated-distance ordering for opponent alerts."""

from __future__ import annotations

from dataclasses import dataclass

from .tracking import TrackAlert


@dataclass(frozen=True)
class RankedAlert:
    rank: int
    track_id: int | str
    label: str
    confidence: float
    opponent_bbox: tuple[float, float, float, float] | None
    item_bbox: tuple[float, float, float, float] | None
    item_observed: bool


def rank_nearest(
    alerts: tuple[TrackAlert, ...],
    max_visible: int,
) -> tuple[RankedAlert, ...]:
    ordered = sorted(
        alerts,
        key=lambda alert: (
            -alert.bbox_height,
            -alert.bbox_bottom,
            str(alert.track_id),
        ),
    )
    return tuple(
        RankedAlert(
            rank=index,
            track_id=alert.track_id,
            label=alert.label,
            confidence=alert.confidence,
            opponent_bbox=alert.opponent_bbox,
            item_bbox=alert.item_bbox,
            item_observed=alert.item_observed,
        )
        for index, alert in enumerate(ordered[:max_visible], start=1)
    )
