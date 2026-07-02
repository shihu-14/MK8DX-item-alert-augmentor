# Alert Overlay Spec

## Trigger Mapping

Alert icons are mapped from model labels through explicit configuration. Current
prototype mappings:

| Model label | Alert icon |
| --- | --- |
| `Piranha-Plant` | `assets/icons/alerts/Piranha-Plant.png` |
| `Super-Horn` | `assets/icons/alerts/Super-Horn.png` |
| `FB` | `assets/icons/alerts/FB.png` |
| `Boomerang` | `assets/icons/alerts/Boomerang.png` |
| `Minacle-Eight` | `assets/icons/alerts/Minacle-Eight.png` |
| `green-shell3` | `assets/icons/alerts/Green-Shell3.png` |

## Display Position

The current prototype renders alert icons near the bottom of the output frame
and horizontally aligns them with the detected item center. Future overlays may
render on a screen edge, above an associated opponent, or in a priority list.

## Display Duration

The current prototype keeps alerts visible for a short fixed duration after a
detection. This should become configurable.

## Confidence Threshold

Item and gate confidence thresholds should be configurable. Current values live
in `detect.py` and should not be reported as evaluated thresholds unless tested.

## Temporal Smoothing

Optional smoothing may:

- Require a detection to appear for multiple frames.
- Keep an alert active for a TTL after the last detection.
- Suppress flicker from single-frame false positives.
- Decay confidence over time.

## Multiple Simultaneous Detections

Class-level alert state is not enough when multiple opponents hold the same
item. Future state should track alerts per detection or per associated opponent
track.

## Priority Rules

Possible priority signals:

- Higher confidence.
- Closer opponent or larger bbox.
- More dangerous item class.
- More recent detection.
- Opponent/item association strength.

Priority rules must be documented before they are treated as evaluated behavior.
