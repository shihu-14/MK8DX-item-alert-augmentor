# Realtime Runtime

## Input Assumptions

The current prototype uses OpenCV capture through `cv2.VideoCapture(0)`.
Depending on the local setup, this may refer to a camera, capture card, or
virtual camera. Realtime behavior depends on the input device, frame size, and
system performance.

## Frame Size Assumptions

`detect.py` derives frame width and height from the first captured frame, then
uses hard-coded proportional or fixed regions. Any change in capture resolution,
layout, or crop can require recalibration.

## Gate Region

The current prototype uses a fixed gate/face region to decide whether item
detection should run. This is a proxy for the gameplay condition where the
player briefly checks rear view or a face/button-like visual cue appears.

Future config should expose:

- Gate region center and size.
- Gate threshold.
- Gate model path.
- Option to disable gate detection for offline evaluation.

## Item Detection Region

The prototype masks upper and lower screen regions and masks the gate region
before running item detection. Future config should expose:

- Upper/lower crop ratios.
- Additional ignored regions.
- Input image size.
- Confidence threshold.

## Expected Command-Line Options

Future scripts should expose options such as:

```text
--source
--item-model
--gate-model
--conf-threshold
--gate-threshold
--imgsz
--output
--no-save
--debug
--profile
```

## Runtime Boundaries

Keep these concerns separable:

- Capture.
- Gate inference.
- Item inference.
- Alert state/smoothing.
- Overlay rendering.
- Display.
- Video writing.
