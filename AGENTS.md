# MK8DX Item Alert Agent Guide

## Project Purpose

This repository is a local research prototype for Mario Kart 8 Deluxe
opponent-held-item alerts. It is not a generic detector and must not claim that
an item is held unless opponent association and temporal confirmation occurred.
Keep use to local research, offline testing, and documentation.

## Source Of Truth

- `mk8dx-alert` is the only supported runtime command.
- `src/mk8dx_item_alert/runtime.py` owns capture and resource lifecycle.
- `src/mk8dx_item_alert/pipeline.py` owns frame-level processing.
- `scripts/train_yolo.py` is the runnable training command.
- `scripts/validate_dataset.py` validates exported dataset structure.
- Concrete checkpoint facts belong in `docs/model-registry.md`.
- Runtime module contracts belong in `docs/architecture.md`.
- Held-item temporal and geometry behavior belongs in
  `docs/held-item-association.md`.
- Detailed workflows live in
  `.agents/skills/mk8dx-item-alert-system/`.

Do not restore deleted compatibility entrypoints, experimental snapshots, or
root-level training scripts. Git history is the archive.

## Python And Runtime Policy

- Keep capture, model loading, inference, association, tracking, ranking,
  overlay, display, and writing behind separate boundaries.
- Avoid import-time model loading, capture, network access, or training.
- Preserve raw model labels exactly. Add canonical names in mapping code.
- Runtime must never download models implicitly.
- Legacy six-class detections are not proof of held state.
- Integrated alerts require an opponent track and temporal confirmation.
- Runtime tracker IDs must never be treated as ground-truth identities;
  evaluation matches held alerts by opponent bbox, negative causes by item bbox,
  and scopes lead time by event.
- Legacy mode must run without the optional `tracking` extra. Integrated mode
  must fail clearly when it is unavailable.
- Keep pure behavior testable without a camera or YOLO checkpoint.

## Data And Artifact Policy

- Keep datasets, videos, frame dumps, predictions, benchmarks, YOLO runs,
  virtual environments, and model binaries out of Git.
- Track model metadata and hashes in `models/manifest.toml`.
- Publish approved checkpoints as versioned GitHub Release assets, not normal
  Git or Git LFS.
- Do not publish models or alert icons until provenance and redistribution
  rights are recorded.

## Verification

Fresh-clone checks do not require datasets or model binaries:

```bash
python -m pip install -e ".[dev]"
pytest -q
RUFF_CACHE_DIR=/tmp/mk8dx-ruff ruff check .
python -m compileall src scripts tests
mk8dx-alert --help
```

When authorized promoted models are present under ignored `models/`, also run:

```bash
mk8dx-alert models verify
```

Run dataset validation before training. Do not report model accuracy, held-item
quality, FPS, or latency unless the corresponding command was run and inspected.
