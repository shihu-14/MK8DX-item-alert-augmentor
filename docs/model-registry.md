# Model Registry

## Promoted Local Models

| Semantic artifact | Role | Dataset | Labels | Evidence | SHA-256 | Publication |
| --- | --- | --- | --- | --- | --- | --- |
| `mk8dx-item-yolov8n-v9.pt` | Legacy item candidate detection | `Item_Detection.v9-original-v2.yolov8` | Six item labels | P 0.828, R 0.778, mAP50 0.795, mAP50-95 0.49; copied from preserved training output | `b803f3a5dafeba16b2f64fed8009909084fea5d35d0ed7b0f2a7d5c3e857ff9a` | Local only, rights review pending |
| `mk8dx-gate-yolov8n-v5.pt` | Face/rear-view gate proxy | `Face-Detection.v5-original-v1.yolov8` | Face | P 0.987, R 0.994, mAP50 0.992, mAP50-95 0.765; copied from preserved training output | `f5861a230af9d5396ca9111e9efdf58b248c9bf96ab632ae80034102608f09c3` | Local only, rights review pending |

These metrics are model-level validation results, not held-item, gate-state,
FPS, or latency evidence. Current confusion matrices are under
`docs/model-evidence/`.

## Planned Integrated Model

The seven-class model has no promoted checkpoint yet. Its labels are the six
legacy item labels followed by `Opponent`. Do not add it to the manifest until
dataset validation, model evaluation, held-alert comparison, hash recording,
and redistribution review are complete.

Historical `best*.pt`, upstream base weights, and experimental face weights
remain available through Git history but are not current artifacts.
