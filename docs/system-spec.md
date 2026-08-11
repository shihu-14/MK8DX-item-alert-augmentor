# System Spec

## Goal

Detect an item while it is visibly associated with an opponent, before it is
thrown, dropped, or activated, and render an alert ordered by estimated
opponent proximity.

Held state requires all of:

1. An integrated detector output for `Opponent` and a supported item.
2. A tracker ID for the opponent.
3. Spatial item/opponent association.
4. Association in at least three of five inference frames.

Thrown, dropped, background, course, and HUD detections must not produce held
alerts.

## Runtime Modes

Legacy mode accepts the promoted six-class item model and produces candidate
alerts for continuity. It emits a warning and must not be reported as verified
held detection.

Integrated mode accepts the six item labels followed by `Opponent`, uses
ByteTrack IDs, confirms association over time, and ranks alerts.

## Estimated Distance

Distance rank is a visual heuristic, not absolute depth and not race position.
It uses smoothed opponent bounding-box height, then box-bottom position. Item
box size is excluded because item classes differ physically.

## Gate

The one-class `Face` detector is an optional rear-view proxy and performance
gate. Its recorded YOLO mAP does not establish end-to-end gate correctness.
Offline evaluation can disable it.
