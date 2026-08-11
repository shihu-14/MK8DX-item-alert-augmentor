# Evaluation Protocol

## Evidence Levels

Report these levels independently:

- Model level: YOLO precision, recall, mAP50, mAP50-95, and confusion matrix.
- Candidate level: legacy six-class item-candidate precision and recall.
- System level: integrated held-alert precision and recall after association,
  confirmation, and TTL.
- Error analysis: false predictions for thrown, dropped, background/course,
  and HUD states, plus unclassified false positives.
- Runtime: gate errors, event-scoped lead time, effective FPS, and stage latency.

Candidate metrics do not claim that an item is opponent-held. Candidate and
held-alert precision/recall have different meanings and must not be compared as
the same metric. Model mAP does not prove held association or realtime
performance.

## Ground-Truth JSONL

Each line represents one unique zero-based frame. Ground truth uses an
`objects` array and may include `gate_active`:

```json
{"frame":42,"gate_active":true,"objects":[{"opponent_id":"kart-a","event_id":"kart-a-fb-1","label":"FB","state":"held","opponent_bbox":[100,80,260,390],"item_bbox":[220,210,252,242],"item_use_frame":73}]}
```

`state` is `held`, `thrown`, `dropped`, `background`, or `hud`.

- Every object requires `item_bbox`. This lets the same held truth support
  legacy candidate evaluation and integrated held-alert evaluation.
- A `held` object also requires `opponent_bbox`.
- A non-held object does not require an opponent, so dropped,
  background/course, and HUD causes can be annotated without inventing one.
- `opponent_id` is recommended for annotation traceability but is never
  compared with a runtime tracker ID.
- `event_id` uniquely identifies one held/item-use event and is required when
  `item_use_frame` is present.

For example, a HUD negative needs only its item-like region:

```json
{"frame":42,"objects":[{"label":"FB","state":"hud","item_bbox":[1680,40,1760,120]}]}
```

## Prediction JSONL

Every prediction file contains exactly one mode. The runtime writes either
legacy candidates or integrated alerts for each processed frame.

Legacy mode records raw six-class detections as `candidates`:

```json
{"frame":42,"gate_active":true,"mode":"legacy","candidates":[{"label":"FB","confidence":0.84,"item_bbox":[222,212,251,241]}]}
```

A legacy candidate has no opponent identity, association result, confirmation,
or TTL semantics. It must never be described as a confirmed held alert.

Integrated mode records confirmed `alerts`:

```json
{"frame":42,"gate_active":true,"mode":"integrated","alerts":[{"runtime_track_id":17,"label":"FB","confidence":0.84,"opponent_bbox":[103,82,258,388],"item_bbox":[222,212,251,241],"item_observed":true}]}
```

`opponent_bbox` is the latest geometry for that opponent track. `item_bbox` is
the most recent associated item detection supporting the alert.
`item_observed` says whether that item association exists on the current frame.

Generate predictions directly from the runtime:

```bash
mk8dx-alert run --source gameplay.mp4 --no-save \
  --predictions-jsonl predictions/gameplay.jsonl
```

## Matching And Metrics

Matching is deterministic, same-label, and one-to-one within each frame. The
default IoU threshold is `0.5`.

Legacy candidate evaluation:

1. Match candidates to `held` truth by item-bbox IoU.
2. Match remaining candidates to non-held truth by item-bbox IoU.
3. Report `metric_scope=legacy_candidate` and `candidate_*` metrics.

Integrated held-alert evaluation:

1. Match alerts to `held` truth by opponent-bbox IoU.
2. Match remaining alerts to non-held truth by item-bbox IoU.
3. Report `metric_scope=integrated_held_alert` and `held_alert_*` metrics.

Positive matching has priority so a valid positive is not consumed by a nearby
negative annotation. Maximum-cardinality bipartite matching supports multiple
opponents holding the same item class. Runtime tracker IDs remain diagnostic
only.

A positive match is a true positive. A non-held match is a classified false
positive in that state. A prediction left after both stages is an
`unclassified_false_positive`. An unmatched held object is a false negative.

Metrics are frame-level. Legacy candidates are independent detections on each
processed frame. An integrated alert that persists under TTL contributes once
for every frame where runtime outputs it. During an opponent-only TTL frame,
the current opponent bbox is used for held matching, while the last supporting
item bbox remains available for negative matching and `item_observed=false`.
If neither bbox matches truth, the alert is an unclassified false positive.

Every truth frame containing `gate_active` requires a prediction frame with
`gate_active`. Metrics report gate false positives (`truth=false`,
`prediction=true`), gate false negatives (`truth=true`, `prediction=false`),
and missing gate predictions separately. `gate_errors` is their sum.

Lead time is calculated per `event_id` as
`item_use_frame - earliest matched prediction frame`. Only predictions matched
to that event are eligible. Legacy output is candidate lead time; integrated
output is held-alert lead time. Earlier unrelated predictions cannot increase
either value.

Evaluate with:

```bash
mk8dx-alert evaluate --ground-truth truth.jsonl \
  --predictions predictions/gameplay.jsonl --iou-threshold 0.5
```

## Promotion Gates

Use the same fixed clips and ground-truth JSONL where possible, but evaluate
each level against a like-for-like baseline:

- Promote a detector model using model-level metrics on the same dataset and
  label contract.
- Promote a legacy candidate model using candidate-level metrics against a
  legacy candidate baseline.
- Promote the integrated system using held-alert metrics against an integrated
  system baseline, together with non-held errors, gate errors, and runtime
  performance.

Do not require integrated held-alert recall to be within a fixed number of
points of legacy candidate recall; association and temporal confirmation make
those scopes semantically different. Record per-clip and per-state failures
even when aggregate metrics pass.

For the target Mac and fixed 1080p input, the initial target is at least 30
effective FPS and p95 `processed_frame` latency at or below 100 ms. This is not
capture-to-photon latency; use the definition in `docs/realtime-runtime.md`.
Do not report success until measured.
