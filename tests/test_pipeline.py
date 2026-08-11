import cv2
import numpy as np

from mk8dx_item_alert.config import AlertConfig, RuntimeConfig
from mk8dx_item_alert.inference import Detection
from mk8dx_item_alert.pipeline import FrameProcessor


class FakeDetector:
    def __init__(self, labels: tuple[str, ...], detections=()) -> None:
        self.labels = labels
        self.detections = tuple(detections)
        self.track_flags: list[bool] = []

    def detect(self, frame, *, track: bool = False):
        self.track_flags.append(track)
        return self.detections


def test_integrated_pipeline_confirms_and_ranks_associated_item() -> None:
    detector = FakeDetector(
        ("Boomerang", "Opponent"),
        (
            Detection("Opponent", 0.9, 100, 100, 300, 400, track_id=7),
            Detection("Boomerang", 0.8, 240, 240, 270, 270),
        ),
    )
    config = RuntimeConfig(
        gate_enabled=False,
        alerts=AlertConfig(confirmation_required=3),
    )
    processor = FrameProcessor(
        item_detector=detector,
        gate_detector=None,
        config=config,
        frame_width=640,
        frame_height=480,
        cv2_module=cv2,
        numpy_module=np,
    )
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    assert processor.process(frame, 1.0).alerts == ()
    assert processor.process(frame, 2.0).alerts == ()
    result = processor.process(frame, 3.0)

    assert result.mode == "integrated"
    assert result.alerts[0].track_id == 7
    assert detector.track_flags == [True, True, True]
    assert set(result.timings_ms) == {
        "gate",
        "mask",
        "item_inference",
        "association_tracking_ranking",
    }


def test_pipeline_refreshes_ttl_geometry_from_opponent_only_detection() -> None:
    detector = FakeDetector(
        ("Boomerang", "Opponent"),
        (
            Detection("Opponent", 0.9, 100, 100, 300, 400, track_id=7),
            Detection("Boomerang", 0.8, 240, 240, 270, 270),
        ),
    )
    processor = FrameProcessor(
        item_detector=detector,
        gate_detector=None,
        config=RuntimeConfig(
            gate_enabled=False,
            alerts=AlertConfig(confirmation_required=1),
        ),
        frame_width=640,
        frame_height=480,
        cv2_module=cv2,
        numpy_module=np,
    )
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    processor.process(frame, 1.0)
    detector.detections = (
        Detection("Opponent", 0.9, 50, 50, 350, 450, track_id=7),
    )

    result = processor.process(frame, 2.0)

    assert result.alerts[0].opponent_bbox == (50, 50, 350, 450)
    assert result.alerts[0].item_bbox == (240, 240, 270, 270)
    assert result.alerts[0].item_observed is False
