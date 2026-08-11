from mk8dx_item_alert.config import DEFAULT_MODEL_DIR, RuntimeConfig


def test_runtime_config_uses_semantic_local_model_paths() -> None:
    config = RuntimeConfig()

    assert config.models.item_model_path == (
        DEFAULT_MODEL_DIR / "mk8dx-item-yolov8n-v9.pt"
    )
    assert config.models.gate_model_path == (
        DEFAULT_MODEL_DIR / "mk8dx-gate-yolov8n-v5.pt"
    )
    assert config.thresholds.item_confidence == 0.45
    assert config.thresholds.gate_confidence == 0.45
    assert config.alerts.confirmation_window == 5
    assert config.alerts.confirmation_required == 3
    assert config.alerts.max_visible == 3
    assert config.gate_enabled is True
    assert config.source == 0
