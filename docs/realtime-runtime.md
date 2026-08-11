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
```

`--profile` reports average and p95 gate, item, writer, and total frame time.
The benchmark target is 30 FPS with p95 frame latency at or below 100 ms for a
fixed 1080p source. No result is claimed until tested on the target hardware.

Video writing is enabled by default and writes under ignored `outputs/`.
Disable it when measuring inference latency.

Ultralytics ByteTrack requires the declared `lap` dependency. The runtime
checks for it before tracking and refuses Ultralytics' implicit installation
path if the environment is incomplete.
