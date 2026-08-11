"""Associate detected held items with tracked opponents."""

from __future__ import annotations

from dataclasses import dataclass

from .config import AssociationConfig
from .inference import Detection


@dataclass(frozen=True)
class AssociatedItem:
    opponent_track_id: int
    opponent: Detection
    item: Detection
    normalized_distance: float


def associate_items(
    opponents: tuple[Detection, ...],
    items: tuple[Detection, ...],
    config: AssociationConfig,
) -> tuple[AssociatedItem, ...]:
    best_by_opponent: dict[int, AssociatedItem] = {}
    for item in items:
        candidates = [
            _candidate(opponent, item, config)
            for opponent in opponents
            if opponent.track_id is not None
            and _inside_expanded_box(opponent, item, config)
        ]
        candidates = [candidate for candidate in candidates if candidate is not None]
        if not candidates:
            continue
        selected = min(candidates, key=lambda candidate: candidate.normalized_distance)
        existing = best_by_opponent.get(selected.opponent_track_id)
        if existing is None or _is_better(selected, existing):
            best_by_opponent[selected.opponent_track_id] = selected
    return tuple(best_by_opponent[key] for key in sorted(best_by_opponent))


def _inside_expanded_box(
    opponent: Detection,
    item: Detection,
    config: AssociationConfig,
) -> bool:
    horizontal_padding = opponent.width * config.horizontal_padding_ratio
    vertical_padding = opponent.height * config.vertical_padding_ratio
    return (
        opponent.x1 - horizontal_padding
        <= item.center_x
        <= opponent.x2 + horizontal_padding
        and opponent.y1 - vertical_padding
        <= item.center_y
        <= opponent.y2 + vertical_padding
    )


def _candidate(
    opponent: Detection,
    item: Detection,
    config: AssociationConfig,
) -> AssociatedItem | None:
    if opponent.track_id is None:
        return None
    half_width = max(opponent.width / 2, 1.0)
    half_height = max(opponent.height / 2, 1.0)
    dx = abs(item.center_x - opponent.center_x) / half_width
    dy = abs(item.center_y - opponent.center_y) / half_height
    return AssociatedItem(
        opponent_track_id=opponent.track_id,
        opponent=opponent,
        item=item,
        normalized_distance=(dx * dx + dy * dy) ** 0.5,
    )


def _is_better(candidate: AssociatedItem, existing: AssociatedItem) -> bool:
    if candidate.item.confidence != existing.item.confidence:
        return candidate.item.confidence > existing.item.confidence
    return candidate.normalized_distance < existing.normalized_distance
