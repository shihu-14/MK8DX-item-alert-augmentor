"""Runtime configuration defaults for the MK8DX item alert prototype."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelConfig:
    item_model_path: str = "runs/detect/train/weights/best_29.pt"
    gate_model_path: str = "runs/detect/train/weights/best_30.pt"


@dataclass(frozen=True)
class ThresholdConfig:
    item_confidence: float = 0.45
    gate_confidence: float = 0.45
    smoothing: float | None = None


@dataclass(frozen=True)
class AlertConfig:
    size: tuple[int, int] = (150, 150)
    duration_sec: float = 2.5
    max_horizontal_velocity: float = 400.0
    bottom_margin: int = 10


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
class OutputConfig:
    save_video: bool = True
    video_path: str = "output_video_new21.mp4"
    fps: float = 30.0
    window_name: str = "YOLOv8 Detection (Face-Gated, Velocity Overlay)"


@dataclass(frozen=True)
class RuntimeConfig:
    models: ModelConfig = field(default_factory=ModelConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    gate_region: GateRegionConfig = field(default_factory=GateRegionConfig)
    item_mask: ItemMaskConfig = field(default_factory=ItemMaskConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    source: int | str = 0
    debug: bool = False
