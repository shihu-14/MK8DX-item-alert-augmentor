---
name: mk8dx-item-alert-system
description: Use for MK8DX item alert work, held item detection, YOLO training/inference, OpenCV realtime capture, face/button-gated detection, alert overlay rendering, realtime FPS/latency improvement, model registry updates, evaluation protocol, and refactoring the detection pipeline.
---

# MK8DX Item Alert System

This repository is an early-alert augmentation for held Mario Kart 8 Deluxe
items. It is not a generic object detection project. The goal is to detect an
opponent's currently held item from the gameplay screen before it is thrown,
dropped, or activated, then render a visible alert.

## Runtime Pipeline

Use this conceptual pipeline when reasoning about runtime changes:

1. Capture a frame from gameplay/camera input.
2. Optionally apply gate detection to determine whether item detection should
   run.
3. Mask or crop irrelevant screen regions.
4. Run YOLO item detection.
5. Map detected labels to canonical item names and alert icons.
6. Apply confidence filtering and optional temporal stabilization.
7. Render the alert overlay.
8. Show or save annotated output.

## Refactoring Order

Refactor in this order unless a task gives a more specific direction:

1. Preserve behavior from `detect.py`.
2. Centralize config.
3. Extract model loading.
4. Extract gate detection.
5. Extract item detection.
6. Extract alert overlay rendering.
7. Add CLI scripts.
8. Add tests for pure logic.
9. Document runtime assumptions.

## Working Guidance

- Treat `detect.py` as the current main runtime prototype.
- Treat `train.py` as the training-history/reference script.
- Treat `main.py`, `tmp1.py`, and `tmp2.py` as experimental snapshots.
- Do not rename model labels in code without a compatibility mapping.
- Keep dataset paths configurable.
- Do not invent metrics, benchmark results, or evaluation status.
- Avoid adding new large artifacts to git.
- Prefer behavior-preserving extraction before redesign.

## Specific Guidance

- YOLO training scripts: keep dataset path, model base, image size, epochs, and
  augmentations configurable; record the command and metrics for each run.
- Model/checkpoint tracking: update `docs/model-registry.md` whenever a
  checkpoint is added, replaced, or promoted for runtime use.
- Realtime inference performance: load models outside the frame loop, make video
  writing optional, gate expensive inference, and measure FPS/latency before
  claiming improvement.
- Alert overlay behavior: document icon mapping, confidence threshold, display
  duration, placement, smoothing, and multiple-detection priority rules.
- Class-label mapping: preserve raw model labels and map them to canonical names
  in configuration or pure helper functions.
- Dataset artifact policy: keep datasets, raw videos, frame dumps, and new
  checkpoints local unless explicitly requested.
- Python style: use typed functions where practical, avoid import-time side
  effects, and use config/dataclass objects for paths, thresholds, and regions.

## Topic References

- System overview: `references/system-overview.md`
- YOLO training: `references/yolo-training.md`
- Realtime inference: `references/realtime-inference.md`
- Model registry: `references/model-registry.md`
- Artifact policy: `references/artifact-policy.md`
- Python style: `references/python-style.md`

## Done Criteria

A change is done only when the requested behavior or documentation exists in the
current tree, relevant assumptions are documented, and any claimed command,
training run, inference run, or metric is backed by actual evidence.
