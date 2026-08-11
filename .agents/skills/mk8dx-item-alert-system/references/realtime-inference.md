# Realtime Inference Guidance

## Frame Loop

- Load and validate models before capture starts.
- Build static masks once per frame size.
- Use the gate only when configured and measure gate errors separately.
- Use ByteTrack only with the integrated seven-class detector.
- Keep display and video writing outside frame processing.
- Never download a model or print per-frame diagnostics implicitly.

## Profiling

`--profile` reports average and p95 milliseconds for capture, gate, mask, item
inference, association/tracking/ranking, overlay, display, enabled writes, and
the measured `processed_frame`. Benchmark with saving disabled unless measuring
writer cost. The first initialization frame is processed but excluded.

Effective FPS is measured-frame count divided by measurement wall-clock time.
`processed_frame` starts at capture and ends after display and enabled writes;
it excludes one-time setup and display scanout and is not capture-to-photon
latency. The initial target is 30 effective FPS and p95 `processed_frame` at or
below 100 ms for a fixed 1080p input. Record hardware, input, package versions,
and command. Do not claim this target from model-reported inference time alone.

## Optimization Order

1. Disable optional video writing.
2. Reuse masks and icon assets.
3. Profile gate and item inference independently.
4. Reduce model input size only with before/after accuracy evidence.
5. Add frame skipping and track interpolation only if measured processing is
   slower than capture.
