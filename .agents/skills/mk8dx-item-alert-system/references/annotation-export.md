# Annotation Export Contract

Annotation is performed outside this repository. Export a versioned YOLO
detection dataset:

```text
data/yolo/<dataset-version>/
  data.yaml
  train/{images,labels}/
  val/{images,labels}/
  test/{images,labels}/
```

Each nonempty label line is:

```text
class_id x_center y_center width height
```

All coordinates are normalized to `[0, 1]`. Preserve this exact class order:
`Boomerang`, `FB`, `Minacle-Eight`, `Piranha-Plant`, `Super-Horn`,
`green-shell3`, `Opponent`.

Annotate opponent boxes and items still held, dragged, or orbiting that
opponent. Do not annotate thrown or dropped items as positive item boxes.
Include them as negative situations, together with course decorations, HUD,
item-like backgrounds, and frames without held items.

Split by gameplay situation rather than near-duplicate frame. Cover course,
lighting, character/vehicle, rear view, distance, multiple opponents,
occlusion, and item-use transitions. Record source clips and export rules in
dataset metadata, but keep all dataset contents local.
