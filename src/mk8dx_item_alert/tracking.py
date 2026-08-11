"""Per-opponent temporal alert state."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .association import AssociatedItem
from .config import AlertConfig
from .inference import Detection


@dataclass
class _TrackState:
    track_id: int | str
    label: str
    history: deque[bool]
    center_x: float
    bbox_height_ema: float
    bbox_bottom: float
    confidence: float
    opponent_bbox: tuple[float, float, float, float] | None
    item_bbox: tuple[float, float, float, float] | None
    item_observed: bool
    confirmed: bool = False
    expires_at: float = 0.0


@dataclass(frozen=True)
class TrackAlert:
    track_id: int | str
    label: str
    center_x: float
    bbox_height: float
    bbox_bottom: float
    confidence: float
    opponent_bbox: tuple[float, float, float, float] | None
    item_bbox: tuple[float, float, float, float] | None
    item_observed: bool


@dataclass
class AlertTracker:
    states: dict[int | str, _TrackState] = field(default_factory=dict)

    def update_associations(
        self,
        associations: tuple[AssociatedItem, ...],
        now: float,
        config: AlertConfig,
        *,
        opponents: tuple[Detection, ...] = (),
    ) -> None:
        associated = {association.opponent_track_id for association in associations}
        for track_id, state in self.states.items():
            if isinstance(track_id, int):
                state.item_observed = False
            if track_id not in associated and isinstance(track_id, int):
                state.history.append(False)

        for opponent in opponents:
            track_id = opponent.track_id
            if track_id is None or track_id in associated:
                continue
            state = self.states.get(track_id)
            if state is not None:
                self._update_opponent_geometry(state, opponent, config)

        for association in associations:
            self._update(
                track_id=association.opponent_track_id,
                label=association.item.label,
                center_x=association.opponent.center_x,
                bbox_height=association.opponent.height,
                bbox_bottom=association.opponent.bottom,
                confidence=association.item.confidence,
                opponent_bbox=(
                    association.opponent.x1,
                    association.opponent.y1,
                    association.opponent.x2,
                    association.opponent.y2,
                ),
                item_bbox=(
                    association.item.x1,
                    association.item.y1,
                    association.item.x2,
                    association.item.y2,
                ),
                item_observed=True,
                now=now,
                config=config,
                required=config.confirmation_required,
            )
        self._remove_expired(now)

    def update_legacy(
        self,
        detections: tuple[Detection, ...],
        now: float,
        config: AlertConfig,
    ) -> None:
        best_by_label: dict[str, Detection] = {}
        for detection in detections:
            existing = best_by_label.get(detection.label)
            if existing is None or detection.confidence > existing.confidence:
                best_by_label[detection.label] = detection
        for label, detection in best_by_label.items():
            self._update(
                track_id=f"legacy:{label}",
                label=label,
                center_x=detection.center_x,
                bbox_height=detection.height,
                bbox_bottom=detection.bottom,
                confidence=detection.confidence,
                opponent_bbox=None,
                item_bbox=(
                    detection.x1,
                    detection.y1,
                    detection.x2,
                    detection.y2,
                ),
                item_observed=True,
                now=now,
                config=config,
                required=1,
            )
        self._remove_expired(now)

    def visible(self, now: float) -> tuple[TrackAlert, ...]:
        self._remove_expired(now)
        return tuple(
            TrackAlert(
                track_id=state.track_id,
                label=state.label,
                center_x=state.center_x,
                bbox_height=state.bbox_height_ema,
                bbox_bottom=state.bbox_bottom,
                confidence=state.confidence,
                opponent_bbox=state.opponent_bbox,
                item_bbox=state.item_bbox,
                item_observed=state.item_observed,
            )
            for state in self.states.values()
            if state.confirmed and now <= state.expires_at
        )

    def _update(
        self,
        *,
        track_id: int | str,
        label: str,
        center_x: float,
        bbox_height: float,
        bbox_bottom: float,
        confidence: float,
        opponent_bbox: tuple[float, float, float, float] | None,
        item_bbox: tuple[float, float, float, float] | None,
        item_observed: bool,
        now: float,
        config: AlertConfig,
        required: int,
    ) -> None:
        state = self.states.get(track_id)
        if state is None or state.label != label:
            state = _TrackState(
                track_id=track_id,
                label=label,
                history=deque(maxlen=config.confirmation_window),
                center_x=center_x,
                bbox_height_ema=bbox_height,
                bbox_bottom=bbox_bottom,
                confidence=confidence,
                opponent_bbox=opponent_bbox,
                item_bbox=item_bbox,
                item_observed=item_observed,
            )
            self.states[track_id] = state
        else:
            alpha = config.proximity_ema_alpha
            state.bbox_height_ema = (
                alpha * bbox_height + (1.0 - alpha) * state.bbox_height_ema
            )
            state.center_x = center_x
            state.bbox_bottom = bbox_bottom
            state.confidence = confidence
            state.opponent_bbox = opponent_bbox
            state.item_bbox = item_bbox
            state.item_observed = item_observed

        state.history.append(True)
        if sum(state.history) >= required:
            state.confirmed = True
            state.expires_at = now + config.duration_sec

    @staticmethod
    def _update_opponent_geometry(
        state: _TrackState,
        opponent: Detection,
        config: AlertConfig,
    ) -> None:
        alpha = config.proximity_ema_alpha
        state.bbox_height_ema = (
            alpha * opponent.height + (1.0 - alpha) * state.bbox_height_ema
        )
        state.center_x = opponent.center_x
        state.bbox_bottom = opponent.bottom
        state.opponent_bbox = (
            opponent.x1,
            opponent.y1,
            opponent.x2,
            opponent.y2,
        )

    def _remove_expired(self, now: float) -> None:
        expired = [
            track_id
            for track_id, state in self.states.items()
            if (
                state.confirmed
                and now > state.expires_at
            )
            or (
                not state.confirmed
                and len(state.history) == state.history.maxlen
                and not any(state.history)
            )
        ]
        for track_id in expired:
            del self.states[track_id]
