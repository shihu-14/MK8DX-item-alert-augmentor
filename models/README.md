# Runtime models

Model binaries are local-only and ignored by Git. The tracked
`manifest.toml` records the approved filenames, hashes, label contracts, and
publication status.

Place authorized copies here and verify them with:

```bash
mk8dx-alert models verify
```

`mk8dx-alert models install` downloads only entries that have an approved
`release_url`. The current entries intentionally have no URL while
redistribution rights are being reviewed.

Installation writes to a sibling `.part` file, validates manifest size and
SHA-256 there, and only then atomically replaces the final filename. An invalid
existing destination is preserved until a valid replacement is ready. Missing
release URLs, failed downloads, and validation failures leave existing bytes
unchanged and always remove the temporary file.
