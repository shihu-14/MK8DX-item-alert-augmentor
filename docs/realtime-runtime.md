# Realtime Runtime

## Input Assumptions

The current prototype uses OpenCV capture through `cv2.VideoCapture(0)`.
Depending on the local setup, this may refer to a camera, capture card, or
virtual camera. Realtime behavior depends on the input device, frame size, and
system performance.

The refactored runtime lives in `mk8dx_item_alert.runtime.run_realtime`.
Use `python scripts/run_realtime.py` for the script entrypoint. `python
detect.py` remains a compatibility wrapper.

## Frame Size Assumptions

The realtime runtime derives frame width and height from the first captured
frame, then uses config defaults that preserve the original proportional and
fixed regions. Any change in capture resolution, layout, or crop can require
recalibration.

## Gate Region

The current prototype uses a fixed gate/face region to decide whether item
detection should run. This is a proxy for the gameplay condition where the
player briefly checks rear view or a face/button-like visual cue appears.

Future config should expose:

- Gate region center and size.
- Gate threshold.
- Gate model path.
- Option to disable gate detection for offline evaluation.

See `docs/configuration-spec.md` for the broader configuration target.

## Item Detection Region

The prototype masks upper and lower screen regions and masks the gate region
before running item detection. Future config should expose:

- Upper/lower crop ratios.
- Additional ignored regions.
- Input image size.
- Confidence threshold.

These values should move into config gradually while preserving current
behavior.

## Command-Line Options

The first refactored script exposes:

```text
--source
--no-save
--debug
```

Configuration design is documented in `docs/configuration-spec.md`. The first
implementation pass uses dataclass defaults and does not load TOML/YAML config
files yet.

## Runtime Boundaries

Keep these concerns separable:

- Capture.
- Gate inference.
- Item inference.
- Alert state/smoothing.
- Overlay rendering.
- Display.
- Video writing.
