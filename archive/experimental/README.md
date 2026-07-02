# Experimental Snapshots

These files are historical experimental snapshots from earlier realtime
prototype work. They are kept for reference and are not the main entrypoints.

Current entrypoints:

- `detect.py`: compatibility entrypoint for the refactored realtime prototype.
- `scripts/run_realtime.py`: current refactored realtime script.

Snapshot notes:

- `main.py`: early OpenCV/YOLO prototype using a Haar cascade gate and a single
  alert image.
- `tmp1.py`: YOLO face-gated item detection snapshot with class-specific alert
  images and debug drawing.
- `tmp2.py`: later YOLO face-gated snapshot with class-level display timing.

These scripts may still contain older experimental thresholds or model choices.
Do not treat them as stable runtime entrypoints.
