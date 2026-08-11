# Local data

All contents below this directory are ignored except this file.

```text
data/
  raw/
  annotated/
  yolo/<dataset-version>/
  samples/
```

The integrated YOLO export must contain the six existing item labels followed
by `Opponent`. Use `scripts/validate_dataset.py` before training. Do not
commit gameplay footage, annotations, extracted frames, or exported datasets.
