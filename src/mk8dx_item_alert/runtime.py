"""Realtime OpenCV/YOLO resource lifecycle."""

from __future__ import annotations

import time
from collections import defaultdict

from .config import PROJECT_ROOT, RuntimeConfig
from .inference import YoloDetector
from .labels import (
    INTEGRATED_MODEL_LABELS,
    ITEM_MODEL_LABELS,
    get_icon_path_for_label,
    model_labels,
)
from .overlay import calculate_ranked_positions, draw_icon, draw_rank_badge
from .pipeline import FrameProcessor


def run_realtime(config: RuntimeConfig) -> None:
    import cv2
    import numpy as np

    _require_file(config.models.item_model_path, "item")
    item_detector = YoloDetector(config.models.item_model_path)
    if item_detector.labels not in (ITEM_MODEL_LABELS, INTEGRATED_MODEL_LABELS):
        raise ValueError(
            "item model labels do not match the supported legacy or integrated "
            f"contract: {item_detector.labels}"
        )

    gate_detector = None
    if config.gate_enabled:
        _require_file(config.models.gate_model_path, "gate")
        gate_detector = YoloDetector(
            config.models.gate_model_path,
            expected_labels=("Face",),
        )
    alert_icons = _load_alert_icons(cv2)

    capture = cv2.VideoCapture(config.source)
    if not capture.isOpened():
        raise OSError(f"capture source could not be opened: {config.source!r}")

    writer = None
    try:
        ok, frame = capture.read()
        if not ok:
            raise RuntimeError("first frame could not be read from capture source")

        frame_height, frame_width = frame.shape[:2]
        processor = FrameProcessor(
            item_detector=item_detector,
            gate_detector=gate_detector,
            config=config,
            frame_width=frame_width,
            frame_height=frame_height,
            cv2_module=cv2,
            numpy_module=np,
        )
        if not processor.integrated_mode:
            print(
                "warning: legacy item-only model active; alerts are not proof "
                "of opponent-held state"
            )

        if config.output.save_video:
            config.output.video_path.parent.mkdir(parents=True, exist_ok=True)
            writer = cv2.VideoWriter(
                str(config.output.video_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                config.output.fps,
                (frame_width, frame_height),
            )
            if not writer.isOpened():
                raise OSError(
                    f"video output could not be opened: {config.output.video_path}"
                )

        profiler: dict[str, list[float]] = defaultdict(list)
        while ok:
            frame_started = time.perf_counter()
            now = time.monotonic()
            annotated = frame.copy()
            result = processor.process(frame, now)
            if config.debug:
                _draw_debug_detections(annotated, result.detections)
            _draw_alerts(
                annotated,
                result.alerts,
                alert_icons,
                config.alerts.size,
                config.alerts.bottom_margin,
            )

            cv2.imshow(config.output.window_name, annotated)
            if writer is not None:
                write_started = time.perf_counter()
                writer.write(annotated)
                profiler["write"].append(_elapsed_ms(write_started))

            profiler["frame"].append(_elapsed_ms(frame_started))
            for stage, elapsed in result.timings_ms.items():
                profiler[stage].append(elapsed)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            ok, frame = capture.read()
        if config.profile:
            _print_profile(profiler)
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


def _load_alert_icons(cv2_module) -> dict[str, object]:
    icons: dict[str, object] = {}
    for label in model_labels():
        icon_path = get_icon_path_for_label(label)
        resolved_path = PROJECT_ROOT / icon_path if icon_path else None
        icon = cv2_module.imread(str(resolved_path)) if resolved_path else None
        if icon is None:
            raise RuntimeError(f"alert icon could not be loaded: {resolved_path}")
        icons[label] = icon
    return icons


def _draw_alerts(
    frame,
    alerts,
    icons: dict[str, object],
    alert_size: tuple[int, int],
    bottom_margin: int,
) -> None:
    positions = calculate_ranked_positions(
        len(alerts),
        (frame.shape[1], frame.shape[0]),
        alert_size,
        bottom_margin=bottom_margin,
    )
    for alert, position in zip(alerts, positions, strict=True):
        icon = icons.get(alert.label)
        if icon is None:
            continue
        draw_icon(frame, icon, position, alert_size)
        draw_rank_badge(frame, alert.rank, position)


def _require_file(path, role: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(
            f"{role} model is missing: {path}. "
            "Run 'mk8dx-alert models verify' or place an authorized model copy."
        )


def _draw_debug_detections(frame, detections) -> None:
    import cv2

    for detection in detections:
        start = (int(detection.x1), int(detection.y1))
        end = (int(detection.x2), int(detection.y2))
        cv2.rectangle(frame, start, end, (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{detection.label} {detection.confidence:.2f}",
            (start[0], max(15, start[1] - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )


def _elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000.0


def _print_profile(samples: dict[str, list[float]]) -> None:
    for stage in sorted(samples):
        values = sorted(samples[stage])
        if not values:
            continue
        p95_index = min(len(values) - 1, int(len(values) * 0.95))
        average = sum(values) / len(values)
        fps = 1000.0 / average if stage == "frame" and average else None
        fps_text = f" fps={fps:.2f}" if fps is not None else ""
        print(
            f"{stage}: avg={average:.2f}ms "
            f"p95={values[p95_index]:.2f}ms n={len(values)}{fps_text}"
        )
