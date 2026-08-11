"""Evaluate frame-level legacy candidates or integrated held alerts."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

VALID_STATES = frozenset({"held", "thrown", "dropped", "background", "hud"})
DEFAULT_IOU_THRESHOLD = 0.5
LEGACY_MODE = "legacy"
INTEGRATED_MODE = "integrated"
LEGACY_METRIC_SCOPE = "legacy_candidate"
INTEGRATED_METRIC_SCOPE = "integrated_held_alert"

BoundingBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class _TruthObject:
    label: str
    state: str
    opponent_bbox: BoundingBox | None
    item_bbox: BoundingBox | None
    event_id: str | None
    item_use_frame: int | None


@dataclass(frozen=True)
class _Prediction:
    label: str
    opponent_bbox: BoundingBox | None
    item_bbox: BoundingBox
    confidence: float
    item_observed: bool


@dataclass(frozen=True)
class EvaluationReport:
    metric_scope: str
    true_positive: int
    false_positive: int
    false_negative: int
    precision: float
    recall: float
    false_alerts_by_state: dict[str, int]
    unclassified_false_positive: int
    gate_false_positive: int
    gate_false_negative: int
    missing_gate_prediction: int
    average_lead_frames: float | None
    lead_frames_by_event: dict[str, int]

    @property
    def gate_errors(self) -> int:
        return (
            self.gate_false_positive
            + self.gate_false_negative
            + self.missing_gate_prediction
        )


def evaluate_jsonl(
    ground_truth_path: Path,
    predictions_path: Path,
    *,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> EvaluationReport:
    if not 0.0 < iou_threshold <= 1.0:
        raise ValueError("iou_threshold must be in (0, 1]")

    truth_frames = _read_frame_records(ground_truth_path, "objects")
    prediction_frames = _read_frame_records(predictions_path)
    prediction_mode = _prediction_mode(prediction_frames, predictions_path)
    collection_key = "candidates" if prediction_mode == LEGACY_MODE else "alerts"
    metric_scope = (
        LEGACY_METRIC_SCOPE
        if prediction_mode == LEGACY_MODE
        else INTEGRATED_METRIC_SCOPE
    )
    true_positive = 0
    false_positive = 0
    false_negative = 0
    unclassified_false_positive = 0
    false_states: Counter[str] = Counter()
    event_definitions: dict[str, tuple[str, int | None]] = {}
    matched_event_frames: dict[str, list[int]] = {}

    for frame in sorted(truth_frames.keys() | prediction_frames.keys()):
        truth_record = truth_frames.get(frame, {"objects": []})
        prediction_record = prediction_frames.get(frame, {"alerts": []})
        truth_objects = tuple(
            _parse_truth_object(value, ground_truth_path, frame)
            for value in truth_record.get("objects", [])
        )
        predicted_alerts = tuple(
            _parse_prediction(value, predictions_path, frame, prediction_mode)
            for value in _record_collection(
                prediction_record,
                collection_key,
                predictions_path,
                frame,
            )
        )
        held_truth = tuple(
            index
            for index, truth_object in enumerate(truth_objects)
            if truth_object.state == "held"
        )
        prediction_indexes = tuple(range(len(predicted_alerts)))
        held_matches = _match_frame(
            truth_objects,
            predicted_alerts,
            held_truth,
            prediction_indexes,
            iou_threshold,
            bbox_kind=(
                "item" if prediction_mode == LEGACY_MODE else "opponent"
            ),
        )
        held_predictions = {prediction_index for prediction_index, _ in held_matches}
        negative_truth = tuple(
            index
            for index, truth_object in enumerate(truth_objects)
            if truth_object.state != "held"
        )
        remaining_predictions = tuple(
            index
            for index in prediction_indexes
            if index not in held_predictions
        )
        negative_matches = _match_frame(
            truth_objects,
            predicted_alerts,
            negative_truth,
            remaining_predictions,
            iou_threshold,
            bbox_kind="item",
        )
        matched_held_truth = {truth_index for _, truth_index in held_matches}
        matched_negative_predictions = {
            prediction_index for prediction_index, _ in negative_matches
        }

        for truth_object in truth_objects:
            _register_event(event_definitions, truth_object)

        for _, truth_index in held_matches:
            truth_object = truth_objects[truth_index]
            true_positive += 1
            if truth_object.event_id is not None:
                matched_event_frames.setdefault(truth_object.event_id, []).append(frame)

        for _, truth_index in negative_matches:
            false_states[truth_objects[truth_index].state] += 1

        classified_false_positive = len(negative_matches)
        unclassified = (
            len(remaining_predictions) - len(matched_negative_predictions)
        )
        false_positive += classified_false_positive + unclassified
        unclassified_false_positive += unclassified
        false_negative += sum(
            truth_index not in matched_held_truth for truth_index in held_truth
        )

    gate_false_positive, gate_false_negative, missing_gate_prediction = (
        _count_gate_errors(truth_frames, prediction_frames)
    )
    lead_frames_by_event = {
        event_id: use_frame - min(matched_event_frames[event_id])
        for event_id, (_, use_frame) in sorted(event_definitions.items())
        if use_frame is not None and matched_event_frames.get(event_id)
    }
    lead_values = tuple(lead_frames_by_event.values())
    return EvaluationReport(
        metric_scope=metric_scope,
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=_safe_ratio(true_positive, true_positive + false_positive),
        recall=_safe_ratio(true_positive, true_positive + false_negative),
        false_alerts_by_state=dict(sorted(false_states.items())),
        unclassified_false_positive=unclassified_false_positive,
        gate_false_positive=gate_false_positive,
        gate_false_negative=gate_false_negative,
        missing_gate_prediction=missing_gate_prediction,
        average_lead_frames=(
            sum(lead_values) / len(lead_values) if lead_values else None
        ),
        lead_frames_by_event=lead_frames_by_event,
    )


def prediction_frame_record(frame: int, result) -> dict[str, object]:
    """Build one runtime prediction record without exposing tracker IDs as GT IDs."""
    if result.mode == LEGACY_MODE:
        return {
            "frame": frame,
            "gate_active": result.gate_active,
            "mode": result.mode,
            "candidates": [
                {
                    "label": detection.label,
                    "confidence": detection.confidence,
                    "item_bbox": [
                        detection.x1,
                        detection.y1,
                        detection.x2,
                        detection.y2,
                    ],
                }
                for detection in result.detections
            ],
        }

    alerts = []
    for alert in result.alerts:
        if alert.opponent_bbox is None or alert.item_bbox is None:
            continue
        alerts.append(
            {
                "runtime_track_id": alert.track_id,
                "label": alert.label,
                "confidence": alert.confidence,
                "opponent_bbox": list(alert.opponent_bbox),
                "item_bbox": list(alert.item_bbox),
                "item_observed": alert.item_observed,
            }
        )
    return {
        "frame": frame,
        "gate_active": result.gate_active,
        "mode": result.mode,
        "alerts": alerts,
    }


def write_prediction_frame(handle: TextIO, frame: int, result) -> None:
    handle.write(json.dumps(prediction_frame_record(frame, result), sort_keys=True))
    handle.write("\n")


def _read_frame_records(
    path: Path,
    collection_key: str | None = None,
) -> dict[int, dict[str, object]]:
    records: dict[int, dict[str, object]] = {}
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        raw = json.loads(line)
        if not isinstance(raw, dict):
            raise TypeError(f"{path}:{line_number}: record must be an object")
        if "frame" not in raw:
            raise ValueError(f"{path}:{line_number}: missing frame")
        frame = int(raw["frame"])
        if frame in records:
            raise ValueError(f"{path}:{line_number}: duplicate frame {frame}")
        collection = raw.get(collection_key, []) if collection_key else None
        if collection_key and not isinstance(collection, list):
            raise TypeError(
                f"{path}:{line_number}: {collection_key} must be a list"
            )
        if "gate_active" in raw and not isinstance(raw["gate_active"], bool):
            raise TypeError(f"{path}:{line_number}: gate_active must be a boolean")
        records[frame] = raw
    return records


def _prediction_mode(
    records: dict[int, dict[str, object]],
    path: Path,
) -> str:
    if not records:
        raise ValueError(f"{path}: prediction file must contain at least one frame")
    modes = {record.get("mode") for record in records.values()}
    if len(modes) != 1 or next(iter(modes)) not in {LEGACY_MODE, INTEGRATED_MODE}:
        raise ValueError(
            f"{path}: prediction frames must use one consistent legacy/integrated mode"
        )
    return str(next(iter(modes)))


def _record_collection(
    record: dict[str, object],
    key: str,
    path: Path,
    frame: int,
) -> list[object]:
    collection = record.get(key, [])
    if not isinstance(collection, list):
        raise TypeError(f"{path}:frame {frame}: {key} must be a list")
    return collection


def _parse_truth_object(raw: object, path: Path, frame: int) -> _TruthObject:
    value = _require_object(raw, path, frame, "truth object")
    state = str(_require_key(value, "state", path, frame))
    if state not in VALID_STATES:
        raise ValueError(f"{path}:frame {frame}: invalid state {state!r}")
    event_id = str(value["event_id"]) if "event_id" in value else None
    item_use_frame = (
        int(value["item_use_frame"]) if "item_use_frame" in value else None
    )
    if item_use_frame is not None and (state != "held" or event_id is None):
        raise ValueError(
            f"{path}:frame {frame}: item_use_frame requires held state and event_id"
        )
    if event_id is not None and state != "held":
        raise ValueError(f"{path}:frame {frame}: event_id requires held state")
    opponent_bbox = _parse_optional_bbox(
        value.get("opponent_bbox"),
        path,
        frame,
        "opponent_bbox",
    )
    item_bbox = _parse_optional_bbox(
        value.get("item_bbox"),
        path,
        frame,
        "item_bbox",
    )
    if state == "held" and opponent_bbox is None:
        raise ValueError(f"{path}:frame {frame}: held state requires opponent_bbox")
    if item_bbox is None:
        raise ValueError(f"{path}:frame {frame}: {state} state requires item_bbox")
    return _TruthObject(
        label=str(_require_key(value, "label", path, frame)),
        state=state,
        opponent_bbox=opponent_bbox,
        item_bbox=item_bbox,
        event_id=event_id,
        item_use_frame=item_use_frame,
    )


def _parse_prediction(
    raw: object,
    path: Path,
    frame: int,
    mode: str,
) -> _Prediction:
    value = _require_object(raw, path, frame, "predicted alert")
    item_observed = value.get("item_observed", True)
    opponent_bbox = _parse_optional_bbox(
        value.get("opponent_bbox"),
        path,
        frame,
        "opponent_bbox",
    )
    if mode == INTEGRATED_MODE:
        if opponent_bbox is None:
            raise ValueError(
                f"{path}:frame {frame}: integrated alert requires opponent_bbox"
            )
        if "item_observed" not in value:
            raise ValueError(
                f"{path}:frame {frame}: integrated alert requires item_observed"
            )
    if not isinstance(item_observed, bool):
        raise TypeError(f"{path}:frame {frame}: item_observed must be a boolean")
    return _Prediction(
        label=str(_require_key(value, "label", path, frame)),
        opponent_bbox=opponent_bbox,
        item_bbox=_parse_bbox(
            _require_key(value, "item_bbox", path, frame),
            path,
            frame,
            "item_bbox",
        ),
        confidence=float(value.get("confidence", 0.0)),
        item_observed=item_observed,
    )


def _match_frame(
    truth: tuple[_TruthObject, ...],
    predictions: tuple[_Prediction, ...],
    truth_indexes: tuple[int, ...],
    prediction_indexes: tuple[int, ...],
    iou_threshold: float,
    *,
    bbox_kind: str,
) -> tuple[tuple[int, int], ...]:
    candidates = {
        prediction_index: sorted(
            (
                (
                    truth_index,
                    _bbox_iou(
                        _prediction_bbox(predictions[prediction_index], bbox_kind),
                        _truth_bbox(truth[truth_index], bbox_kind),
                    ),
                )
                for truth_index in truth_indexes
                if predictions[prediction_index].label == truth[truth_index].label
                and _bbox_iou(
                    _prediction_bbox(predictions[prediction_index], bbox_kind),
                    _truth_bbox(truth[truth_index], bbox_kind),
                )
                >= iou_threshold
            ),
            key=lambda candidate: (-candidate[1], candidate[0]),
        )
        for prediction_index in prediction_indexes
    }
    order = sorted(
        prediction_indexes,
        key=lambda index: (
            len(candidates[index]),
            -predictions[index].confidence,
            _prediction_bbox(predictions[index], bbox_kind),
            predictions[index].label,
            index,
        ),
    )
    truth_owner: dict[int, int] = {}

    def assign(prediction_index: int, visited: set[int]) -> bool:
        for truth_index, _ in candidates[prediction_index]:
            if truth_index in visited:
                continue
            visited.add(truth_index)
            owner = truth_owner.get(truth_index)
            if owner is None or assign(owner, visited):
                truth_owner[truth_index] = prediction_index
                return True
        return False

    for prediction_index in order:
        assign(prediction_index, set())
    return tuple(sorted((prediction, truth) for truth, prediction in truth_owner.items()))


def _truth_bbox(truth: _TruthObject, bbox_kind: str) -> BoundingBox:
    bbox = truth.opponent_bbox if bbox_kind == "opponent" else truth.item_bbox
    if bbox is None:
        raise ValueError(f"truth record is missing {bbox_kind}_bbox")
    return bbox


def _prediction_bbox(prediction: _Prediction, bbox_kind: str) -> BoundingBox:
    bbox = (
        prediction.opponent_bbox
        if bbox_kind == "opponent"
        else prediction.item_bbox
    )
    if bbox is None:
        raise ValueError(f"prediction record is missing {bbox_kind}_bbox")
    return bbox


def _bbox_iou(left: BoundingBox, right: BoundingBox) -> float:
    intersection_width = max(0.0, min(left[2], right[2]) - max(left[0], right[0]))
    intersection_height = max(0.0, min(left[3], right[3]) - max(left[1], right[1]))
    intersection = intersection_width * intersection_height
    left_area = (left[2] - left[0]) * (left[3] - left[1])
    right_area = (right[2] - right[0]) * (right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def _parse_bbox(
    raw: object,
    path: Path,
    frame: int,
    name: str,
) -> BoundingBox:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValueError(f"{path}:frame {frame}: {name} must have 4 values")
    x1, y1, x2, y2 = (float(value) for value in raw)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"{path}:frame {frame}: {name} has invalid bounds")
    return x1, y1, x2, y2


def _parse_optional_bbox(
    raw: object,
    path: Path,
    frame: int,
    name: str,
) -> BoundingBox | None:
    if raw is None:
        return None
    return _parse_bbox(raw, path, frame, name)


def _register_event(
    definitions: dict[str, tuple[str, int | None]], truth_object: _TruthObject
) -> None:
    if truth_object.event_id is None:
        return
    definition = truth_object.label, truth_object.item_use_frame
    existing = definitions.get(truth_object.event_id)
    if existing is None:
        definitions[truth_object.event_id] = definition
        return
    labels_differ = existing[0] != definition[0]
    use_frames_differ = (
        existing[1] is not None
        and definition[1] is not None
        and existing[1] != definition[1]
    )
    if labels_differ or use_frames_differ:
        raise ValueError(
            f"event_id {truth_object.event_id!r} has inconsistent label/use frame"
        )
    if existing[1] is None and definition[1] is not None:
        definitions[truth_object.event_id] = definition


def _count_gate_errors(
    truth_frames: dict[int, dict[str, object]],
    prediction_frames: dict[int, dict[str, object]],
) -> tuple[int, int, int]:
    false_positive = 0
    false_negative = 0
    missing = 0
    for frame, truth_record in truth_frames.items():
        if "gate_active" not in truth_record:
            continue
        prediction_record = prediction_frames.get(frame)
        truth_active = bool(truth_record["gate_active"])
        if prediction_record is None or "gate_active" not in prediction_record:
            missing += 1
            continue
        prediction_active = bool(prediction_record["gate_active"])
        if prediction_active and not truth_active:
            false_positive += 1
        elif truth_active and not prediction_active:
            false_negative += 1
    return false_positive, false_negative, missing
def _require_object(
    raw: object, path: Path, frame: int, description: str
) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise TypeError(f"{path}:frame {frame}: {description} must be an object")
    return raw


def _require_key(
    value: dict[str, object], key: str, path: Path, frame: int
) -> object:
    if key not in value:
        raise ValueError(f"{path}:frame {frame}: missing {key}")
    return value[key]


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
