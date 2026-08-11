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
{"frame":42,"gate_active":true,"objects":[{"opponent_id":"kart-a","event_id":"kart-a-fb-1","label":"FB","state":"held","opponent_bbox":[100,80,260,390],"item_bbox":[220,210,252,242],"item_use_frame":73}]}
```

`state` is `held`, `thrown`, `dropped`, `background`, or `hud`.

- A `held` object requires `opponent_bbox`; `item_bbox` is optional supporting
  annotation.
- A non-held object requires `item_bbox`. `opponent_bbox` is optional, so
  dropped, background/course, and HUD causes can be annotated without inventing
  an opponent.
- `opponent_id` is recommended for annotation traceability but is never
  compared with a runtime tracker ID.
- `event_id` uniquely identifies one held/item-use event and is required when
  `item_use_frame` is present.

For example, a HUD negative needs only its item-like region:

```json
{"frame":42,"objects":[{"label":"FB","state":"hud","item_bbox":[1680,40,1760,120]}]}
```

Runtime predictions use an `alerts` array:

```json
{"frame":42,"gate_active":true,"mode":"integrated","alerts":[{"runtime_track_id":17,"label":"FB","confidence":0.84,"opponent_bbox":[103,82,258,388],"item_bbox":[222,212,251,241],"item_observed":true}]}
```

`opponent_bbox` is the latest geometry for that opponent track. `item_bbox` is
the most recent associated item detection supporting the alert.
`item_observed` says whether that item association exists on the current frame.

Generate this file directly from the runtime:

```bash
mk8dx-alert run --source gameplay.mp4 --no-save \
  --predictions-jsonl predictions/gameplay.jsonl
```

Only integrated confirmed alerts have an opponent bbox and are written to
`alerts`. Legacy candidate alerts are intentionally omitted; the frame still
records its gate result and `mode`.

## Matching And Metrics

Matching is deterministic and one-to-one within each frame:

1. Match same-label predictions to `held` truth by opponent-bbox IoU.
2. Match only the remaining predictions to non-held truth by item-bbox IoU.
3. Use the configured IoU threshold for both stages (default `0.5`).

Held matching has priority so a valid opponent-held alert is not consumed by a
nearby negative item annotation. Maximum-cardinality bipartite matching in each
stage supports multiple opponents holding the same item class. Runtime tracker
IDs remain diagnostic only.

A held match is a true positive. A non-held item match is a classified false
positive in that state. A prediction left after both stages is reported as
`unclassified_false_positive`. An unmatched held object is a false negative.

Metrics are frame-level. A confirmed alert that persists under TTL contributes
once for every frame where runtime outputs it. During an opponent-only frame,
the current opponent bbox is used for held matching, while the last supporting
item bbox remains available for negative-cause matching and
`item_observed=false`. If neither bbox matches truth on that frame, the alert is
an unclassified false positive.

Every truth frame containing `gate_active` requires a prediction frame with
`gate_active`. Metrics report gate false positives (`truth=false`,
`prediction=true`), gate false negatives (`truth=true`, `prediction=false`),
and missing gate predictions separately. `gate_errors` is their sum.

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
