from pathlib import Path

from mk8dx_item_alert.cli import build_parser, main


def test_run_command_parses_documented_options() -> None:
    args = build_parser().parse_args(
        [
            "run",
            "--source",
            "video.mp4",
            "--no-save",
            "--profile",
            "--predictions-jsonl",
            "predictions/run.jsonl",
        ]
    )

    assert args.command == "run"
    assert args.source == "video.mp4"
    assert args.no_save is True
    assert args.profile is True
    assert args.predictions_jsonl == Path("predictions/run.jsonl")


def test_evaluate_command_parses_iou_threshold() -> None:
    args = build_parser().parse_args(
        [
            "evaluate",
            "--ground-truth",
            "truth.jsonl",
            "--predictions",
            "predictions.jsonl",
            "--iou-threshold",
            "0.6",
        ]
    )

    assert args.iou_threshold == 0.6


def test_evaluate_command_prints_false_alert_and_gate_breakdown(
    tmp_path: Path,
    capsys,
) -> None:
    truth = tmp_path / "truth.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    truth.write_text(
        '{"frame":1,"gate_active":false,"objects":[]}\n',
        encoding="utf-8",
    )
    predictions.write_text(
        '{"frame":1,"gate_active":true,"alerts":[]}',
        encoding="utf-8",
    )

    assert main(
        [
            "evaluate",
            "--ground-truth",
            str(truth),
            "--predictions",
            str(predictions),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "unclassified_fp=0" in output
    assert "gate_errors=1 gate_fp=1 gate_fn=0 gate_missing=0" in output
