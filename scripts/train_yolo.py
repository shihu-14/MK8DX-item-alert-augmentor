#!/usr/bin/env python3
"""Train a reproducible MK8DX YOLO detection run."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from collections.abc import Mapping, Sequence
from importlib import metadata as importlib_metadata
from pathlib import Path

METADATA_FILENAME = "training-metadata.json"
VERSIONED_PACKAGES = ("ultralytics", "torch", "numpy", "opencv-python")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--scale", type=float, default=0.4)
    parser.add_argument("--shear", type=float, default=2.0)
    parser.add_argument("--perspective", type=float, default=0.0005)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--deterministic",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--project", type=Path, default=Path("runs/detect"))
    parser.add_argument("--name")
    parser.add_argument("--device")
    return parser


def build_training_options(args: argparse.Namespace) -> dict[str, object]:
    options: dict[str, object] = {
        "data": str(args.data),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "scale": args.scale,
        "shear": args.shear,
        "perspective": args.perspective,
        "seed": args.seed,
        "deterministic": args.deterministic,
        "project": str(args.project),
    }
    if args.name:
        options["name"] = args.name
    if args.device:
        options["device"] = args.device
    return options


def build_training_metadata(
    args: argparse.Namespace,
    options: Mapping[str, object],
    *,
    package_versions: Mapping[str, str] | None = None,
) -> dict[str, object]:
    data_path = args.data.resolve()
    base_model_path = Path(args.model)
    base_model: dict[str, object] = {"reference": args.model}
    if base_model_path.is_file():
        resolved_model = base_model_path.resolve()
        base_model.update(
            {
                "path": str(resolved_model),
                "sha256": _sha256_file(resolved_model),
            }
        )
    return {
        "schema_version": 1,
        "dataset": {
            "config_path": str(data_path),
            "config_sha256": _sha256_file(data_path),
        },
        "base_model": base_model,
        "training_options": dict(options),
        "package_versions": dict(package_versions or collect_package_versions()),
    }


def collect_package_versions() -> dict[str, str]:
    versions = {"python": platform.python_version()}
    for package in VERSIONED_PACKAGES:
        try:
            versions[package] = importlib_metadata.version(package)
        except importlib_metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def write_training_metadata(
    run_directory: Path,
    metadata: Mapping[str, object],
) -> Path:
    destination = run_directory / METADATA_FILENAME
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.data.is_file():
        raise SystemExit(f"dataset config does not exist: {args.data}")

    from ultralytics import YOLO

    options = build_training_options(args)
    model = YOLO(args.model)
    model.train(**options)
    save_dir = getattr(getattr(model, "trainer", None), "save_dir", None)
    if save_dir is None:
        raise RuntimeError("Ultralytics did not expose the completed run directory")
    metadata_path = write_training_metadata(
        Path(save_dir),
        build_training_metadata(args, options),
    )
    print(f"training metadata: {metadata_path}")
    return 0


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
