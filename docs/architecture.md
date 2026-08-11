# Runtime Architecture

## Dependency Direction

`cli -> runtime -> pipeline -> inference/association/tracking/ranking`

`overlay`, `regions`, `labels`, and `config` provide focused helpers.
`model_store` is used only by explicit model-management commands.

## Module Boundaries

- `runtime.py`: capture, display, writers, model/icon lifecycle, and profiling.
- `pipeline.py`: gate, mask, detection, association, tracking, and ranking order.
- `inference.py`: Ultralytics loading/output normalization and label validation.
- `association.py`: deterministic item/opponent one-to-one matching.
- `tracking.py`: per-opponent temporal state and TTL geometry.
- `ranking.py`: estimated-proximity ordering.
- `overlay.py`: alert placement and drawing.
- `evaluation.py`: prediction JSONL serialization and offline metrics.
- `model_store.py`: explicit manifest verification and model installation.

## Contracts

- `Detection` is normalized model output with an optional runtime track ID.
- `AssociatedItem` binds one item detection to one opponent track for a frame.
- `TrackAlert` retains temporal state, current opponent geometry, and the last
  supporting item-detection geometry.
- `RankedAlert` is display- and evaluation-ready alert state.
- `FrameResult` carries detections, associations, alerts, mode, and timings.

Ultralytics result objects do not escape `inference.py`. OpenCV frames remain
array-like at module boundaries. Runtime tracker IDs are diagnostics and are
never treated as ground-truth identities.

## Side Effects

Only CLI, model-store, runtime, and training boundaries perform network access,
model loading, capture, display, writing, or training. Importing package modules
must not start those operations.

Models and icons load before the frame loop. The static mask is reused for a
fixed frame size. Video and prediction writers are optional and closed with the
capture and display resources.

## Modes

- Legacy mode uses the six item labels and produces candidate alerts only.
- Integrated mode appends `Opponent`, uses ByteTrack IDs, associates held-item
  evidence, confirms it temporally, refreshes opponent geometry, and ranks it.

Legacy output must not be represented as confirmed opponent-held evidence.
