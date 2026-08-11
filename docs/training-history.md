# Training History

This file preserves evidence previously embedded as comments in the root
`train.py`. Dataset contents and complete YOLO runs are not in the repository.

| Run/dataset | Purpose | Aggregate evidence |
| --- | --- | --- |
| Item_Detection.v4-original-v1 | Early item model | P 0.987, R 0.987, mAP50 0.993, mAP50-95 0.75 |
| Item_Detection.v7 / train21 | Six-class item model | P 0.863, R 0.751, mAP50 0.81, mAP50-95 0.488 |
| Item_Detection.v8 / train24 | Six-class item model | P 0.834, R 0.746, mAP50 0.793, mAP50-95 0.454 |
| Item_Detection.v9 / train29 | Promoted legacy item model | P 0.828, R 0.778, mAP50 0.795, mAP50-95 0.49 |
| Face-Detection.v4 / train27 | Gate model | P 0.987, R 0.994, mAP50 0.993, mAP50-95 0.763 |
| Face-Detection.v5 / train30 | Promoted gate model | P 0.987, R 0.994, mAP50 0.992, mAP50-95 0.765 |

The historical notes reported Ultralytics 8.3.116, Python 3.11.7, Torch 2.7.0
with CUDA 12.6, and an RTX 3090 for later runs. These timings and metrics have
not been reproduced in the current Mac environment.

Future runs use `scripts/train_yolo.py` and must record the exact command,
dataset version, package versions, class order, metrics, failures, and
checkpoint hash. The script writes `training-metadata.json` into the completed
ignored run directory with seed, deterministic mode, training options,
dataset-config hash, local base-model hash when available, and major package
versions. Evaluation evidence and promoted-checkpoint facts still require an
explicit registry update.
