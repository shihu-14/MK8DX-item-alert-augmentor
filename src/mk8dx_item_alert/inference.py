"""Typed detector boundary for Ultralytics YOLO."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    track_id: int | None = None

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def bottom(self) -> float:
        return self.y2


class Detector(Protocol):
    labels: tuple[str, ...]

    def detect(self, frame, *, track: bool = False) -> tuple[Detection, ...]: ...


class YoloDetector:
    """Load a YOLO model once and normalize its detection output."""

    def __init__(
        self,
        model_path: Path,
        expected_labels: tuple[str, ...] | None = None,
    ) -> None:
        from ultralytics import YOLO

        self.model_path = model_path
        self._model = YOLO(str(model_path))
        names = self._model.names
        self.labels = tuple(names[index] for index in sorted(names))
        if expected_labels is not None and self.labels != expected_labels:
            raise ValueError(
                f"unexpected labels for {model_path}: "
                f"expected {expected_labels}, got {self.labels}"
            )

    def detect(self, frame, *, track: bool = False) -> tuple[Detection, ...]:
        if track:
            if find_spec("lap") is None:
                raise RuntimeError(
                    "integrated ByteTrack mode requires the tracking extra; "
                    "install it with 'python -m pip install -e \".[tracking]\"'"
                )
            result = self._model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False,
            )[0]
        else:
            result = self._model.predict(frame, verbose=False)[0]
        return tuple(_parse_box(box, result.names) for box in result.boxes)


def _parse_box(box, names: dict[int, str]) -> Detection:
    coordinates = box.xyxy[0].cpu().tolist()
    box_id = getattr(box, "id", None)
    track_id = int(box_id.item()) if box_id is not None else None
    return Detection(
        label=names[int(box.cls.item())],
        confidence=float(box.conf.item()),
        x1=float(coordinates[0]),
        y1=float(coordinates[1]),
        x2=float(coordinates[2]),
        y2=float(coordinates[3]),
        track_id=track_id,
    )
