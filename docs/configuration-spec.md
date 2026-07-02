# Configuration Spec

This document describes what should eventually move out of hard-coded script
constants and into configuration. It is a documentation/spec pass; do not
implement a config system until the change is behavior-preserving and scoped.

The first implementation refactor stores current defaults in
`mk8dx_item_alert.config.RuntimeConfig`. It does not load YAML or TOML files yet.

## Runtime Model Paths

Configuration should include:

- Item model path.
- Gate/face model path.

## Class And Icon Mapping

Configuration should map:

- Raw model label.
- Canonical item name.
- Display name.
- Alert icon path.

Raw model labels should remain stable for compatibility. Canonical names and
display names can be added in mapping layers.

## Thresholds

Configuration should include:

- Item confidence threshold.
- Gate confidence threshold.
- Optional smoothing threshold.

## Regions

Configuration should include:

- Gate region.
- Item detection mask/crop region.
- Ignored screen regions.

Regions should document whether values are absolute pixels, ratios, or derived
from frame dimensions.

## Input And Output

Configuration should include:

- Camera/source id.
- Optional video file source.
- Output video path.
- Save/no-save flag.
- Debug/profile flags.

## Realtime Behavior

Configuration should include:

- Alert duration.
- Frame skipping.
- Temporal smoothing TTL.
- Multiple detection priority.

## Future Config Format

YAML or TOML would both work. YAML is convenient for nested runtime settings;
TOML is convenient when aligning with Python tooling. Do not force a format
until the first behavior-preserving extraction is implemented.

Example sketch:

```yaml
models:
  item: runs/detect/train/weights/best_29.pt
  gate: runs/detect/train/weights/best_30.pt

thresholds:
  item_confidence: 0.45
  gate_confidence: 0.45
  smoothing: 0.5

regions:
  gate:
    center_x_offset: 100
    center_y_offset: 200
    width: 430
    height: 360
  item_mask:
    upper_ratio: 0.23
    lower_ratio: 0.8
  ignored: []

input:
  source: 0

output:
  save: true
  video_path: output_video_new21.mp4
  debug: false
  profile: false

alerts:
  duration_sec: 2.5
  frame_skip: 1
  temporal_ttl_sec: 0.5
  priority: ["confidence", "proximity", "recency"]

labels:
  - raw: Piranha-Plant
    canonical: piranha_plant
    display: Piranha Plant
    icon: assets/icons/alerts/Piranha-Plant.png
```
