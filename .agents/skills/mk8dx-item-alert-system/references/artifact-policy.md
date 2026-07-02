# Artifact Policy

## Default Rule

Do not newly commit raw videos, datasets, YOLO runs, generated videos, debug
dumps, predictions, or model checkpoints by default. These artifacts are often
large, machine-specific, or derived from local experiments.

## Expected Local Paths

Use local-only paths such as:

- `data/raw/`
- `data/annotated/`
- `data/yolo/`
- `data/samples/`
- `datasets/`
- `runs/`
- `outputs/`
- `debug_frames/`

`data/README.md` may be committed to document local layout.

## Existing Artifacts

The current repository may already track some checkpoints and run images. Do not
remove or replace existing tracked artifacts without an explicit task. Document
them in the model registry and artifact policy instead.

## Sharing Results

Prefer lightweight summaries, metrics tables, and selected small illustrative
images. Use external storage or a release process for large checkpoints or video
artifacts when needed.
