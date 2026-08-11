# YOLO Training Guidance

Use `scripts/train_yolo.py`; importing project modules must never start
training. The command exposes dataset path, base model, image size, epochs,
augmentation values, output project/name, and device.

Run `scripts/validate_dataset.py` before training. The integrated dataset must
use the exact seven-class order documented in `held-item-association.md`.

For every run, record:

- Exact command and package versions.
- Dataset name/version and split policy.
- Label order and annotation policy.
- Base model, image size, epochs, augmentations, and device.
- Precision, recall, mAP50, mAP50-95, and confusion matrix.
- Held, thrown, dropped, background, HUD, distance, and occlusion failures.
- Checkpoint SHA-256 and storage state.

Training outputs remain under ignored `runs/`. Promotion requires updating the
model registry and manifest. A model must not be uploaded while artifact
provenance or redistribution rights are unresolved.
