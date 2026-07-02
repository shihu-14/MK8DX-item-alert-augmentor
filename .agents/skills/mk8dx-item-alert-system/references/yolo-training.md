# YOLO Training Guidance

## Purpose

YOLO training in this repository should support MK8DX held-item alerting, not a
generic object-detection benchmark. Training notes must preserve enough context
to connect a checkpoint to its dataset, labels, and intended runtime use.

## Script Structure

Training scripts should:

- Keep dataset paths configurable.
- Keep image size, epochs, augmentations, and model base configurable.
- Avoid hard-coded local absolute paths.
- Record the exact command or config used to produce each checkpoint.
- Save metrics and failure cases alongside the run notes.

`train.py` is currently a training-history/reference script. Future runnable
training commands should live under `scripts/`, for example
`scripts/train_yolo.py`.

## Required Run Records

For every checkpoint that is kept or referenced, record:

- Model/checkpoint filename.
- Purpose: item detection, gate/face/button detection, or other.
- Dataset name and version.
- Label set.
- Train command or config.
- Precision, recall, mAP50, and mAP50-95 when known.
- Confusion matrix location when known.
- Known failure cases.
- Storage location.

Use `unknown` when evidence is missing. Do not infer metrics from nearby runs.

## Dataset Format

Annotation itself is done outside Codex. Document only the expected exported
format. The expected format is YOLO detection format:

```text
dataset/
  data.yaml
  train/
    images/
    labels/
  valid/ or val/
    images/
    labels/
  test/
    images/
    labels/
```

Each label file should contain YOLO normalized bounding boxes:

```text
class_id x_center y_center width height
```

## Failure Cases To Track

Track examples where the model confuses:

- Held items with thrown or dropped items.
- Course decorations with gameplay items.
- Player HUD elements with world items.
- Distant small items with background objects.
- Gate/face detection false positives and false negatives.
