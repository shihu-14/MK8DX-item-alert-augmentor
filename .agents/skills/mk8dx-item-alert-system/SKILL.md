---
name: mk8dx-item-alert-system
description: Use for MK8DX held-item detection, YOLO training/inference, OpenCV capture, gate detection, opponent association, alert ranking, model distribution, evaluation, and runtime refactoring.
---

# MK8DX Item Alert System

## Working Rules

- Read the project specifications relevant to the task before changing code.
- Do not add compatibility entrypoints or experimental snapshots; use Git
  history for obsolete code.
- Never infer metrics or artifact rights that are not recorded.
- Follow the linked project specifications instead of restating their
  contracts in Skill references.

## Task Workflow

- Runtime changes: read architecture, held association, realtime runtime, and
  realtime inference guidance.
- Evaluation changes: read the evaluation protocol and held association spec.
- Model changes: read training guidance, artifact policy, model registry, and
  evaluation protocol.
- Dataset changes: read dataset policy and training guidance.
- Overlay changes: read held association and alert overlay specifications.

Add focused pure-logic tests first for identity, temporal, artifact, and metric
contracts. Run the repository verification commands before reporting results.

## Project Specifications

- System behavior: `docs/system-spec.md`
- Architecture: `docs/architecture.md`
- Held association: `docs/held-item-association.md`
- Runtime and profiling: `docs/realtime-runtime.md`
- Evaluation: `docs/evaluation-protocol.md`
- Overlay: `docs/alert-overlay-spec.md`
- Dataset policy: `docs/dataset-policy.md`
- Artifact policy: `docs/artifact-policy.md`
- Artifact provenance: `docs/artifact-provenance.md`
- Model registry: `docs/model-registry.md`

## Workflow References

- Realtime implementation: `references/realtime-inference.md`
- Training: `references/yolo-training.md`

## Done Criteria

The requested behavior exists in the current tree, tests cover the changed
contracts, fresh-clone checks pass without local artifacts, applicable local
artifact checks pass separately, and docs match inspected implementation.
