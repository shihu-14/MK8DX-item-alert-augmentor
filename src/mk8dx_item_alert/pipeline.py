"""Frame-level gate, detection, association, and ranking pipeline."""

from __future__ import annotations

import time
from dataclasses import dataclass

from .association import AssociatedItem, associate_items
from .config import RuntimeConfig
from .inference import Detection, Detector
from .labels import OPPONENT_LABEL
from .ranking import RankedAlert, rank_nearest
from .regions import Rect, compute_gate_region, compute_item_mask_bounds
from .tracking import AlertTracker


@dataclass(frozen=True)
class FrameResult:
    gate_active: bool
    mode: str
    detections: tuple[Detection, ...]
    associations: tuple[AssociatedItem, ...]
    alerts: tuple[RankedAlert, ...]
    timings_ms: dict[str, float]


class FrameProcessor:
    def __init__(
        self,
        *,
        item_detector: Detector,
        gate_detector: Detector | None,
        config: RuntimeConfig,
        frame_width: int,
        frame_height: int,
        cv2_module,
        numpy_module,
    ) -> None:
        self.item_detector = item_detector
        self.gate_detector = gate_detector
        self.config = config
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cv2 = cv2_module
        self.np = numpy_module
        self.gate_region = compute_gate_region(
            frame_width,
            frame_height,
            config.gate_region,
        )
        self.mask = self._build_mask()
        self.tracker = AlertTracker()
        self.integrated_mode = OPPONENT_LABEL in item_detector.labels

    def process(self, frame, now: float) -> FrameResult:
        timings: dict[str, float] = {}
        started = time.perf_counter()
        gate_active = self._gate_active(frame)
        timings["gate"] = _elapsed_ms(started)
        detections: tuple[Detection, ...] = ()
        associations: tuple[AssociatedItem, ...] = ()

        if gate_active:
            started = time.perf_counter()
            masked = self.cv2.bitwise_and(frame, frame, mask=self.mask)
            timings["mask"] = _elapsed_ms(started)
            started = time.perf_counter()
            detections = tuple(
                detection
                for detection in self.item_detector.detect(
                    masked,
                    track=self.integrated_mode,
                )
                if detection.confidence >= self.config.thresholds.item_confidence
            )
            timings["item_inference"] = _elapsed_ms(started)

            started = time.perf_counter()
            if self.integrated_mode:
                opponents = tuple(
                    detection
                    for detection in detections
                    if detection.label == self.config.association.opponent_label
                )
                items = tuple(
                    detection
                    for detection in detections
                    if detection.label != self.config.association.opponent_label
                )
                associations = associate_items(
                    opponents,
                    items,
                    self.config.association,
                )
                self.tracker.update_associations(
                    associations,
                    now,
                    self.config.alerts,
                )
            else:
                self.tracker.update_legacy(
                    detections,
                    now,
                    self.config.alerts,
                )
        elif self.integrated_mode:
            started = time.perf_counter()
            self.tracker.update_associations((), now, self.config.alerts)
        else:
            started = time.perf_counter()

        alerts = rank_nearest(
            self.tracker.visible(now),
            self.config.alerts.max_visible,
        )
        timings["association_tracking_ranking"] = _elapsed_ms(started)
        return FrameResult(
            gate_active=gate_active,
            mode="integrated" if self.integrated_mode else "legacy",
            detections=detections,
            associations=associations,
            alerts=alerts,
            timings_ms=timings,
        )

    def _gate_active(self, frame) -> bool:
        if not self.config.gate_enabled or self.gate_detector is None:
            return True
        region = self.gate_region
        crop = frame[region.y1 : region.y2, region.x1 : region.x2]
        return any(
            detection.confidence >= self.config.thresholds.gate_confidence
            for detection in self.gate_detector.detect(crop)
        )

    def _build_mask(self):
        upper_y, lower_y = compute_item_mask_bounds(
            self.frame_height,
            self.config.item_mask,
        )
        mask = self.np.ones(
            (self.frame_height, self.frame_width),
            dtype=self.np.uint8,
        ) * 255
        mask[:upper_y, :] = 0
        mask[lower_y:, :] = 0
        region: Rect = self.gate_region
        mask[region.y1 : region.y2, region.x1 : region.x2] = 0
        return mask


def _elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000.0
