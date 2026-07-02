# Dataset Policy

## Local Layout

Keep datasets local by default. Suggested local layout:

```text
data/
  raw/
  annotated/
  yolo/
  samples/
```

`data/README.md` may be committed. Dataset contents should not be committed by
default.

## Annotation

Annotation is done outside Codex. This repository should document expected
formats and policies, not detailed GUI instructions for annotation tools.

## Expected YOLO Export

See `.agents/skills/mk8dx-item-alert-system/references/annotation-export.md`
for the repo skill's exported dataset contract.

Expected exported dataset layout:

```text
data/yolo/<dataset-version>/
  data.yaml
  train/
    images/
    labels/
  val/ or valid/
    images/
    labels/
  test/
    images/
    labels/
```

Each label file uses normalized YOLO detection boxes:

```text
class_id x_center y_center width height
```

## Splits

Use train/val/test splits that separate gameplay scenarios where possible.
Avoid evaluating only on frames that are near-duplicates of training frames.

Track coverage for:

- Characters and vehicles.
- Courses and lighting.
- Rear-view and normal-view frames.
- Near and distant opponents.
- Held, thrown, dropped, and background lookalikes.
- HUD and UI negatives.

## Commit Policy

Do not newly commit raw videos, extracted frame dumps, full datasets, generated
YOLO exports, or large derived artifacts by default. Commit lightweight docs,
metadata, and small illustrative samples only when explicitly useful.
