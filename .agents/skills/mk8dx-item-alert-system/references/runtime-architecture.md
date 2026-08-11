# Runtime Architecture

## Dependency Direction

`cli -> runtime -> pipeline -> inference/association/tracking/ranking`

`overlay`, `regions`, `labels`, and `config` provide focused helpers.
`model_store` is used only by explicit model-management commands.

## Contracts

- `Detection` is the normalized model output and carries an optional track ID.
- `AssociatedItem` binds one item to one opponent track for a frame.
- `TrackAlert` is confirmed temporal state for one opponent.
- `RankedAlert` is display-ready estimated-distance ordering.
- `FrameResult` carries detections, associations, alerts, mode, and timings.
- Evaluation prediction JSONL carries frame gate state and integrated confirmed
  alert labels/opponent boxes; runtime tracker IDs remain diagnostic only.

OpenCV frames remain array-like values at module boundaries. Ultralytics result
objects must not escape `inference.py`.

## Side Effects

Only CLI/model store/runtime/training boundaries may perform network access,
model loading, capture, display, writing, or training. Importing package modules
must not start those operations.

The frame mask is created once for a fixed frame size. Models and icons are
loaded before the loop. Video output is optional and checked for successful
opening.

## Modes

- Legacy: six item classes, immediate candidate alerts, explicit warning.
- Integrated: six item classes plus `Opponent`, ByteTrack IDs, spatial
  association, three-of-five confirmation, and distance ranking.

Do not silently treat legacy output as integrated held-item evidence.
