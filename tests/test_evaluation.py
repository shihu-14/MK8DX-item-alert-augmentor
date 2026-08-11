import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from mk8dx_item_alert.evaluation import (
    evaluate_jsonl,
    prediction_frame_record,
)


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def _truth_object(
    bbox: list[int],
    *,
    label: str = "FB",
    state: str = "held",
    event_id: str | None = None,
    item_use_frame: int | None = None,
) -> dict[str, object]:
    value: dict[str, object] = {
        "label": label,
        "state": state,
    }
    if state == "held":
        value["opponent_id"] = f"gt-{bbox[0]}"
        value["opponent_bbox"] = bbox
    else:
        value["item_bbox"] = bbox
    if event_id is not None:
        value["event_id"] = event_id
    if item_use_frame is not None:
        value["item_use_frame"] = item_use_frame
    return value


def _prediction(
    opponent_bbox: list[int],
    *,
    track_id: int,
    label: str = "FB",
    item_bbox: list[int] | None = None,
    item_observed: bool = True,
) -> dict[str, object]:
    return {
        "runtime_track_id": track_id,
        "label": label,
        "confidence": 0.9,
        "opponent_bbox": opponent_bbox,
        "item_bbox": item_bbox or opponent_bbox,
        "item_observed": item_observed,
    }


def test_tracker_ids_are_not_used_as_ground_truth_identity(tmp_path: Path) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    _write_jsonl(
        truth,
        [{"frame": 1, "objects": [_truth_object([0, 0, 100, 100])]}],
    )
    _write_jsonl(
        predictions,
        [{"frame": 1, "alerts": [_prediction([0, 0, 100, 100], track_id=999)]}],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.true_positive == 1
    assert report.false_positive == 0
    assert report.false_negative == 0


def test_same_label_for_two_opponents_is_matched_one_to_one(tmp_path: Path) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    _write_jsonl(
        truth,
        [
            {
                "frame": 7,
                "objects": [
                    _truth_object([0, 0, 100, 100]),
                    _truth_object([120, 0, 220, 100]),
                ],
            }
        ],
    )
    _write_jsonl(
        predictions,
        [
            {
                "frame": 7,
                "alerts": [
                    _prediction([120, 0, 220, 100], track_id=4),
                    _prediction([0, 0, 100, 100], track_id=4),
                ],
            }
        ],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.true_positive == 2
    assert report.precision == 1.0
    assert report.recall == 1.0


def test_gate_metrics_separate_fp_fn_and_missing(tmp_path: Path) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    _write_jsonl(
        truth,
        [
            {"frame": 1, "gate_active": False, "objects": []},
            {"frame": 2, "gate_active": True, "objects": []},
            {"frame": 3, "gate_active": True, "objects": []},
        ],
    )
    _write_jsonl(
        predictions,
        [
            {"frame": 1, "gate_active": True, "alerts": []},
            {"frame": 2, "gate_active": False, "alerts": []},
        ],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.gate_false_positive == 1
    assert report.gate_false_negative == 1
    assert report.missing_gate_prediction == 1
    assert report.gate_errors == 3


def test_lead_time_is_scoped_to_each_matched_held_event(tmp_path: Path) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    bbox = [0, 0, 100, 100]
    _write_jsonl(
        truth,
        [
            {
                "frame": 1,
                "objects": [_truth_object(bbox, state="thrown")],
            },
            {
                "frame": 10,
                "objects": [
                    _truth_object(
                        bbox,
                        event_id="hold-1",
                        item_use_frame=20,
                    )
                ],
            },
            {
                "frame": 15,
                "objects": [
                    _truth_object(
                        bbox,
                        event_id="hold-2",
                        item_use_frame=30,
                    )
                ],
            },
        ],
    )
    _write_jsonl(
        predictions,
        [
            {"frame": 1, "alerts": [_prediction(bbox, track_id=1)]},
            {"frame": 10, "alerts": [_prediction(bbox, track_id=9)]},
            {"frame": 15, "alerts": [_prediction(bbox, track_id=12)]},
        ],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.false_alerts_by_state == {"thrown": 1}
    assert report.lead_frames_by_event == {"hold-1": 10, "hold-2": 15}
    assert report.average_lead_frames == 12.5


def test_runtime_prediction_record_uses_bbox_and_keeps_tracker_id_local() -> None:
    alert = SimpleNamespace(
        track_id=81,
        label="FB",
        confidence=0.75,
        opponent_bbox=(1.0, 2.0, 30.0, 40.0),
        item_bbox=(20.0, 25.0, 30.0, 35.0),
        item_observed=False,
    )
    result = SimpleNamespace(gate_active=True, mode="integrated", alerts=(alert,))

    record = prediction_frame_record(3, result)

    assert record["frame"] == 3
    assert record["alerts"][0]["runtime_track_id"] == 81
    assert record["alerts"][0]["opponent_bbox"] == [1.0, 2.0, 30.0, 40.0]
    assert record["alerts"][0]["item_bbox"] == [20.0, 25.0, 30.0, 35.0]
    assert record["alerts"][0]["item_observed"] is False


@pytest.mark.parametrize("state", ["thrown", "dropped", "background", "hud"])
def test_negative_without_opponent_is_classified_by_item_bbox(
    tmp_path: Path,
    state: str,
) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    item_bbox = [300, 200, 340, 240]
    _write_jsonl(
        truth,
        [{"frame": 1, "objects": [_truth_object(item_bbox, state=state)]}],
    )
    _write_jsonl(
        predictions,
        [
            {
                "frame": 1,
                "alerts": [
                    _prediction(
                        [0, 0, 100, 100],
                        track_id=7,
                        item_bbox=item_bbox,
                    )
                ],
            }
        ],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.false_positive == 1
    assert report.false_alerts_by_state == {state: 1}
    assert report.unclassified_false_positive == 0


def test_unmatched_prediction_is_reported_as_unclassified_false_positive(
    tmp_path: Path,
) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    _write_jsonl(truth, [{"frame": 1, "objects": []}])
    _write_jsonl(
        predictions,
        [{"frame": 1, "alerts": [_prediction([0, 0, 100, 100], track_id=1)]}],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.false_positive == 1
    assert report.unclassified_false_positive == 1
    assert report.false_alerts_by_state == {}


def test_persistent_ttl_alert_is_counted_on_each_output_frame(
    tmp_path: Path,
) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    _write_jsonl(
        truth,
        [
            {"frame": 1, "objects": [_truth_object([0, 0, 100, 100])]},
            {"frame": 2, "objects": [_truth_object([20, 0, 140, 120])]},
        ],
    )
    _write_jsonl(
        predictions,
        [
            {"frame": 1, "alerts": [_prediction([0, 0, 100, 100], track_id=5)]},
            {
                "frame": 2,
                "alerts": [
                    _prediction(
                        [20, 0, 140, 120],
                        track_id=5,
                        item_observed=False,
                    )
                ],
            },
        ],
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.true_positive == 2
    assert report.false_positive == 0


def test_event_identity_rejects_inconsistent_labels(tmp_path: Path) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    _write_jsonl(
        truth,
        [
            {
                "frame": 1,
                "objects": [
                    _truth_object([0, 0, 100, 100], event_id="event-1")
                ],
            },
            {
                "frame": 2,
                "objects": [
                    _truth_object(
                        [0, 0, 100, 100],
                        label="Boomerang",
                        event_id="event-1",
                        item_use_frame=5,
                    )
                ],
            },
        ],
    )
    _write_jsonl(predictions, [])

    with pytest.raises(ValueError, match="inconsistent label/use frame"):
        evaluate_jsonl(truth, predictions)
