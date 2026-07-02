"""Compatibility entrypoint for the refactored realtime prototype."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main() -> None:
    _ensure_src_on_path()

    from mk8dx_item_alert.config import RuntimeConfig
    from mk8dx_item_alert.runtime import run_realtime

    run_realtime(RuntimeConfig())


if __name__ == "__main__":
    main()
