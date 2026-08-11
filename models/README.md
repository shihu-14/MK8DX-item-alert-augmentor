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
