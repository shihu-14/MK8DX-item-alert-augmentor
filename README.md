# MK8DX Item Detection

This repository is a local research prototype for an item-alert augmentation
system for Mario Kart 8 Deluxe. It detects opponent-held items from a live
gameplay or camera feed and renders alert icons on the realtime video output.

The project is not a generic object-detection demo. The core motivation is that
opponents visibly hold items before throwing or activating them. Seeing that
held item early can provide a clearer warning than alerts that appear only after
an item is already active.

## Current Prototype Status

- `detect.py` is the current main runtime prototype.
- `train.py` is the current YOLO training-history/reference script.
- `main.py`, `tmp1.py`, and `tmp2.py` are experimental snapshots.
- The prototype uses OpenCV and Ultralytics YOLO.
- It captures frames, applies a face/button-like gate region, runs item
  detection, maps detected classes to alert image files, and overlays alert
  icons.

The current prototype detects item-like objects in selected regions. It does not
yet fully prove that a detected item is held by a specific opponent rather than
thrown, dropped, or part of the course background.

## Required Local Files

Runtime depends on local model checkpoints and alert image files. Current
prototype paths include:

- `runs/detect/train/weights/best_29.pt` for item detection.
- `runs/detect/train/weights/best_30.pt` for gate/face detection.
- Alert icons such as `Piranha-Plant.png`, `Super-Horn.png`, `FB.png`,
  `Boomerang.png`, `Minacle-Eight.png`, and `Green-Shell3.png`.

Some checkpoints are currently tracked for continuity, but new model artifacts
should not be committed by default. See `docs/model-registry.md` and
`docs/dataset-policy.md`.

Annotation is external to this repository workflow. Exported YOLO datasets
should follow `docs/dataset-policy.md` and
`.agents/skills/mk8dx-item-alert-system/references/annotation-export.md`.

## Setup

Create a local Python environment and install dependencies:

```bash
python -m venv yolovenv
source yolovenv/bin/activate
pip install -e ".[dev]"
```

If editable install is not needed:

```bash
pip install opencv-python numpy ultralytics
```

## Run

The current prototype is script-based:

```bash
python detect.py
```

Future runnable commands should move under `scripts/`, for example:

```bash
python scripts/run_realtime.py --config configs/local.yaml
```

Realtime use depends on local camera/gameplay capture setup, frame size, gate
region calibration, and checkpoint availability.

## Documentation

- System spec: `docs/system-spec.md`
- Class labels: `docs/class-labels.md`
- Model registry: `docs/model-registry.md`
- Configuration spec: `docs/configuration-spec.md`
- Dataset policy: `docs/dataset-policy.md`
- Evaluation protocol: `docs/evaluation-protocol.md`
- Realtime runtime: `docs/realtime-runtime.md`
- Alert overlay: `docs/alert-overlay-spec.md`
- Local data layout: `data/README.md`

YOLO metrics are necessary but not sufficient for this project. Evaluation also
needs held-item alert behavior, including early alerts, missed held items,
thrown/dropped/background false alerts, gate errors, FPS, and latency.

## Artifact Policy

Raw videos, datasets, generated videos, debug dumps, prediction outputs, YOLO
runs, and new model checkpoints should stay local unless a task explicitly asks
to publish them. Keep lightweight documentation and reproducible notes in git.

## Scope

This project is intended for local research, offline testing, and documentation.
It should not be used to create unfair online competitive assistance.
