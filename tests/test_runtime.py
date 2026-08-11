from pathlib import Path

import cv2
import numpy as np

from mk8dx_item_alert import runtime
from mk8dx_item_alert.config import ModelConfig, OutputConfig, RuntimeConfig
from mk8dx_item_alert.inference import Detection


class FakeCapture:
    def __init__(self, frame) -> None:
        self.frame = frame
        self.released = False
        self.read_count = 0

    def isOpened(self) -> bool:
        return True

    def read(self):
        self.read_count += 1
        return True, self.frame.copy()

    def release(self) -> None:
        self.released = True


class FakeYoloDetector:
    def __init__(self, path: Path, expected_labels=None) -> None:
        if "gate" in path.name:
            self.labels = ("Face",)
        else:
            self.labels = (
                "Boomerang",
                "FB",
                "Minacle-Eight",
                "Piranha-Plant",
                "Super-Horn",
                "green-shell3",
            )
        if expected_labels is not None:
            assert self.labels == expected_labels

    def detect(self, frame, *, track: bool = False):
        if self.labels == ("Face",):
            return (Detection("Face", 0.9, 0, 0, 10, 10),)
        return (Detection("Boomerang", 0.9, 10, 10, 20, 20),)


def test_runtime_releases_capture_without_camera_or_real_models(
    monkeypatch,
    tmp_path: Path,
) -> None:
    item_model = tmp_path / "item.pt"
    gate_model = tmp_path / "gate.pt"
    item_model.write_bytes(b"item")
    gate_model.write_bytes(b"gate")
    capture = FakeCapture(np.zeros((120, 160, 3), dtype=np.uint8))

    monkeypatch.setattr(runtime, "YoloDetector", FakeYoloDetector)
    monkeypatch.setattr(cv2, "VideoCapture", lambda source: capture)
    monkeypatch.setattr(
        cv2,
        "imread",
        lambda path: np.zeros((32, 32, 3), dtype=np.uint8),
    )
    monkeypatch.setattr(cv2, "imshow", lambda *args: None)
    monkeypatch.setattr(cv2, "waitKey", lambda delay: ord("q"))
    monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

    runtime.run_realtime(
        RuntimeConfig(
            models=ModelConfig(item_model, gate_model),
            output=OutputConfig(save_video=False),
        )
    )

    assert capture.released is True
    assert capture.read_count == 1
