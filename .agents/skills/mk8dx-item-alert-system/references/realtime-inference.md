# Realtime Inference Guidance

## Frame Loop

- Load and validate models before capture starts.
- Build static masks once per frame size.
- Use the gate only when configured and measure gate errors separately.
- Use ByteTrack only with the integrated seven-class detector.
- Keep display and video writing outside frame processing.
- Never download a model or print per-frame diagnostics implicitly.

## Profiling

`--profile` reports average and p95 milliseconds for gate inference, item
inference, video writing, and the full processed frame. Benchmark with saving
disabled unless measuring writer cost.

The initial performance target is 30 effective FPS and p95 end-to-end frame
latency at or below 100 ms for a fixed 1080p input on the target machine. Record
hardware, input, package versions, and command. Do not claim this target from
model-reported inference time alone.

## Optimization Order

1. Disable optional video writing.
2. Reuse masks and icon assets.
3. Profile gate and item inference independently.
4. Reduce model input size only with before/after accuracy evidence.
5. Add frame skipping and track interpolation only if measured processing is
   slower than capture.
