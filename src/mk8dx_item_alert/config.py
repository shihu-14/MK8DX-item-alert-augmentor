"""Configuration for the MK8DX item-alert runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"


@dataclass(frozen=True)
class ModelConfig:
    item_model_path: Path = (
        DEFAULT_MODEL_DIR / "mk8dx-item-yolov8n-v9.pt"
    )
    gate_model_path: Path = (
        DEFAULT_MODEL_DIR / "mk8dx-gate-yolov8n-v5.pt"
    )


@dataclass(frozen=True)
class ThresholdConfig:
    item_confidence: float = 0.45
    gate_confidence: float = 0.45


@dataclass(frozen=True)
class AlertConfig:
    size: tuple[int, int] = (96, 96)
    duration_sec: float = 2.5
    bottom_margin: int = 10
    max_visible: int = 3
    confirmation_window: int = 5
    confirmation_required: int = 3
    proximity_ema_alpha: float = 0.4


@dataclass(frozen=True)
class GateRegionConfig:
    center_x_offset: int = 100
    center_y_offset: int = 200
    width: int = 430
    height: int = 360


@dataclass(frozen=True)
class ItemMaskConfig:
    upper_ratio: float = 0.23
    lower_ratio: float = 0.8


@dataclass(frozen=True)
class AssociationConfig:
    opponent_label: str = "Opponent"
    horizontal_padding_ratio: float = 0.75
    vertical_padding_ratio: float = 0.5


@dataclass(frozen=True)
class OutputConfig:
    save_video: bool = True
    video_path: Path = PROJECT_ROOT / "outputs" / "annotated.mp4"
    fps: float = 30.0
    window_name: str = "MK8DX Held-Item Alert"
    predictions_jsonl_path: Path | None = None


@dataclass(frozen=True)
class RuntimeConfig:
    models: ModelConfig = field(default_factory=ModelConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    gate_region: GateRegionConfig = field(default_factory=GateRegionConfig)
    item_mask: ItemMaskConfig = field(default_factory=ItemMaskConfig)
    association: AssociationConfig = field(default_factory=AssociationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    source: int | str = 0
    gate_enabled: bool = True
    debug: bool = False
    profile: bool = False
