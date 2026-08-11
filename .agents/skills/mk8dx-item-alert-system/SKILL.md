---
name: mk8dx-item-alert-system
description: Use for MK8DX held-item detection, YOLO training/inference, OpenCV capture, gate detection, opponent association, alert ranking, model distribution, evaluation, and runtime refactoring.
---

# MK8DX Item Alert System

## Goal And Claims

Build an early warning for items visibly held by opponents in Mario Kart 8
Deluxe. Keep held items distinct from thrown items, dropped items, course
objects, and HUD elements.

The legacy six-class model detects item-like objects only. Describe its output
as a candidate alert. Describe an alert as opponent-held only when the
integrated model detects an opponent, association succeeds, and temporal
confirmation passes.

## Runtime Pipeline

1. Capture a gameplay frame.
2. Optionally evaluate the rear-view gate.
3. Apply the static item-region mask.
4. Run the legacy or integrated YOLO detector.
5. Normalize YOLO output into typed detections.
6. Associate item detections with tracked opponents.
7. Confirm association in at least three of five inference frames.
8. Rank confirmed opponents by estimated proximity.
9. Render at most three fixed-layout alerts.
10. Optionally display, write, and profile output.

## Repository Boundaries

- `runtime.py`: resource lifecycle and frame loop.
- `inference.py`: Ultralytics adapter and label validation.
- `pipeline.py`: gate, mask, detection, and per-frame orchestration.
- `association.py`: opponent/item spatial association.
- `tracking.py`: per-opponent temporal state.
- `ranking.py`: estimated-distance ordering.
- `overlay.py`: placement, clipping, and drawing.
- `model_store.py`: explicit model verification and installation.
- `scripts/train_yolo.py`: training only.
- `scripts/validate_dataset.py`: exported dataset validation.

Do not add compatibility entrypoints or experimental snapshots. Use Git history
for obsolete code.

## Model And Artifact Rules

- Preserve the six existing raw item labels and their numeric order.
- Append `Opponent` as class 6 in an integrated seven-class model.
- Keep `.pt`, datasets, videos, runs, and generated output out of Git.
- Record promoted artifacts in `models/manifest.toml` and
  `docs/model-registry.md`.
- Use versioned GitHub Release assets after redistribution rights are confirmed.
- Runtime must not perform implicit downloads.
- Use unknown for undocumented evidence and never infer metrics.

## Evaluation Rules

- Validate a dataset before training.
- Compare legacy and integrated behavior on the same held/non-held clips.
- Report model metrics separately from held-alert metrics.
- Measure thrown, dropped, background, and HUD false alerts.
- Measure gate errors, lead timing, effective FPS, and p95 frame latency.
- Do not claim the 30 FPS / 100 ms target without a fixed 1080p benchmark.

## Topic References

- System behavior: `docs/system-spec.md`
- Runtime architecture: `references/runtime-architecture.md`
- Held association: `references/held-item-association.md`
- Realtime performance: `references/realtime-inference.md`
- Training: `references/yolo-training.md`
- Annotation/export: `references/annotation-export.md`
- Artifacts: `references/artifact-policy.md`
- Model registry: `docs/model-registry.md`
- Evaluation: `docs/evaluation-protocol.md`

## Required Reading

- Runtime work: runtime architecture, held association, and realtime inference.
- Model work: training, artifact policy, model registry, and evaluation.
- Dataset work: annotation/export and `docs/dataset-policy.md`.
- Overlay work: held association and `docs/alert-overlay-spec.md`.

## Done Criteria

The requested behavior exists in the current tree, pure logic has tests, CLI
and artifact checks pass, docs match the implementation, and every claimed
metric is backed by inspected output.
