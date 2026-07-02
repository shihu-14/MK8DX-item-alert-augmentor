"""Realtime OpenCV/YOLO runtime for the MK8DX item alert prototype."""

from __future__ import annotations

import time

from .config import RuntimeConfig
from .labels import get_icon_path_for_label, model_labels
from .overlay import draw_icon
from .regions import compute_gate_region, compute_item_mask_bounds
from .smoothing import AlertStateTracker


def _load_alert_icons(cv2_module) -> dict[str, object | None]:
    icons: dict[str, object | None] = {}
    for label in model_labels():
        icon_path = get_icon_path_for_label(label)
        icons[label] = cv2_module.imread(icon_path) if icon_path else None
    return icons


def run_realtime(config: RuntimeConfig) -> None:
    import cv2
    import numpy as np
    from ultralytics import YOLO

    item_model = YOLO(config.models.item_model_path)
    gate_model = YOLO(config.models.gate_model_path)
    alert_icons = _load_alert_icons(cv2)
    alert_tracker = AlertStateTracker(model_labels())

    cap = cv2.VideoCapture(config.source)
    if not cap.isOpened():
        raise IOError("キャプチャデバイスが開けません")

    out = None
    try:
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("カメラからフレームが取得できません")

        frame_height, frame_width = frame.shape[:2]
        gate_region = compute_gate_region(
            frame_width,
            frame_height,
            config.gate_region,
        )
        upper_y, lower_y = compute_item_mask_bounds(frame_height, config.item_mask)

        if config.output.save_video:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(
                config.output.video_path,
                fourcc,
                config.output.fps,
                (frame_width, frame_height),
            )

        while True:
            ok, frame = cap.read()
            if not ok:
                print("フレーム取得失敗")
                break

            now = time.time()
            annotated = frame.copy()

            face_crop = frame[
                gate_region.y1 : gate_region.y2,
                gate_region.x1 : gate_region.x2,
            ]
            face_boxes = gate_model(face_crop)[0].boxes
            face_in = any(
                float(box.conf) >= config.thresholds.gate_confidence
                for box in face_boxes
            )

            if face_in:
                if config.debug:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                mask = np.ones((frame_height, frame_width), np.uint8) * 255
                mask[:upper_y, :] = 0
                mask[lower_y:, :] = 0
                mask[
                    gate_region.y1 : gate_region.y2,
                    gate_region.x1 : gate_region.x2,
                ] = 0
                roi = cv2.bitwise_and(frame, frame, mask=mask)

                results = item_model(roi)[0]
                for box in results.boxes:
                    if float(box.conf) < config.thresholds.item_confidence:
                        continue

                    x1, _, x2, _ = box.xyxy[0].cpu().numpy()
                    class_name = results.names[int(box.cls)]

                    if (
                        class_name not in alert_icons
                        or alert_icons[class_name] is None
                    ):
                        continue

                    center_x = (x1 + x2) / 2
                    alert_tracker.update_detection(
                        class_name,
                        center_x,
                        now,
                        frame_width,
                        frame_height,
                        config.alerts,
                    )

            for visible_alert in alert_tracker.visible_alerts(
                now,
                frame_width,
                config.alerts,
            ):
                icon = alert_icons.get(visible_alert.label)
                if icon is not None:
                    draw_icon(
                        annotated,
                        icon,
                        visible_alert.position,
                        config.alerts.size,
                    )

            cv2.imshow(config.output.window_name, annotated)

            if out is not None:
                out.write(annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        if out is not None:
            out.release()
        cv2.destroyAllWindows()
