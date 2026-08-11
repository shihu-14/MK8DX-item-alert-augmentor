# Artifact Policy

## Git

Track source, tests, docs, model metadata, hashes, and selected lightweight
evidence. Do not track:

- Dataset contents or exported YOLO data.
- Raw or generated gameplay videos.
- YOLO runs, predictions, debug frames, or benchmark output.
- Virtual environments and caches.
- PT, ONNX, or engine model binaries.

## Runtime Models

Store local binaries under ignored `models/`. The tracked manifest defines
semantic filenames, role, version, label order, dataset, size, SHA-256, release
name, and publication URL.

Approved models are versioned GitHub Release assets. Runtime never downloads
implicitly; users call `mk8dx-alert models install`. Verify size and SHA-256
before loading. Explicit installation must download to a sibling temporary
file, verify that temporary file, and atomically replace the final path only
after validation succeeds. Never delete or modify an invalid existing model
until its replacement has passed size and checksum validation.

Keep `release_url` empty and publication status pending until model and data
provenance, upstream terms, and redistribution authorization are recorded.

Existing historical binary blobs remain in Git history. Do not rewrite history
without a separate explicit authorization.
