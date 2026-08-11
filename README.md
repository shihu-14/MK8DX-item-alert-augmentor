# MK8DX Item Alert Augmentor

A local research prototype that detects item candidates visible around Mario
Kart 8 Deluxe opponents and renders clearer alerts on captured gameplay.

The checked-in runtime models are intentionally not described as full
held-item detection. The current six-class item model sees item-like objects,
and the one-class gate model detects the configured `Face` cue. A true held
alert requires the integrated seven-class model, opponent tracking, spatial
association, and temporal confirmation implemented by this repository.

This project is for local research, offline evaluation, and documentation, not
unfair online competitive use.

## Setup

Python 3.11 or newer is required.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Models

Model binaries are ignored by Git. Authorized local copies belong in
`models/` using the filenames in `models/manifest.toml`.

```bash
mk8dx-alert models verify
mk8dx-alert models install
```

Installation is currently unavailable because the Release URLs remain empty
until redistribution rights are confirmed. Runtime never downloads models
implicitly.

Current local model roles:

- `mk8dx-item-yolov8n-v9.pt`: legacy six-class item detector.
- `mk8dx-gate-yolov8n-v5.pt`: one-class gate detector.

## Realtime

```bash
mk8dx-alert run --source 0
mk8dx-alert run --source gameplay.mp4 --no-save --profile
```

Use `--no-gate` to evaluate without the rear-view gate. Use `--item-model`
or `--gate-model` for an explicit local checkpoint. Legacy mode prints a
warning because item detections are not proof of held state.

## Training And Evaluation

```bash
python scripts/validate_dataset.py data/yolo/<dataset-version>
python scripts/train_yolo.py --data data/yolo/<dataset-version>/data.yaml
mk8dx-alert evaluate --ground-truth truth.jsonl --predictions predictions.jsonl
```

The integrated model uses the existing six item labels in their current order
and appends `Opponent`. Only held, dragged, or orbiting items are positives;
thrown, dropped, course, background, and HUD examples are negatives.

Integrated ByteTrack mode uses the declared `lap` dependency. The runtime
still checks for it explicitly and never invokes Ultralytics' auto-installer.

## Development

```bash
pytest -q
RUFF_CACHE_DIR=/tmp/mk8dx-ruff ruff check .
```

See `docs/system-spec.md`, `docs/model-registry.md`,
`docs/evaluation-protocol.md`, and the repository Skill under
`.agents/skills/mk8dx-item-alert-system/`.

Model and icon provenance is not yet established. Do not publish those
artifacts until `docs/artifact-provenance.md` records authorization.
