"""Evaluate frame-level held-item alert records."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

VALID_STATES = frozenset({"held", "thrown", "dropped", "background", "hud"})
DEFAULT_IOU_THRESHOLD = 0.5

BoundingBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class _TruthObject:
    label: str
    state: str
    opponent_bbox: BoundingBox
    event_id: str | None
    item_use_frame: int | None


@dataclass(frozen=True)
class _PredictedAlert:
    label: str
    opponent_bbox: BoundingBox
    confidence: float


@dataclass(frozen=True)
class EvaluationReport:
    true_positive: int
    false_positive: int
    false_negative: int
    precision: float
    recall: float
    false_alerts_by_state: dict[str, int]
    gate_errors: int
    average_lead_frames: float | None
    lead_frames_by_event: dict[str, int]


def evaluate_jsonl(
    ground_truth_path: Path,
    predictions_path: Path,
    *,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> EvaluationReport:
    if not 0.0 < iou_threshold <= 1.0:
        raise ValueError("iou_threshold must be in (0, 1]")

    truth_frames = _read_frame_records(ground_truth_path, "objects")
    prediction_frames = _read_frame_records(predictions_path, "alerts")
    true_positive = 0
    false_positive = 0
    false_negative = 0
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
            _parse_predicted_alert(value, predictions_path, frame)
            for value in prediction_record.get("alerts", [])
        )
        matches = _match_frame(truth_objects, predicted_alerts, iou_threshold)
        matched_truth = {truth_index for _, truth_index in matches}
        matched_predictions = {prediction_index for prediction_index, _ in matches}

        for truth_object in truth_objects:
            _register_event(event_definitions, truth_object)

        for _, truth_index in matches:
            truth_object = truth_objects[truth_index]
            if truth_object.state == "held":
                true_positive += 1
                if truth_object.event_id is not None:
                    matched_event_frames.setdefault(truth_object.event_id, []).append(
                        frame
                    )
            else:
                false_positive += 1
                false_states[truth_object.state] += 1

        false_positive += len(predicted_alerts) - len(matched_predictions)
        false_negative += sum(
            truth_object.state == "held" and index not in matched_truth
            for index, truth_object in enumerate(truth_objects)
        )

    gate_errors = _count_gate_errors(truth_frames, prediction_frames)
    lead_frames_by_event = {
        event_id: use_frame - min(matched_event_frames[event_id])
        for event_id, (_, use_frame) in sorted(event_definitions.items())
        if use_frame is not None and matched_event_frames.get(event_id)
    }
    lead_values = tuple(lead_frames_by_event.values())
    return EvaluationReport(
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=_safe_ratio(true_positive, true_positive + false_positive),
        recall=_safe_ratio(true_positive, true_positive + false_negative),
        false_alerts_by_state=dict(sorted(false_states.items())),
        gate_errors=gate_errors,
        average_lead_frames=(
            sum(lead_values) / len(lead_values) if lead_values else None
        ),
        lead_frames_by_event=lead_frames_by_event,
    )


def prediction_frame_record(frame: int, result) -> dict[str, object]:
    """Build one runtime prediction record without exposing tracker IDs as GT IDs."""
    alerts = []
    for alert in result.alerts:
        if alert.opponent_bbox is None:
            continue
        alerts.append(
            {
                "runtime_track_id": alert.track_id,
                "label": alert.label,
                "confidence": alert.confidence,
                "opponent_bbox": list(alert.opponent_bbox),
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


def _read_frame_records(path: Path, collection_key: str) -> dict[int, dict[str, object]]:
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
        collection = raw.get(collection_key, [])
        if not isinstance(collection, list):
            raise TypeError(
                f"{path}:{line_number}: {collection_key} must be a list"
            )
        if "gate_active" in raw and not isinstance(raw["gate_active"], bool):
            raise TypeError(f"{path}:{line_number}: gate_active must be a boolean")
        records[frame] = raw
    return records


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
    return _TruthObject(
        label=str(_require_key(value, "label", path, frame)),
        state=state,
        opponent_bbox=_parse_bbox(
            _require_key(value, "opponent_bbox", path, frame), path, frame
        ),
        event_id=event_id,
        item_use_frame=item_use_frame,
    )


def _parse_predicted_alert(
    raw: object, path: Path, frame: int
) -> _PredictedAlert:
    value = _require_object(raw, path, frame, "predicted alert")
    return _PredictedAlert(
        label=str(_require_key(value, "label", path, frame)),
        opponent_bbox=_parse_bbox(
            _require_key(value, "opponent_bbox", path, frame), path, frame
        ),
        confidence=float(value.get("confidence", 0.0)),
    )


def _match_frame(
    truth: tuple[_TruthObject, ...],
    predictions: tuple[_PredictedAlert, ...],
    iou_threshold: float,
) -> tuple[tuple[int, int], ...]:
    candidates = {
        prediction_index: sorted(
            (
                (truth_index, _bbox_iou(prediction.opponent_bbox, target.opponent_bbox))
                for truth_index, target in enumerate(truth)
                if prediction.label == target.label
                and _bbox_iou(prediction.opponent_bbox, target.opponent_bbox)
                >= iou_threshold
            ),
            key=lambda candidate: (-candidate[1], candidate[0]),
        )
        for prediction_index, prediction in enumerate(predictions)
    }
    order = sorted(
        range(len(predictions)),
        key=lambda index: (
            len(candidates[index]),
            -predictions[index].confidence,
            predictions[index].opponent_bbox,
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


def _bbox_iou(left: BoundingBox, right: BoundingBox) -> float:
    intersection_width = max(0.0, min(left[2], right[2]) - max(left[0], right[0]))
    intersection_height = max(0.0, min(left[3], right[3]) - max(left[1], right[1]))
    intersection = intersection_width * intersection_height
    left_area = (left[2] - left[0]) * (left[3] - left[1])
    right_area = (right[2] - right[0]) * (right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def _parse_bbox(raw: object, path: Path, frame: int) -> BoundingBox:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValueError(f"{path}:frame {frame}: opponent_bbox must have 4 values")
    x1, y1, x2, y2 = (float(value) for value in raw)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"{path}:frame {frame}: opponent_bbox has invalid bounds")
    return x1, y1, x2, y2


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
) -> int:
    errors = 0
    for frame, truth_record in truth_frames.items():
        if "gate_active" not in truth_record:
            continue
        errors += not _gate_prediction_matches(
            truth_record,
            prediction_frames.get(frame),
        )
    return errors


def _gate_prediction_matches(
    truth_record: dict[str, object],
    prediction_record: dict[str, object] | None,
) -> bool:
    if prediction_record is None or "gate_active" not in prediction_record:
        return False
    return bool(prediction_record["gate_active"]) == bool(truth_record["gate_active"])


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
