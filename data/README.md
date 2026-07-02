# Local Data Directory

This directory documents local data layout. Dataset contents are local-only by
default and should not be committed unless a task explicitly asks for a small
sample or metadata file.

Suggested layout:

```text
data/
  raw/
  annotated/
  yolo/
  samples/
```

## Directories

- `data/raw/`: raw local gameplay videos, camera captures, or extracted frames.
- `data/annotated/`: annotation project exports or intermediate labeled data.
- `data/yolo/`: exported YOLO-format datasets with `data.yaml`, images, and
  labels.
- `data/samples/`: small illustrative samples that may be committed only when
  explicitly useful and safe to share.

## Commit Policy

Can be committed:

- `data/README.md`.
- Small metadata files when explicitly requested.
- Small sample images only when intentionally selected.

Should not be committed by default:

- Raw videos.
- Full frame dumps.
- Full annotation exports.
- YOLO datasets.
- Generated predictions.
- Debug frame dumps.
- New checkpoints.
