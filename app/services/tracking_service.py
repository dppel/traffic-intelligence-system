from src.tracker import TrackedVehicle, VehicleTracker


class TrackingService:
    """Thin backend adapter around the Phase 2 tracker."""

    def __init__(self, model_path: str = "models/yolov8n.pt", confidence: float = 0.35):
        self.tracker = VehicleTracker(model_path=model_path, confidence=confidence)

    def track_frame(self, frame) -> list[TrackedVehicle]:
        return self.tracker.track(frame)

