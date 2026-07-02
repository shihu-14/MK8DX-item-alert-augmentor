#!/usr/bin/env python3
"""Run the refactored MK8DX realtime item-alert prototype."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def _parse_source(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Camera index or video path.")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write annotated output video.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print per-frame debug messages when gate detection is active.",
    )
    return parser.parse_args()


def main() -> None:
    _ensure_src_on_path()

    from mk8dx_item_alert.config import RuntimeConfig
    from mk8dx_item_alert.runtime import run_realtime

    args = parse_args()
    config = RuntimeConfig()

    if args.source is not None:
        config = replace(config, source=_parse_source(args.source))
    if args.no_save:
        config = replace(
            config,
            output=replace(config.output, save_video=False),
        )
    if args.debug:
        config = replace(config, debug=True)

    run_realtime(config)


if __name__ == "__main__":
    main()
