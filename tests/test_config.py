from mk8dx_item_alert.config import RuntimeConfig


def test_runtime_config_defaults_match_current_prototype() -> None:
    config = RuntimeConfig()

    assert config.models.item_model_path == "runs/detect/train/weights/best_29.pt"
    assert config.models.gate_model_path == "runs/detect/train/weights/best_30.pt"
    assert config.thresholds.item_confidence == 0.45
    assert config.thresholds.gate_confidence == 0.45
    assert config.alerts.size == (150, 150)
    assert config.alerts.duration_sec == 2.5
    assert config.alerts.max_horizontal_velocity == 400.0
    assert config.output.video_path == "output_video_new21.mp4"
    assert config.output.save_video is True
    assert config.source == 0
    assert config.debug is False
    assert config.gate_region.center_x_offset == 100
    assert config.gate_region.center_y_offset == 200
    assert config.gate_region.width == 430
    assert config.gate_region.height == 360
    assert config.item_mask.upper_ratio == 0.23
    assert config.item_mask.lower_ratio == 0.8
