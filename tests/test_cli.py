from pathlib import Path

from mk8dx_item_alert.cli import build_parser


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
