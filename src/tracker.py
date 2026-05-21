from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.detector import VEHICLE_CLASS_IDS, VehicleDetector


@dataclass(frozen=True)
class TrackedVehicle:
    track_id: int
    class_id: int
    label: str
    confidence: float
    box: tuple[int, int, int, int]
    center: tuple[int, int]
    speed_pixels_per_frame: float


class VehicleTracker:
    """ByteTrack wrapper that converts YOLO tracking output into app-level objects."""

    def __init__(self, model_path: str = "models/yolov8n.pt", confidence: float = 0.35):
        self.detector = VehicleDetector(model_path=model_path, confidence=confidence)
        self.previous_centers: dict[int, tuple[int, int]] = {}

    def track(self, frame: np.ndarray) -> list[TrackedVehicle]:
        results = self.detector.model.track(
            frame,
            conf=self.detector.confidence,
            classes=list(VEHICLE_CLASS_IDS.keys()),
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )

        tracked_vehicles: list[TrackedVehicle] = []
        if not results:
            return tracked_vehicles

        boxes = results[0].boxes
        if boxes is None or boxes.id is None:
            return tracked_vehicles

        for box in boxes:
            class_id = int(box.cls[0])
            if class_id not in VEHICLE_CLASS_IDS:
                continue

            track_id = int(box.id[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_tuple = (int(x1), int(y1), int(x2), int(y2))
            center = ((box_tuple[0] + box_tuple[2]) // 2, (box_tuple[1] + box_tuple[3]) // 2)
            speed = self._estimate_speed(track_id, center)

            tracked_vehicles.append(
                TrackedVehicle(
                    track_id=track_id,
                    class_id=class_id,
                    label=VEHICLE_CLASS_IDS[class_id],
                    confidence=float(box.conf[0]),
                    box=box_tuple,
                    center=center,
                    speed_pixels_per_frame=speed,
                )
            )

        self._keep_only_active_tracks(tracked_vehicles)
        return tracked_vehicles

    def _estimate_speed(self, track_id: int, center: tuple[int, int]) -> float:
        previous_center = self.previous_centers.get(track_id)
        self.previous_centers[track_id] = center

        if previous_center is None:
            return 0.0

        dx = center[0] - previous_center[0]
        dy = center[1] - previous_center[1]
        return float((dx * dx + dy * dy) ** 0.5)

    def _keep_only_active_tracks(self, vehicles: list[TrackedVehicle]) -> None:
        active_ids = {vehicle.track_id for vehicle in vehicles}
        self.previous_centers = {
            track_id: center
            for track_id, center in self.previous_centers.items()
            if track_id in active_ids
        }

