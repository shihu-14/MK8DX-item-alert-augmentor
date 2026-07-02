# Model Registry

Use `unknown` when a field is not documented by current files. Do not infer
metrics from nearby runs.

| Checkpoint | Purpose | Used by | Dataset/version | Label set | Metrics | Artifact location | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `runs/detect/train/weights/best_29.pt` | Item detection | `scripts/run_realtime.py`, `detect.py` | `Item_Detection.v9-original-v2.yolov8` | Boomerang, FB, Minacle-Eight, Piranha-Plant, Super-Horn, green-shell3 | all: P 0.828, R 0.778, mAP50 0.795, mAP50-95 0.49, from `train.py` notes | `runs/detect/train/weights/best_29.pt` | Current main item model. |
| `runs/detect/train/weights/best_30.pt` | Gate/face detection | `scripts/run_realtime.py`, `detect.py` | `Face-Detection.v5-original-v1.yolov8` | Face | all: P 0.987, R 0.994, mAP50 0.992, mAP50-95 0.765, from `train.py` notes | `runs/detect/train/weights/best_30.pt` | Current main gate/face model. |
| `runs/detect/train/weights/best_24.pt` | Item detection | Historical/reference | `Item_Detection.v8-full-items-v4.yolov8` | Boomerang, FB, Minacle-Eight, Piranha-Plant, Super-Horn, green-shell3 | all: P 0.834, R 0.746, mAP50 0.793, mAP50-95 0.454, from `train.py` notes | `runs/detect/train/weights/best_24.pt` | Historical item checkpoint. |
| `runs/detect/train/weights/best.pt` | Item detection | `archive/experimental/main.py`, `archive/experimental/tmp1.py`, `archive/experimental/tmp2.py` | unknown | Current file appears to expose item labels, but source run is unknown | unknown | `runs/detect/train/weights/best.pt` | Ambiguous historical/latest item checkpoint. |
| `runs/detect/train/weights/best2.pt` | Gate/face detection | `archive/experimental/tmp2.py` | unknown | Face | unknown | `runs/detect/train/weights/best2.pt` | Historical gate/face checkpoint. |
| `yolov8n.pt` | Base/pretrained model | `train.py` | upstream/base | COCO/base labels, not documented here | not applicable | `yolov8n.pt` | Used as training base in current script. |
| `yolov8n-face.pt` | Face model/checkpoint | `archive/experimental/tmp1.py` | unknown | unknown | unknown | `yolov8n-face.pt` | Historical experimental face model. |

## Registry Maintenance

For each new checkpoint, record:

- Purpose and intended entrypoint.
- Dataset version and label set.
- Train command/config.
- Precision, recall, mAP50, mAP50-95.
- Confusion matrix location.
- Known failure cases.
- Whether it is committed, local-only, or stored externally.
