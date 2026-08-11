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
    candidates_by_item = {
        item_index: _item_candidates(opponents, item, config)
        for item_index, item in enumerate(items)
    }
    item_order = sorted(
        range(len(items)),
        key=lambda index: (
            len(candidates_by_item[index]),
            -items[index].confidence,
            items[index].center_x,
            items[index].center_y,
            items[index].label,
            index,
        ),
    )
    opponent_owner: dict[int, int] = {}

    def assign(item_index: int, visited: set[int]) -> bool:
        for candidate in candidates_by_item[item_index]:
            track_id = candidate.opponent_track_id
            if track_id in visited:
                continue
            visited.add(track_id)
            owner = opponent_owner.get(track_id)
            if owner is None or assign(owner, visited):
                opponent_owner[track_id] = item_index
                return True
        return False

    for item_index in item_order:
        assign(item_index, set())

    return tuple(
        next(
            candidate
            for candidate in candidates_by_item[item_index]
            if candidate.opponent_track_id == track_id
        )
        for track_id, item_index in sorted(opponent_owner.items())
    )


def _item_candidates(
    opponents: tuple[Detection, ...],
    item: Detection,
    config: AssociationConfig,
) -> tuple[AssociatedItem, ...]:
    best_by_track: dict[int, AssociatedItem] = {}
    for opponent in opponents:
        if opponent.track_id is None or not _inside_expanded_box(
            opponent, item, config
        ):
            continue
        candidate = _candidate(opponent, item)
        existing = best_by_track.get(candidate.opponent_track_id)
        if existing is None or candidate.normalized_distance < existing.normalized_distance:
            best_by_track[candidate.opponent_track_id] = candidate
    return tuple(
        sorted(
            best_by_track.values(),
            key=lambda candidate: (
                candidate.normalized_distance,
                candidate.opponent_track_id,
            ),
        )
    )


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
) -> AssociatedItem:
    assert opponent.track_id is not None
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
