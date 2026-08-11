"""Evaluate frame-level held-item alert records."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


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


def evaluate_jsonl(
    ground_truth_path: Path,
    predictions_path: Path,
) -> EvaluationReport:
    truth = _read_jsonl(ground_truth_path)
    predictions = _read_jsonl(predictions_path)
    held = {_event_key(event) for event in truth if event["state"] == "held"}
    predicted = {_event_key(event) for event in predictions}

    true_positive = len(held & predicted)
    false_positive = len(predicted - held)
    false_negative = len(held - predicted)
    false_states: Counter[str] = Counter()
    nonheld = {
        _event_key(event): str(event["state"])
        for event in truth
        if event["state"] != "held"
    }
    for key in predicted:
        if key in nonheld:
            false_states[nonheld[key]] += 1

    truth_gate = {
        int(event["frame"]): bool(event["gate_active"])
        for event in truth
        if "gate_active" in event
    }
    predicted_gate = {
        int(event["frame"]): bool(event["gate_active"])
        for event in predictions
        if "gate_active" in event
    }
    gate_errors = sum(
        predicted_gate.get(frame) != active
        for frame, active in truth_gate.items()
        if frame in predicted_gate
    )
    lead_frames = _lead_frames(truth, predictions)
    return EvaluationReport(
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        precision=_safe_ratio(true_positive, true_positive + false_positive),
        recall=_safe_ratio(true_positive, true_positive + false_negative),
        false_alerts_by_state=dict(sorted(false_states.items())),
        gate_errors=gate_errors,
        average_lead_frames=(
            sum(lead_frames) / len(lead_frames) if lead_frames else None
        ),
    )


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        for required in ("frame", "track_id", "label"):
            if required not in record:
                raise ValueError(f"{path}:{line_number}: missing {required}")
        records.append(record)
    return records


def _event_key(event: dict[str, object]) -> tuple[int, str, str]:
    return int(event["frame"]), str(event["track_id"]), str(event["label"])


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _lead_frames(
    truth: list[dict[str, object]],
    predictions: list[dict[str, object]],
) -> list[int]:
    earliest_prediction: dict[tuple[str, str], int] = {}
    for event in predictions:
        key = str(event["track_id"]), str(event["label"])
        frame = int(event["frame"])
        earliest_prediction[key] = min(
            frame,
            earliest_prediction.get(key, frame),
        )

    leads: list[int] = []
    seen: set[tuple[str, str, int]] = set()
    for event in truth:
        if event.get("state") != "held" or "item_use_frame" not in event:
            continue
        key = str(event["track_id"]), str(event["label"])
        use_frame = int(event["item_use_frame"])
        unique = key[0], key[1], use_frame
        if unique in seen or key not in earliest_prediction:
            continue
        seen.add(unique)
        leads.append(use_frame - earliest_prediction[key])
    return leads
