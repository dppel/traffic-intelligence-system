from pathlib import Path

import pandas as pd

from app.utils.paths import ANALYTICS_DIR, resolve_project_path


FEATURE_COLUMNS = [
    "frame_index",
    "timestamp_seconds",
    "active_vehicles",
    "unique_vehicles",
    "average_speed_pixels_per_frame",
    "active_vehicles_lag_1",
    "active_vehicles_rolling_mean_5",
    "average_speed_rolling_mean_5",
    "congestion_score_lag_1",
    "active_vehicle_delta",
]

TARGET_COLUMN = "future_congestion_score"


class TrafficDatasetBuilder:
    """Builds supervised ML datasets from Phase 2/4 frame analytics CSV files."""

    required_columns = {
        "frame_index",
        "timestamp_seconds",
        "active_vehicles",
        "unique_vehicles",
        "average_speed_pixels_per_frame",
        "congestion_score",
        "congestion_level",
    }

    def load_history(self, csv_path: str | None = None) -> pd.DataFrame:
        csv_files = [resolve_project_path(csv_path)] if csv_path else self._discover_csv_files()
        frames: list[pd.DataFrame] = []

        for file_path in csv_files:
            if not file_path.exists():
                continue
            dataframe = pd.read_csv(file_path)
            if not self.required_columns.issubset(dataframe.columns):
                continue
            dataframe = dataframe.copy()
            dataframe["source_csv"] = str(file_path)
            frames.append(dataframe)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def build_supervised_dataset(self, csv_path: str | None = None) -> pd.DataFrame:
        history = self.load_history(csv_path)
        if history.empty:
            return history

        prepared_frames: list[pd.DataFrame] = []
        for _, group in history.groupby("source_csv"):
            prepared = group.sort_values("frame_index").copy()
            prepared["active_vehicles_lag_1"] = prepared["active_vehicles"].shift(1)
            prepared["congestion_score_lag_1"] = prepared["congestion_score"].shift(1)
            prepared["active_vehicle_delta"] = prepared["active_vehicles"].diff()
            prepared["active_vehicles_rolling_mean_5"] = (
                prepared["active_vehicles"].rolling(window=5, min_periods=1).mean()
            )
            prepared["average_speed_rolling_mean_5"] = (
                prepared["average_speed_pixels_per_frame"].rolling(window=5, min_periods=1).mean()
            )
            prepared[TARGET_COLUMN] = prepared["congestion_score"].shift(-1)
            prepared_frames.append(prepared)

        dataset = pd.concat(prepared_frames, ignore_index=True)
        dataset[FEATURE_COLUMNS + [TARGET_COLUMN]] = dataset[FEATURE_COLUMNS + [TARGET_COLUMN]].fillna(0.0)
        return dataset

    def latest_feature_row(self, csv_path: str | None = None) -> pd.DataFrame:
        dataset = self.build_supervised_dataset(csv_path)
        if dataset.empty:
            return dataset
        return dataset.tail(1)[FEATURE_COLUMNS]

    def _discover_csv_files(self) -> list[Path]:
        return sorted(ANALYTICS_DIR.glob("*.csv")) + sorted((ANALYTICS_DIR / "runs").glob("*.csv"))

