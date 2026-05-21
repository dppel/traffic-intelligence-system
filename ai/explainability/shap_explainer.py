from pathlib import Path

import joblib
import shap

from ai.training.dataset import TrafficDatasetBuilder
from ai.training.train_congestion_model import DEFAULT_MODEL_PATH


class ShapExplanationService:
    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.dataset_builder = TrafficDatasetBuilder()

    def explain_latest_prediction(self, csv_path: str | None = None) -> dict:
        if not self.model_path.exists():
            raise FileNotFoundError("Congestion model not found. Train it with POST /predictions/train first.")

        bundle = joblib.load(self.model_path)
        model = bundle["model"]
        feature_columns = bundle["feature_columns"]
        feature_row = self.dataset_builder.latest_feature_row(csv_path)
        if feature_row.empty:
            raise ValueError("No analytics data available for explanation.")

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(feature_row[feature_columns])
        values = shap_values[0].tolist()
        base_value = float(explainer.expected_value)

        contributions = sorted(
            [
                {
                    "feature": feature,
                    "value": float(feature_row.iloc[0][feature]),
                    "shap_value": round(float(shap_value), 4),
                }
                for feature, shap_value in zip(feature_columns, values)
            ],
            key=lambda item: abs(item["shap_value"]),
            reverse=True,
        )

        return {
            "base_value": round(base_value, 4),
            "top_features": contributions[:5],
            "all_features": contributions,
            "interpretation": self._build_interpretation(contributions[:3]),
        }

    def _build_interpretation(self, top_features: list[dict]) -> str:
        if not top_features:
            return "No feature contribution was available."

        feature_names = ", ".join(item["feature"] for item in top_features)
        return f"The prediction is mostly influenced by: {feature_names}."

