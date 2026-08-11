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

Use the item center and an opponent box expanded by configurable horizontal and
vertical ratios. Ignore opponents without a tracker ID. Resolve all candidate
edges with deterministic maximum-cardinality bipartite matching so each item
and opponent is used at most once. Prefer constrained/high-confidence items,
then normalized center distance and stable geometry/track-ID tie breakers. This
prevents overlapping expanded boxes from consuming an item that could have
been assigned to another opponent.

## Temporal Confirmation

Track state by opponent ID, not item class. Confirm an item after association in
at least three of the last five inference frames. Reset the confirmation window
when the associated item label changes. Keep confirmed alerts for the configured
TTL.

## Estimated Distance

This is neither absolute depth nor race position. Rank by the EMA-smoothed
opponent bounding-box height, descending. Use bounding-box bottom position as a
tie-breaker and stable track ID as the final deterministic key. Do not use item
box area because physical item sizes differ.

Display at most three confirmed opponents and label them 1 through 3 from
estimated nearest to farthest.
