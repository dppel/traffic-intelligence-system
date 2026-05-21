from pathlib import Path

import pandas as pd
from fastapi import HTTPException

from app.schemas.analytics_schema import AnalyticsSummaryResponse, TrafficTimelinePoint
from app.utils.paths import ANALYTICS_DIR, latest_file, resolve_project_path


class AnalyticsService:
    required_columns = {
        "frame_index",
        "timestamp_seconds",
        "active_vehicles",
        "unique_vehicles",
        "average_speed_pixels_per_frame",
        "congestion_score",
        "congestion_level",
    }

    def load_frame_metrics(self, csv_path: str | None = None) -> tuple[pd.DataFrame, Path]:
        resolved_path = self._resolve_csv_path(csv_path)
        if not resolved_path.exists():
            raise HTTPException(status_code=404, detail=f"Analytics CSV not found: {resolved_path}")

        dataframe = pd.read_csv(resolved_path)
        missing_columns = self.required_columns.difference(dataframe.columns)
        if missing_columns:
            raise HTTPException(
                status_code=422,
                detail=f"Analytics CSV is missing columns: {sorted(missing_columns)}",
            )
        return dataframe, resolved_path

    def get_summary(self, csv_path: str | None = None) -> AnalyticsSummaryResponse:
        dataframe, resolved_path = self.load_frame_metrics(csv_path)
        if dataframe.empty:
            raise HTTPException(status_code=422, detail="Analytics CSV is empty.")

        return AnalyticsSummaryResponse(
            processed_frames=int(len(dataframe)),
            total_unique_vehicles=int(dataframe["unique_vehicles"].max()),
            incoming_vehicles=int(dataframe["incoming_vehicles"].max()) if "incoming_vehicles" in dataframe.columns else 0,
            outgoing_vehicles=int(dataframe["outgoing_vehicles"].max()) if "outgoing_vehicles" in dataframe.columns else 0,
            average_active_vehicles=round(float(dataframe["active_vehicles"].mean()), 2),
            peak_active_vehicles=int(dataframe["active_vehicles"].max()),
            peak_congestion_score=round(float(dataframe["congestion_score"].max()), 2),
            dominant_congestion_level=str(dataframe["congestion_level"].mode().iloc[0]),
            source_csv=str(resolved_path),
        )

    def get_timeline(self, csv_path: str | None = None, limit: int = 100) -> list[TrafficTimelinePoint]:
        dataframe, _ = self.load_frame_metrics(csv_path)
        limited = dataframe.head(limit)
        return [
            TrafficTimelinePoint(
                frame_index=int(row.frame_index),
                timestamp_seconds=float(row.timestamp_seconds),
                active_vehicles=int(row.active_vehicles),
                unique_vehicles=int(row.unique_vehicles),
                incoming_vehicles=int(getattr(row, "incoming_vehicles", 0)),
                outgoing_vehicles=int(getattr(row, "outgoing_vehicles", 0)),
                average_speed_pixels_per_frame=float(row.average_speed_pixels_per_frame),
                congestion_score=float(row.congestion_score),
                congestion_level=str(row.congestion_level),
            )
            for row in limited.itertuples(index=False)
        ]

    def _resolve_csv_path(self, csv_path: str | None) -> Path:
        if csv_path:
            return resolve_project_path(csv_path)

        default_path = ANALYTICS_DIR / "frame_metrics.csv"
        if default_path.exists():
            return default_path

        latest_csv = latest_file(ANALYTICS_DIR, "*.csv")
        if latest_csv is not None:
            return latest_csv

        return default_path

