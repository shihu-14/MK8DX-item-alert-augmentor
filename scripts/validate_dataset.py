#!/usr/bin/env python3
"""Validate an exported seven-class MK8DX YOLO dataset."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from mk8dx_item_alert.labels import INTEGRATED_MODEL_LABELS

EXPECTED_LABELS = INTEGRATED_MODEL_LABELS


def validate_dataset(root: Path) -> list[str]:
    errors: list[str] = []
    data_yaml = root / "data.yaml"
    if not data_yaml.is_file():
        return [f"missing dataset config: {data_yaml}"]

    from ultralytics.utils import YAML

    config = YAML.load(data_yaml)
    names = config.get("names")
    if isinstance(names, dict):
        labels = tuple(names[index] for index in sorted(names))
    else:
        labels = tuple(names or ())
    if labels != EXPECTED_LABELS:
        errors.append(f"label order must be {EXPECTED_LABELS}, got {labels}")

    split_directories = [root / "train"]
    validation = root / "val"
    if not validation.is_dir():
        validation = root / "valid"
    split_directories.append(validation)
    if (root / "test").is_dir():
        split_directories.append(root / "test")

    for split in split_directories:
        images = split / "images"
        labels_dir = split / "labels"
        if not images.is_dir():
            errors.append(f"missing images directory: {images}")
        if not labels_dir.is_dir():
            errors.append(f"missing labels directory: {labels_dir}")
            continue
        for label_file in sorted(labels_dir.glob("*.txt")):
            errors.extend(_validate_label_file(label_file, len(EXPECTED_LABELS)))
    return errors


def _validate_label_file(path: Path, class_count: int) -> list[str]:
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        if not raw_line.strip():
            continue
        fields = raw_line.split()
        location = f"{path}:{line_number}"
        if len(fields) != 5:
            errors.append(f"{location}: expected five fields")
            continue
        try:
            class_id = int(fields[0])
            coordinates = tuple(float(value) for value in fields[1:])
        except ValueError:
            errors.append(f"{location}: fields must be numeric")
            continue
        if not 0 <= class_id < class_count:
            errors.append(f"{location}: class id {class_id} is out of range")
        if any(value < 0.0 or value > 1.0 for value in coordinates):
            errors.append(f"{location}: normalized coordinates must be within [0, 1]")
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args(argv)
    errors = validate_dataset(args.dataset)
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"valid dataset: {args.dataset}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
