import pytest

from mk8dx_item_alert import inference


def test_tracking_refuses_implicit_lap_install(monkeypatch) -> None:
    detector = inference.YoloDetector.__new__(inference.YoloDetector)
    detector.labels = ("Boomerang", "Opponent")
    monkeypatch.setattr(inference, "find_spec", lambda name: None)

    with pytest.raises(RuntimeError, match="install it explicitly"):
        detector.detect(object(), track=True)
