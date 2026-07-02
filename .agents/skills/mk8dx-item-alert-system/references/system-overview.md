# System Overview

## Goal

This project builds a local item-alert augmentation system for Mario Kart 8
Deluxe. Opponent characters can visibly hold their current item before throwing,
dropping, or activating it. Skilled players can briefly check rear view and infer
the threat, but the item is small, often visible only briefly, and easy to miss.

The system aims to detect that held item from the actual gameplay or camera feed
and display an alert icon on an edge of the screen or another visible area.

## Held-Item Detection Is Not Thrown-Item Alerting

In-game alerts usually warn after an item is already active, incoming, or near
the player. This project targets an earlier signal: the opponent's held item.
That means item context matters:

- A held item is visually attached to, carried by, dragged behind, or orbiting an
  opponent.
- A thrown item moves independently after use.
- A dropped item remains on the road or track surface.
- Course decoration can resemble an item but is not a gameplay threat.

The current prototype detects item-like objects in selected regions. Future
refactors should add opponent/item association and temporal checks before making
strong claims that an item is held.

## Current Prototype

The current runtime prototype is `detect.py`. It uses OpenCV for capture and
overlay, Ultralytics YOLO for item detection, and a face/button-like gate region
to decide whether to run item detection.

`train.py` records training history and metrics for several item and gate/face
models. `main.py`, `tmp1.py`, and `tmp2.py` are experimental snapshots.

## Runtime Pipeline

1. Capture a frame from the gameplay/camera input.
2. Run optional gate detection, such as a face/button-like region check.
3. Mask or crop irrelevant screen regions.
4. Run YOLO item detection on the selected frame/ROI.
5. Map model labels to canonical item names and alert icon files.
6. Filter detections by confidence.
7. Optionally stabilize detections over time.
8. Render alert icons into the realtime output frame.
9. Show the output and optionally save annotated video.

## Refactoring Direction

Keep behavior stable first. Extract config, model loading, gating, detection,
overlay, smoothing, and evaluation in small steps. Do not turn the repository
into a generic detector; preserve the MK8DX held-item alert purpose.
