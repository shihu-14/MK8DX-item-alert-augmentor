# Evaluation Protocol

## Separate Evidence

Report these independently:

- YOLO precision, recall, mAP50, mAP50-95, and confusion matrix.
- Frame-level held-alert precision and recall.
- False alerts for thrown, dropped, background/course, and HUD states.
- Gate false positives, false negatives, and missing predictions.
- Alert lead frames/time per held/item-use event.
- Effective FPS and average/p95 runtime stage latency.

Model mAP does not prove held association or realtime performance.

## Frame JSONL Contract

Each JSONL line is one unique zero-based frame. Ground truth uses an `objects`
array and may include `gate_active`:

```json
{"frame":42,"gate_active":true,"objects":[{"opponent_id":"kart-a","event_id":"kart-a-fb-1","label":"FB","state":"held","opponent_bbox":[100,80,260,390],"item_use_frame":73}]}
```

`state` is `held`, `thrown`, `dropped`, `background`, or `hud`.
`opponent_bbox` identifies the opponent involved in the annotation. An
`opponent_id` is recommended for annotation traceability but is never compared
with a runtime tracker ID. `event_id` must uniquely identify one held/item-use
event; it is required whenever `item_use_frame` is present.

Runtime predictions use an `alerts` array:

```json
{"frame":42,"gate_active":true,"mode":"integrated","alerts":[{"runtime_track_id":17,"label":"FB","confidence":0.84,"opponent_bbox":[103,82,258,388]}]}
```

Generate this file directly from the runtime:

```bash
mk8dx-alert run --source gameplay.mp4 --no-save \
  --predictions-jsonl predictions/gameplay.jsonl
```

Only integrated confirmed alerts have an opponent bbox and are written to
`alerts`. Legacy candidate alerts are intentionally omitted; the frame still
records its gate result and `mode`.

## Matching And Metrics

For each frame, predictions and truth objects must have the same item label and
an opponent-bbox IoU at or above the configured threshold (default `0.5`). A
deterministic maximum-cardinality bipartite match enforces one prediction per
truth object and one truth object per prediction. Runtime tracker IDs are
diagnostic only. This supports multiple opponents holding the same item class.

A prediction matched to `held` is a true positive. A prediction matched to a
non-held state is a false positive in that state. An unmatched prediction is
an unclassified false positive, and an unmatched held object is a false
negative. Counts are frame-level, so a persistent alert contributes once per
annotated frame.

Every truth frame containing `gate_active` requires a prediction frame with
`gate_active`. A missing value, missing frame, or unequal value is one gate
error.

Lead time is calculated separately for each `event_id` as
`item_use_frame - earliest matched prediction frame`. Only predictions matched
to truth records for that event are eligible. Earlier unrelated predictions,
including another event with the same label, cannot increase lead time.

Evaluate with:

```bash
mk8dx-alert evaluate --ground-truth truth.jsonl \
  --predictions predictions/gameplay.jsonl --iou-threshold 0.5
```

## Promotion Gates

Compare legacy and integrated modes on the same fixed clips. Promote only when
held recall falls by no more than two percentage points and non-held false
alerts improve. Record failures even when aggregate metrics pass.

For the target Mac and fixed 1080p input, the initial target is at least 30
effective FPS and p95 `processed_frame` latency at or below 100 ms. The runtime
metric is not capture-to-photon latency; use the definition in
`docs/realtime-runtime.md`. Do not report success until measured.
