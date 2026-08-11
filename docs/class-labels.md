# Class Labels

The promoted legacy item model embeds this exact numeric order:

| ID | Raw label | Canonical name | Display name |
| --- | --- | --- | --- |
| 0 | `Boomerang` | boomerang | Boomerang |
| 1 | `FB` | fb | FB |
| 2 | `Minacle-Eight` | miracle_eight | Miracle Eight |
| 3 | `Piranha-Plant` | piranha_plant | Piranha Plant |
| 4 | `Super-Horn` | super_horn | Super Horn |
| 5 | `green-shell3` | triple_green_shell | Triple Green Shell |

The integrated model must append:

| ID | Raw label | Canonical name |
| --- | --- | --- |
| 6 | `Opponent` | opponent |

Do not silently correct `Minacle-Eight`, expand `FB`, or otherwise rename
raw labels. Display and canonical aliases belong in mapping code.
