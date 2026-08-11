"""Realtime OpenCV/YOLO resource lifecycle."""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass

from .config import PROJECT_ROOT, RuntimeConfig
from .evaluation import write_prediction_frame
from .inference import YoloDetector
from .labels import (
    INTEGRATED_MODEL_LABELS,
    ITEM_MODEL_LABELS,
    get_icon_path_for_label,
    model_labels,
)
from .overlay import calculate_ranked_positions, draw_icon, draw_rank_badge
from .pipeline import FrameProcessor


@dataclass(frozen=True)
class StageProfile:
    average_ms: float
    p95_ms: float
    samples: int


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
    prediction_handle = None
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

        if config.output.predictions_jsonl_path is not None:
            prediction_path = config.output.predictions_jsonl_path
            prediction_path.parent.mkdir(parents=True, exist_ok=True)
            prediction_handle = prediction_path.open("w", encoding="utf-8")

        profiler: dict[str, list[float]] = defaultdict(list)
        frame_number = 0
        measuring = False
        measured_frames = 0
        measurement_started = 0.0
        measurement_ended = 0.0
        while True:
            frame_started = 0.0
            if measuring:
                frame_started = time.perf_counter()
                capture_started = time.perf_counter()
                ok, frame = capture.read()
                if not ok:
                    break
                profiler["capture"].append(_elapsed_ms(capture_started))

            now = time.monotonic()
            annotated = frame.copy()
            result = processor.process(frame, now)

            overlay_started = time.perf_counter()
            if config.debug:
                _draw_debug_detections(annotated, result.detections)
            _draw_alerts(
                annotated,
                result.alerts,
                alert_icons,
                config.alerts.size,
                config.alerts.bottom_margin,
            )
            if measuring:
                profiler["overlay"].append(_elapsed_ms(overlay_started))

            if prediction_handle is not None:
                prediction_started = time.perf_counter()
                write_prediction_frame(prediction_handle, frame_number, result)
                if measuring:
                    profiler["prediction_write"].append(
                        _elapsed_ms(prediction_started)
                    )

            display_started = time.perf_counter()
            cv2.imshow(config.output.window_name, annotated)
            quit_requested = cv2.waitKey(1) & 0xFF == ord("q")
            if measuring:
                profiler["display"].append(_elapsed_ms(display_started))

            if writer is not None:
                write_started = time.perf_counter()
                writer.write(annotated)
                if measuring:
                    profiler["video_write"].append(_elapsed_ms(write_started))

            if measuring:
                for stage, elapsed in result.timings_ms.items():
                    profiler[stage].append(elapsed)
                profiler["processed_frame"].append(_elapsed_ms(frame_started))
                measured_frames += 1
                measurement_ended = time.perf_counter()

            frame_number += 1
            if quit_requested:
                break
            if not measuring:
                measuring = True
                measurement_started = time.perf_counter()

        if config.profile:
            wall_seconds = (
                measurement_ended - measurement_started if measured_frames else 0.0
            )
            _print_profile(profiler, measured_frames, wall_seconds)
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        if prediction_handle is not None:
            prediction_handle.close()
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


def _summarize_samples(values: list[float]) -> StageProfile:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("profile samples must not be empty")
    p95_index = math.ceil(len(ordered) * 0.95) - 1
    return StageProfile(
        average_ms=sum(ordered) / len(ordered),
        p95_ms=ordered[p95_index],
        samples=len(ordered),
    )


def _print_profile(
    samples: dict[str, list[float]],
    processed_frames: int,
    wall_seconds: float,
) -> None:
    effective_fps = processed_frames / wall_seconds if wall_seconds > 0 else 0.0
    print(
        f"effective_fps={effective_fps:.2f} processed_frames={processed_frames} "
        f"wall_seconds={wall_seconds:.3f}"
    )
    for stage in sorted(samples):
        if not samples[stage]:
            continue
        summary = _summarize_samples(samples[stage])
        print(
            f"{stage}: avg={summary.average_ms:.2f}ms "
            f"p95={summary.p95_ms:.2f}ms n={summary.samples}"
        )
