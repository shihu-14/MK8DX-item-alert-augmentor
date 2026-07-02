# Evaluation Protocol

## Detection Metrics

Record standard YOLO metrics for item and gate models:

- Precision.
- Recall.
- mAP50.
- mAP50-95.
- Confusion matrix.

Keep metrics tied to a specific checkpoint, dataset version, label set, image
size, and confidence threshold.

## Runtime Metrics

For realtime changes, record:

- FPS.
- Average latency.
- Per-stage latency when possible.
- False alerts.
- Missed held items.
- Gate false positives.
- Gate false negatives.

## Held-Item Evaluation

Because this project targets held items, evaluate separately from generic item
detection:

- Correct alert for an opponent-held item.
- No alert for dropped road items.
- No alert for thrown/projectile items unless explicitly intended.
- No alert for course decoration or HUD elements.
- Correct handling of multiple simultaneous detections.

## Before/After Requirement

When changing detection logic, compare before and after using the same sample
set or video segment. Report only metrics that were actually measured.

## Evidence Policy

Do not claim training, inference, or evaluation was run unless the command was
actually executed and the output was inspected. If only documentation changed,
say that no runtime evaluation was performed.
