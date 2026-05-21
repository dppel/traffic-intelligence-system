from pathlib import Path

import joblib

from ai.training.dataset import TrafficDatasetBuilder
from ai.training.train_congestion_model import DEFAULT_MODEL_PATH


class CongestionPredictor:
    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.dataset_builder = TrafficDatasetBuilder()

    def predict_latest(self, csv_path: str | None = None) -> dict[str, int | float | str]:
        bundle = self._load_model()
        feature_row = self.dataset_builder.latest_feature_row(csv_path)
        if feature_row.empty:
            raise ValueError("No analytics data available for prediction.")

        model = bundle["model"]
        score = float(model.predict(feature_row)[0])
        score = max(0.0, min(score, 100.0))
        level = self._score_to_level(score)

        return {
            "predicted_congestion_score": round(score, 2),
            "predicted_congestion_level": level,
            "model_path": str(self.model_path),
            "input_features": feature_row.iloc[0].to_dict(),
        }

    def _load_model(self) -> dict:
        if not self.model_path.exists():
            raise FileNotFoundError("Congestion model not found. Train it with POST /predictions/train first.")
        return joblib.load(self.model_path)

    def _score_to_level(self, score: float) -> str:
        if score >= 65.0:
            return "High Congestion"
        if score >= 35.0:
            return "Medium Congestion"
        return "Low Congestion"

