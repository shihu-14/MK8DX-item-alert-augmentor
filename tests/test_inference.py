from types import SimpleNamespace

import pytest

from mk8dx_item_alert import inference


def test_tracking_refuses_implicit_lap_install(monkeypatch) -> None:
    detector = inference.YoloDetector.__new__(inference.YoloDetector)
    detector.labels = ("Boomerang", "Opponent")
    monkeypatch.setattr(inference, "find_spec", lambda name: None)

    with pytest.raises(RuntimeError, match="tracking extra"):
        detector.detect(object(), track=True)


def test_legacy_prediction_does_not_require_lap(monkeypatch) -> None:
    detector = inference.YoloDetector.__new__(inference.YoloDetector)
    detector.labels = ("Boomerang",)
    detector._model = SimpleNamespace(
        predict=lambda frame, verbose: [SimpleNamespace(names={}, boxes=())]
    )
    monkeypatch.setattr(inference, "find_spec", lambda name: None)

    assert detector.detect(object(), track=False) == ()
