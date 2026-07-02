# Class Labels

Model labels must not be silently renamed. If display names or canonical names
change, keep an explicit alias mapping.

| Canonical item | Current model label | Display name | Alert image | Notes |
| --- | --- | --- | --- | --- |
| piranha_plant | `Piranha-Plant` | Piranha Plant | `assets/icons/alerts/Piranha-Plant.png` | Can be confused with course decoration. |
| super_horn | `Super-Horn` | Super Horn | `assets/icons/alerts/Super-Horn.png` | Current label uses hyphen. |
| fireball_or_fire_flower | `FB` | FB | `assets/icons/alerts/FB.png` | Meaning should be clarified before renaming. |
| boomerang | `Boomerang` | Boomerang | `assets/icons/alerts/Boomerang.png` | May appear as held or thrown depending state. |
| miracle_eight | `Minacle-Eight` | Miracle Eight | `assets/icons/alerts/Minacle-Eight.png` | Current model spelling is `Minacle-Eight`; do not silently rename. |
| triple_green_shell | `green-shell3` | Triple Green Shell | `assets/icons/alerts/Green-Shell3.png` | Current label is lowercase with suffix `3`. |

## Alias Policy

- Preserve model labels exactly for inference compatibility.
- Add aliases only in mapping/config layers.
- Document spelling issues, such as `Minacle-Eight` vs `Miracle Eight`, without
  changing model labels in code.
- Keep alert icon filenames explicit.
