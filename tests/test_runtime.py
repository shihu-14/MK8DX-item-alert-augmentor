import json
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


class FakeWriter:
    def __init__(self) -> None:
        self.write_count = 0
        self.released = False

    def isOpened(self) -> bool:
        return True

    def write(self, frame) -> None:
        self.write_count += 1

    def release(self) -> None:
        self.released = True


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


def test_runtime_writes_frame_level_prediction_jsonl(
    monkeypatch,
    tmp_path: Path,
) -> None:
    item_model = tmp_path / "item.pt"
    gate_model = tmp_path / "gate.pt"
    predictions = tmp_path / "predictions" / "run.jsonl"
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
            output=OutputConfig(
                save_video=False,
                predictions_jsonl_path=predictions,
            ),
        )
    )

    record = json.loads(predictions.read_text(encoding="utf-8"))
    assert record["frame"] == 0
    assert record["gate_active"] is True
    assert record["mode"] == "legacy"
    assert record["alerts"] == []


def test_profile_output_uses_wall_clock_effective_fps(capsys) -> None:
    runtime._print_profile(
        {"processed_frame": [10.0, 20.0], "capture": [1.0, 2.0]},
        processed_frames=2,
        wall_seconds=0.1,
    )

    output = capsys.readouterr().out
    assert "effective_fps=20.00 processed_frames=2 wall_seconds=0.100" in output
    assert "processed_frame: avg=15.00ms p95=20.00ms n=2" in output


def test_runtime_profiles_each_documented_active_stage(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    item_model = tmp_path / "item.pt"
    gate_model = tmp_path / "gate.pt"
    item_model.write_bytes(b"item")
    gate_model.write_bytes(b"gate")
    capture = FakeCapture(np.zeros((120, 160, 3), dtype=np.uint8))
    writer = FakeWriter()
    keys = iter((0, ord("q")))

    monkeypatch.setattr(runtime, "YoloDetector", FakeYoloDetector)
    monkeypatch.setattr(cv2, "VideoCapture", lambda source: capture)
    monkeypatch.setattr(cv2, "VideoWriter", lambda *args: writer)
    monkeypatch.setattr(cv2, "VideoWriter_fourcc", lambda *args: 0)
    monkeypatch.setattr(
        cv2,
        "imread",
        lambda path: np.zeros((32, 32, 3), dtype=np.uint8),
    )
    monkeypatch.setattr(cv2, "imshow", lambda *args: None)
    monkeypatch.setattr(cv2, "waitKey", lambda delay: next(keys))
    monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

    runtime.run_realtime(
        RuntimeConfig(
            models=ModelConfig(item_model, gate_model),
            output=OutputConfig(
                video_path=tmp_path / "output.mp4",
                predictions_jsonl_path=tmp_path / "predictions.jsonl",
            ),
            profile=True,
        )
    )

    output = capsys.readouterr().out
    for stage in (
        "capture",
        "gate",
        "mask",
        "item_inference",
        "association_tracking_ranking",
        "overlay",
        "prediction_write",
        "display",
        "video_write",
        "processed_frame",
    ):
        assert f"{stage}:" in output
    assert "processed_frames=1" in output
    assert writer.write_count == 2
    assert writer.released is True
