from dataclasses import dataclass
import os
from pathlib import Path

YOLO_CONFIG_DIR = Path(".cache/ultralytics").resolve()
YOLO_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(YOLO_CONFIG_DIR))

from ultralytics import YOLO


VEHICLE_CLASS_IDS = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


@dataclass(frozen=True)
class Detection:
    class_id: int
    label: str
    confidence: float
    box: tuple[int, int, int, int]


class VehicleDetector:
    """YOLO-based detector focused on road vehicle classes."""

    def __init__(self, model_path: str = "models/yolov8n.pt", confidence: float = 0.35):
        self.confidence = confidence
        resolved_model_path = Path(model_path)
        self.model = YOLO(str(resolved_model_path if resolved_model_path.exists() else "yolov8n.pt"))

    def detect(self, frame) -> list[Detection]:
        results = self.model(frame, conf=self.confidence, verbose=False)
        detections: list[Detection] = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id not in VEHICLE_CLASS_IDS:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        class_id=class_id,
                        label=VEHICLE_CLASS_IDS[class_id],
                        confidence=float(box.conf[0]),
                        box=(int(x1), int(y1), int(x2), int(y2)),
                    )
                )

        return detections
