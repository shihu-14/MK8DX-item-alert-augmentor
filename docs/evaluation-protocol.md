# Evaluation Protocol

## Separate Evidence

Report these independently:

- YOLO precision, recall, mAP50, mAP50-95, and confusion matrix.
- Held-alert precision and recall.
- False alerts for thrown, dropped, background/course, and HUD states.
- Gate false positives and false negatives.
- Alert lead frames/time before item use.
- Effective FPS and average/p95 stage and frame latency.

Model mAP does not prove held association or realtime performance.

## JSONL Contract

Ground-truth records contain `frame`, `track_id`, `label`, and `state`.
`state` is one of `held`, `thrown`, `dropped`, `background`, or
`hud`. Optional `gate_active` records gate truth and `item_use_frame`
enables average alert lead-frame reporting.

Prediction records contain `frame`, `track_id`, and `label`, with optional
`gate_active`. Evaluate with:

```bash
mk8dx-alert evaluate --ground-truth truth.jsonl --predictions predictions.jsonl
```

## Promotion Gates

Compare legacy and integrated modes on the same fixed clips. Promote only when
held recall falls by no more than two percentage points and non-held false
alerts improve. Record failures even when aggregate metrics pass.

For the target Mac and fixed 1080p input, profile with video saving disabled.
The initial runtime target is at least 30 effective FPS and p95 frame latency at
or below 100 ms. Do not report success until measured.
