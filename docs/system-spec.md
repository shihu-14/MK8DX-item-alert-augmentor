# System Spec

## Project Purpose

This repository builds a local item-alert augmentation system for Mario Kart 8
Deluxe. The player can briefly check rear view and see opponents holding their
current items, but those items are small and visible only briefly. The system
aims to detect the opponent's currently held item from the gameplay screen and
display a clearer alert icon.

## Why Held Items Matter

Held-item detection is earlier than thrown-item alerting. Existing in-game
alerts tend to warn after an item is incoming, thrown, or activated. This project
tries to warn when an opponent is still holding the item.

The important distinction is state:

- Held: attached to or moving with an opponent.
- Thrown/projectile: moving independently after use.
- Dropped: placed on the road or track.
- Background/UI: not a held opponent item.

The current prototype detects item-like objects in selected regions. A future
held-item classifier should use opponent association and temporal behavior.

## Current Entry Points

- `detect.py`: current main realtime prototype.
- `train.py`: YOLO training-history/reference script.
- `main.py`, `tmp1.py`, `tmp2.py`: experimental snapshots.

## Runtime Pipeline

1. Capture frame from gameplay/camera input.
2. Optionally run gate detection to decide whether item detection should run.
3. Mask or crop irrelevant regions.
4. Run YOLO item detection.
5. Map model labels to canonical item names and alert icons.
6. Filter by confidence and optionally stabilize over time.
7. Render alert overlay.
8. Show and optionally save annotated output.

## Non-Goals For The Current Documentation Pass

- Do not fully rewrite the implementation.
- Do not remove existing experimental scripts.
- Do not rename model labels in code.
- Do not invent benchmark results.
