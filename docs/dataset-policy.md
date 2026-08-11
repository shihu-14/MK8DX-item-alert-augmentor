# Dataset Policy

Dataset content is local-only under `data/yolo/<dataset-version>/` and is
ignored by Git. Keep only contracts, metadata templates, and aggregate evidence
in the repository.

The integrated export uses:

```text
data.yaml
train/{images,labels}/
val/{images,labels}/
test/{images,labels}/
```

Class IDs 0 through 5 preserve the current item model order; ID 6 is
`Opponent`. Run `python scripts/validate_dataset.py <dataset>` before
training.

Annotate opponent boxes and items while held, dragged, or orbiting. Thrown and
dropped items are negative situations, as are course decorations, HUD objects,
background lookalikes, and frames with no held item.

Separate train/validation/test by gameplay situation where possible. Record
course, capture direction, distance, lighting, character/vehicle, occlusion,
multiple opponents, and item-state transitions. Do not use near-duplicate frame
splits as primary evidence.
