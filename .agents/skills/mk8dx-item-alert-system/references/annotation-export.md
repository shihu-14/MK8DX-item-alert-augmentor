# Annotation Export Contract

Annotation is done outside Codex. This reference documents the exported dataset
contract that Codex can work with in files, scripts, configs, and docs.

Codex should not perform manual annotation and should not write GUI annotation
tool instructions.

## Expected YOLO Detection Layout

Use a versioned exported dataset directory:

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

The dataset version should identify the source clips, labeling rules, label set,
and export date or run identifier.

## Expected `data.yaml`

`data.yaml` should define:

- Train, validation, and optional test image paths.
- Number of classes.
- Class names in the exact model-label order.

Preserve label order between dataset exports, training configs, model registry
entries, and runtime class mappings. If a label name contains a spelling issue,
document it and keep the raw model label stable unless a migration is planned.

## Label File Format

Each image has a matching `.txt` label file using normalized YOLO boxes:

```text
class_id x_center y_center width height
```

Coordinates are normalized to image width and height.

## Split Guidance

Separate train/val/test by gameplay situation where possible rather than using
only near-duplicate frames. Consider separation by:

- Course or scene.
- Rear-view versus normal-view capture.
- Distance to opponent.
- Lighting and effects.
- Held, thrown, dropped, and background-negative situations.

## Negative Examples

Include negative frames or labels that cover:

- Thrown items.
- Dropped items.
- Course decorations.
- HUD/UI objects.
- Item-like background objects.
- Frames without held items.

These examples are important because this project should avoid alerting on
objects that are not opponent-held items.

## Special Held-Item Cases

Dataset notes should document whether and how labels cover:

- Items held in hand.
- Items dragged behind a kart.
- Orbiting items such as shells.
- Multiple opponents in one frame.
- Partial occlusion.
- Rear-view mirror and brief-visibility cases.

## Codex Boundary

Codex may update exported-file checks, training scripts, config schemas,
documentation, and registry entries. Manual frame labeling and GUI annotation
procedures remain outside Codex.
