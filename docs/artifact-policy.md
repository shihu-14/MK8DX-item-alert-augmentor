# Artifact Policy

## Git Tracking

Track source, tests, documentation, model metadata, hashes, and selected
lightweight evaluation evidence. Do not track:

- Dataset contents or exported YOLO data.
- Raw or generated gameplay videos.
- YOLO runs, prediction JSONL, debug frames, or benchmark output.
- Virtual environments, caches, and local configuration.
- PT, ONNX, or engine model binaries.

Historical binary blobs remain in Git history. Do not rewrite history without
separate explicit authorization.

## Runtime Models

Store local model binaries under ignored `models/`. The tracked
`models/manifest.toml` defines each model's semantic filename, role, version,
label order, dataset version, size, SHA-256, Release name, publication status,
and URL.

Approved models are versioned GitHub Release assets, not normal Git or Git LFS
objects. Runtime never downloads implicitly; installation is an explicit
`mk8dx-alert models install` operation.

Installation downloads to a sibling temporary file, validates its size and
SHA-256, and atomically replaces the destination only after validation passes.
An existing invalid destination must remain unchanged if the URL is missing or
download/validation fails.

Keep `release_url` empty and publication status pending until model and dataset
provenance, upstream terms, and redistribution authorization are recorded in
`docs/artifact-provenance.md`. Apply the same provenance requirement to alert
icons and other third-party artifacts.
