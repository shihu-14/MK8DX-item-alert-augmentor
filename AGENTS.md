# MK8DX Item Alert Agent Guide

## Project Purpose

This repository is a local research prototype for Mario Kart 8 Deluxe held-item
alerts. It detects opponent-held items from gameplay/camera frames before the
item is thrown or activated, then renders alert icons on the realtime output.
It is not a generic object-detection repository.

Keep the project intended for local research, offline testing, and
documentation, not for unfair online competitive use.

## Source Of Truth

- `detect.py` remains the compatibility entrypoint for the realtime prototype.
- `src/mk8dx_item_alert/runtime.py` contains the refactored realtime runtime.
- `train.py` is the current YOLO training-history/reference script.
- `archive/experimental/main.py`, `archive/experimental/tmp1.py`, and
  `archive/experimental/tmp2.py` are historical snapshots. Do not delete them in
  routine cleanup.
- Detailed procedures live in `.agents/skills/mk8dx-item-alert-system/` and
  `docs/`.

## Development Policy

- Preserve current behavior before refactoring.
- Do not create more top-level experimental scripts such as `tmp3.py`.
- Put reusable code under `src/`.
- Put runnable commands under `scripts/`.
- Move hard-coded paths, thresholds, class names, crop regions, and output
  filenames into config gradually.

## Python/CV Code Policy

- Keep model loading, capture, gate detection, item detection, overlay rendering,
  smoothing, and video writing separable.
- Avoid import-time side effects when extracting modules.
- Prefer typed functions and config objects for thresholds, paths, and regions.
- Keep pure logic testable without a camera or YOLO model.

## Data And Artifact Policy

- Do not newly commit raw videos, datasets, generated videos, debug dumps,
  prediction outputs, or model checkpoints by default.
- Existing tracked artifacts should be documented before changing or replacing
  them.
- Keep local data under `data/` as described in `data/README.md`.

## Testing And Evaluation

- Do not claim training, inference, FPS, or evaluation was run unless actually
  run.
- When detection logic changes, compare before/after precision, recall, mAP,
  false alerts, missed held items, gate errors, FPS, and latency where possible.

## Codex Behavior

- Use the repo skill `mk8dx-item-alert-system` for MK8DX item alerts, held item
  detection, YOLO training/inference, OpenCV realtime capture, gate detection,
  alert overlay work, model registry updates, evaluation, and pipeline
  refactoring.
- Keep `AGENTS.md` short. Put detailed YOLO, annotation, artifact, and runtime
  procedures in docs or skill references.
- Keep reusable workflows in the repo skill and put concrete labels,
  checkpoints, metrics, calibration values, and experiment notes in docs or
  references.
