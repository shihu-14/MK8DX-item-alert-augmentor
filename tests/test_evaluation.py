from pathlib import Path

from mk8dx_item_alert.evaluation import evaluate_jsonl


def test_evaluation_separates_held_hits_and_nonheld_false_alerts(
    tmp_path: Path,
) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    truth.write_text(
        '{"frame":1,"track_id":1,"label":"FB","state":"held",'
        '"item_use_frame":5}\n'
        '{"frame":2,"track_id":2,"label":"FB","state":"thrown"}\n'
    )
    predictions.write_text(
        '{"frame":1,"track_id":1,"label":"FB"}\n'
        '{"frame":2,"track_id":2,"label":"FB"}\n'
    )

    report = evaluate_jsonl(truth, predictions)

    assert report.true_positive == 1
    assert report.false_positive == 1
    assert report.false_alerts_by_state == {"thrown": 1}
    assert report.average_lead_frames == 4.0
