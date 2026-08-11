# Dataset Policy

Dataset content is local-only under `data/yolo/<dataset-version>/` and is
ignored by Git. Keep only contracts, metadata templates, and aggregate evidence
in the repository.

The integrated export uses:

```text
data/yolo/<dataset-version>/
  data.yaml
  train/{images,labels}/
  val/{images,labels}/
  test/{images,labels}/
```

Each nonempty YOLO label line is:

```text
class_id x_center y_center width height
```

All coordinates are normalized to `[0, 1]`. Preserve this exact class order:
`Boomerang`, `FB`, `Minacle-Eight`, `Piranha-Plant`, `Super-Horn`,
`green-shell3`, `Opponent`. Class IDs 0 through 5 therefore preserve the
current item-model order, and ID 6 is `Opponent`.

Run `python scripts/validate_dataset.py <dataset>` before training.

Annotate opponent boxes and items while held, dragged, or orbiting. Thrown and
dropped items are negative situations, as are course decorations, HUD objects,
background lookalikes, and frames with no held item.

Separate train/validation/test by gameplay situation where possible. Record
course, capture direction, distance, lighting, character/vehicle, occlusion,
multiple opponents, and item-state transitions. Do not use near-duplicate frame
splits as primary evidence. Dataset metadata must record source clips and the
annotation/export rules used for that version, without committing the clips or
exported dataset.
