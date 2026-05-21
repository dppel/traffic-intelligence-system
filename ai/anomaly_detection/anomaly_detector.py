import pandas as pd
from sklearn.ensemble import IsolationForest

from ai.training.dataset import TrafficDatasetBuilder


ANOMALY_FEATURES = [
    "active_vehicles",
    "unique_vehicles",
    "average_speed_pixels_per_frame",
    "congestion_score",
]


class TrafficAnomalyDetector:
    def __init__(self) -> None:
        self.dataset_builder = TrafficDatasetBuilder()

    def detect(self, csv_path: str | None = None, limit: int = 50) -> list[dict[str, int | float | str]]:
        history = self.dataset_builder.load_history(csv_path)
        if history.empty or len(history) < 8:
            return []

        dataframe = history.copy()
        features = dataframe[ANOMALY_FEATURES].fillna(0.0)
        model = IsolationForest(contamination="auto", random_state=42)
        dataframe["anomaly_label"] = model.fit_predict(features)
        dataframe["anomaly_score"] = model.decision_function(features)

        anomalies = dataframe[dataframe["anomaly_label"] == -1].sort_values("anomaly_score").head(limit)
        return [self._row_to_event(row) for row in anomalies.itertuples(index=False)]

    def _row_to_event(self, row) -> dict[str, int | float | str]:
        severity = "high" if float(row.congestion_score) >= 65.0 else "medium"
        return {
            "event_type": "ml_anomaly",
            "timestamp_seconds": float(row.timestamp_seconds),
            "frame_index": int(row.frame_index),
            "severity": severity,
            "summary": (
                f"ML anomaly detected with {int(row.active_vehicles)} active vehicles "
                f"and congestion score {float(row.congestion_score):.1f}."
            ),
            "value": round(float(row.anomaly_score), 4),
            "source_csv": str(row.source_csv),
        }
