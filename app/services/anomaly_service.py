from app.schemas.ai_schema import AnomalyResponse
from ai.anomaly_detection.anomaly_detector import TrafficAnomalyDetector


class AnomalyService:
    def __init__(self) -> None:
        self.detector = TrafficAnomalyDetector()

    def detect(self, csv_path: str | None = None, limit: int = 50) -> list[AnomalyResponse]:
        return [AnomalyResponse(**event) for event in self.detector.detect(csv_path, limit=limit)]
