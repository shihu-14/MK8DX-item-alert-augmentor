# Realtime Runtime

`mk8dx-alert run` is the only supported entrypoint. It opens a camera index or
video path, derives fixed regions from the first frame, processes that frame
without discarding it, and releases capture, writer, and windows on exit.

The runtime loads models and alert icons before the loop. The frame processor
reuses a static mask, optionally runs the gate, normalizes detections, performs
association/tracking/ranking, and returns display-ready alerts.

## Options

```text
--source
--item-model
--gate-model
--no-gate
--no-save
--debug
--profile
--predictions-jsonl
```

`--predictions-jsonl` writes one evaluation record per processed frame. See
`docs/evaluation-protocol.md` for the schema and matching rules.

## Profiling Definition

The first frame establishes dimensions and static resources and is processed
normally, but is excluded from the measurement window. Profiling samples do not
change frame processing; `--profile` only controls whether the collected
summary is printed.

Measured stages are:

- `capture`: `VideoCapture.read` for a measured frame.
- `gate`: gate crop, inference, thresholding, or the disabled-gate check.
- `mask`: application of the static item-region mask on gate-active frames.
- `item_inference`: item model call and confidence filtering.
- `association_tracking_ranking`: association, temporal state, and ranking.
- `overlay`: debug boxes and alert rendering.
- `prediction_write`: optional evaluation JSONL serialization/write.
- `display`: `imshow` and `waitKey`.
- `video_write`: optional annotated-video write.

`processed_frame` is wall-clock latency from the start of `capture` through
completion of pipeline processing, overlay, display, and enabled writes for one
measured frame. It excludes model/icon loading, capture opening, first-frame
initialization, and display scanout. It must not be described as
capture-to-photon or whole-system end-to-end latency.

Effective FPS is `measured processed frames / measurement wall-clock seconds`,
from immediately before the first measured capture through completion of the
last measured frame. It is not derived from average frame latency.

The benchmark target is 30 effective FPS with p95 `processed_frame` latency at
or below 100 ms for a fixed 1080p source. No result is claimed until tested on
the target hardware.

Video writing is enabled by default and writes under ignored `outputs/`.
Disable it when measuring inference latency.

Ultralytics ByteTrack requires the optional `tracking` extra. Legacy mode runs
without `lap`. Integrated mode checks for it before tracking and refuses
Ultralytics' implicit installation path if the environment is incomplete.
