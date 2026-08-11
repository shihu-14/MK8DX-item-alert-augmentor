#!/usr/bin/env python3
"""Train a reproducible MK8DX YOLO detection run."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--scale", type=float, default=0.4)
    parser.add_argument("--shear", type=float, default=2.0)
    parser.add_argument("--perspective", type=float, default=0.0005)
    parser.add_argument("--project", type=Path, default=Path("runs/detect"))
    parser.add_argument("--name")
    parser.add_argument("--device")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.data.is_file():
        raise SystemExit(f"dataset config does not exist: {args.data}")

    from ultralytics import YOLO

    options: dict[str, object] = {
        "data": str(args.data),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "scale": args.scale,
        "shear": args.shear,
        "perspective": args.perspective,
        "project": str(args.project),
    }
    if args.name:
        options["name"] = args.name
    if args.device:
        options["device"] = args.device
    YOLO(args.model).train(**options)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
