# Realtime Inference Guidance

## Low-Latency Principles

Realtime performance matters because the held item may be visible only briefly.
The runtime should minimize avoidable latency and make expensive steps optional.

## Frame Loop Rules

- Load models before entering the frame loop.
- Avoid blocking I/O inside the frame loop.
- Keep capture, inference, overlay, and video writing separable.
- Make video writing optional because it can affect latency.
- Avoid per-frame debug printing unless a debug flag is enabled.
- Reuse resized icons and static masks where practical.

## Configurable Runtime Values

Move these values into config gradually:

- Camera/input source.
- FPS target.
- Input image size.
- Item confidence threshold.
- Gate confidence threshold.
- Gate/crop regions.
- Item detection mask regions.
- Alert duration.
- Output path.
- Debug flag.

## Frame Skipping And Smoothing

If inference is slower than capture:

- Run YOLO every N frames and track/stabilize alerts between detections.
- Keep recent detections for a short TTL.
- Require detections to persist for multiple frames before high-confidence
  alerts.
- Decay alerts quickly when no supporting detections appear.

## Profiling

When optimizing, measure:

- Capture time.
- Gate inference time.
- Item inference time.
- Overlay time.
- Video writing time.
- End-to-end frame latency.
- Effective FPS.

Do not claim FPS or latency improvements unless they were measured.
