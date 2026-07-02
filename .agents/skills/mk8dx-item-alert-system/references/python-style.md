# Python Style

## Module Design

- Use typed functions where practical.
- Avoid global mutable runtime state when refactoring.
- Keep import-time side effects out of modules.
- Use `if __name__ == "__main__"` for executable scripts.
- Prefer dataclasses or config objects for thresholds, paths, class names,
  regions, and output settings.

## Extraction Targets

When extracting from `detect.py`, prefer modules like:

```text
src/mk8dx_item_alert/
  config.py
  capture.py
  models.py
  gating.py
  detection.py
  overlay.py
  smoothing.py
  evaluation.py
```

Runnable commands should live under `scripts/`.

## Testable Logic

Keep pure functions testable without a camera or YOLO model. Good test targets
include:

- Label canonicalization.
- Region calculations.
- Alert TTL and smoothing.
- Overlay placement and clipping.
- Priority ordering for multiple detections.

## Runtime Boundaries

OpenCV capture, YOLO inference, and video writing are side-effectful. Keep them
behind small interfaces so the rest of the pipeline can be tested.
