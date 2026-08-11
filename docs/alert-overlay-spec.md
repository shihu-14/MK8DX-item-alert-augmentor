# Alert Overlay

Raw item labels map explicitly to the six PNG files under
`assets/icons/alerts/`. Unknown labels never render an icon.

Confirmed integrated alerts are sorted by estimated proximity and displayed in
a centered bottom row. Each icon has a visible rank badge:

- 1 is the estimated nearest opponent.
- At most three alerts are shown.
- Equal-size icons and fixed gaps prevent dynamic layout shifts.
- Position and copy bounds are clipped to the frame.

The rank is not race position or absolute distance. Legacy item-only mode uses
the same layout but remains candidate display behavior, not confirmed
opponent-held evidence.

Track state is keyed by opponent ID. Two opponents holding the same item
produce independent alerts. Confirmed state persists for the configured TTL.
