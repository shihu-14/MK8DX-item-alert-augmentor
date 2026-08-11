# Held-Item Association

## Label Contract

The integrated detector uses this exact order:

1. Boomerang
2. FB
3. Minacle-Eight
4. Piranha-Plant
5. Super-Horn
6. green-shell3
7. Opponent

Only opponent-held items are positive item annotations. Thrown, dropped,
background, course-decoration, and HUD examples are negatives.

## Spatial Association

An item is a candidate for an opponent when its center is inside the configured
expanded opponent box. Opponents without a tracker ID are ignored.

All candidate edges are resolved with deterministic maximum-cardinality
bipartite matching. Each item and opponent is used at most once. Ordering
prefers constrained/high-confidence items, then normalized center distance and
stable geometry/track-ID tie breakers. This prevents overlapping expanded
boxes from consuming an item that another opponent could have used.

## Temporal State And TTL

State is keyed by runtime opponent track ID, not item class. Association in at
least three of the last five inference frames confirms an alert. A label change
resets that confirmation window. A confirmed alert remains visible until its
TTL expires; only a new item association extends the expiry time.

On every gate-active integrated frame:

- A current association updates opponent geometry, item bbox, confidence,
  confirmation history, and TTL.
- If association is absent but the same opponent track ID is detected, the
  latest opponent bbox, center, bottom, and height EMA update. The last item bbox
  remains as the alert's supporting evidence and `item_observed` becomes false.
- An opponent-only observation does not extend TTL or count as item evidence.

When the gate is inactive, or the opponent track itself is not observed, no
current geometry is available. The previous opponent and item bboxes remain
until TTL expiry, `item_observed` is false, and the confirmation history records
the missing association.

## Estimated Distance

Distance rank is neither absolute depth nor race position. Confirmed alerts are
ordered by EMA-smoothed opponent bbox height, then bbox bottom, then stable
track ID. Item box area is not used because physical item sizes differ. At most
three alerts are displayed from estimated nearest to farthest.

Evaluation semantics for current/stale item evidence and persistent TTL frames
are defined in `docs/evaluation-protocol.md`.
