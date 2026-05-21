from pathlib import Path

import joblib
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ai.training.dataset import FEATURE_COLUMNS, TARGET_COLUMN, TrafficDatasetBuilder
from app.utils.paths import PROJECT_ROOT


DEFAULT_MODEL_PATH = PROJECT_ROOT / "ai" / "models" / "congestion_xgb.joblib"


class CongestionModelTrainer:
    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.dataset_builder = TrafficDatasetBuilder()

    def train(self, csv_path: str | None = None) -> dict[str, int | float | str]:
        dataset = self.dataset_builder.build_supervised_dataset(csv_path)
        if dataset.empty or len(dataset) < 10:
            raise ValueError("Not enough analytics history to train a congestion model. Process more frames first.")

        X = dataset[FEATURE_COLUMNS]
        y = dataset[TARGET_COLUMN]

        test_size = 0.25 if len(dataset) >= 40 else 0.2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        model = XGBRegressor(
            n_estimators=80,
            max_depth=3,
            learning_rate=0.08,
            objective="reg:squarederror",
            random_state=42,
        )
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        metrics = {
            "training_rows": int(len(dataset)),
            "feature_count": int(len(FEATURE_COLUMNS)),
            "mae": round(float(mean_absolute_error(y_test, predictions)), 3),
            "r2": round(float(r2_score(y_test, predictions)), 3) if len(y_test) > 1 else 0.0,
            "model_path": str(self.model_path),
        }

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": model,
                "feature_columns": FEATURE_COLUMNS,
                "metrics": metrics,
            },
            self.model_path,
        )
        return metrics

