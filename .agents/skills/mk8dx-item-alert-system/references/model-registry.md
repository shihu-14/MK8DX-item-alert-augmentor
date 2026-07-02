# Model Registry Guidance

## Purpose

The model registry documents what each checkpoint is for and what evidence
exists for its quality. This avoids silently swapping item models, gate models,
or experimental weights.

## Required Fields

Record the following for each checkpoint:

- Filename.
- Purpose.
- Runtime usage.
- Dataset/version.
- Label set.
- Metrics.
- Confusion matrix or run artifact location.
- Known failure cases.
- Storage location.
- Notes about uncertainty.

## Current Checkpoint Names

Known checkpoint names in the current repository include:

- `best.pt`
- `best2.pt`
- `best_24.pt`
- `best_29.pt`
- `best_30.pt`
- `yolov8n.pt`
- `yolov8n-face.pt`

Use `docs/model-registry.md` as the human-readable table. Do not invent missing
metrics; use `unknown` when the source is not documented.
