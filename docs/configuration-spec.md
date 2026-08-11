# Configuration

Runtime defaults are immutable dataclasses in `mk8dx_item_alert.config`.
There is no YAML/TOML runtime configuration layer.

Configuration groups:

- Models: semantic local item and gate paths under `models/`.
- Thresholds: item and gate confidence.
- Gate region: frame-center offsets and fixed dimensions.
- Item mask: upper and lower frame ratios.
- Association: opponent label and expanded-box ratios.
- Alerts: icon size, TTL, maximum count, three-of-five confirmation, and
  proximity EMA.
- Output: save flag, ignored output path, FPS, and window name.
- Runtime: source, gate enabled, debug, and profile flags.

The CLI overrides source, model paths, gate, save, debug, and profiling without
mutating defaults. Model distribution metadata is separate in
`models/manifest.toml`.
