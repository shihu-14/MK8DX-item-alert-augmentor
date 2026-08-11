"""Command-line interface for the MK8DX item-alert augmentor."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from .config import DEFAULT_MODEL_DIR, RuntimeConfig
from .model_store import (
    DEFAULT_MANIFEST_PATH,
    ModelStoreError,
    install_models,
    load_manifest,
    verify_models,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mk8dx-alert")
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="Run realtime item alerts.")
    run_parser.add_argument("--source", default="0", help="Camera index or video path.")
    run_parser.add_argument("--item-model", type=Path)
    run_parser.add_argument("--gate-model", type=Path)
    run_parser.add_argument("--no-gate", action="store_true")
    run_parser.add_argument("--no-save", action="store_true")
    run_parser.add_argument("--debug", action="store_true")
    run_parser.add_argument("--profile", action="store_true")

    models_parser = commands.add_parser("models", help="Manage local model files.")
    model_commands = models_parser.add_subparsers(
        dest="model_command",
        required=True,
    )
    for name in ("verify", "install"):
        model_parser = model_commands.add_parser(name)
        model_parser.add_argument(
            "--manifest",
            type=Path,
            default=DEFAULT_MANIFEST_PATH,
        )
        model_parser.add_argument(
            "--model-dir",
            type=Path,
            default=DEFAULT_MODEL_DIR,
        )

    evaluate_parser = commands.add_parser(
        "evaluate",
        help="Evaluate JSONL held-item alert records.",
    )
    evaluate_parser.add_argument("--ground-truth", type=Path, required=True)
    evaluate_parser.add_argument("--predictions", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return _run_command(args)
    if args.command == "evaluate":
        return _evaluate_command(args)
    return _models_command(args)


def _run_command(args: argparse.Namespace) -> int:
    from .runtime import run_realtime

    config = RuntimeConfig(
        source=_parse_source(args.source),
        gate_enabled=not args.no_gate,
        debug=args.debug,
        profile=args.profile,
    )
    if args.item_model is not None:
        config = replace(
            config,
            models=replace(config.models, item_model_path=args.item_model),
        )
    if args.gate_model is not None:
        config = replace(
            config,
            models=replace(config.models, gate_model_path=args.gate_model),
        )
    if args.no_save:
        config = replace(
            config,
            output=replace(config.output, save_video=False),
        )
    run_realtime(config)
    return 0


def _models_command(args: argparse.Namespace) -> int:
    try:
        manifest = load_manifest(args.manifest)
        if args.model_command == "verify":
            paths = verify_models(manifest, args.model_dir)
        else:
            paths = install_models(manifest, args.model_dir)
    except ModelStoreError as error:
        print(f"model error: {error}")
        return 1
    for path in paths:
        print(f"verified: {path}")
    return 0


def _evaluate_command(args: argparse.Namespace) -> int:
    from .evaluation import evaluate_jsonl

    report = evaluate_jsonl(args.ground_truth, args.predictions)
    print(
        f"precision={report.precision:.4f} recall={report.recall:.4f} "
        f"tp={report.true_positive} fp={report.false_positive} "
        f"fn={report.false_negative} gate_errors={report.gate_errors}"
    )
    if report.average_lead_frames is not None:
        print(f"average_lead_frames={report.average_lead_frames:.2f}")
    for state, count in report.false_alerts_by_state.items():
        print(f"false_alert[{state}]={count}")
    return 0


def _parse_source(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value
