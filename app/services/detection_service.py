from src.detector import Detection, VehicleDetector


class DetectionService:
    """Thin backend adapter around the Phase 1 detector."""

    def __init__(self, model_path: str = "models/yolov8n.pt", confidence: float = 0.35):
        self.detector = VehicleDetector(model_path=model_path, confidence=confidence)

    def detect_frame(self, frame) -> list[Detection]:
        return self.detector.detect(frame)

