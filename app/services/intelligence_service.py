from fastapi import HTTPException

from ai.training.dataset import TrafficDatasetBuilder
from app.schemas.ai_schema import IntelligenceSummaryResponse


class IntelligenceService:
    def __init__(self) -> None:
        self.dataset_builder = TrafficDatasetBuilder()

    def summarize_patterns(self, csv_path: str | None = None) -> IntelligenceSummaryResponse:
        history = self.dataset_builder.load_history(csv_path)
        if history.empty:
            raise HTTPException(status_code=404, detail="No analytics history found.")

        peak_active = int(history["active_vehicles"].max())
        average_active = round(float(history["active_vehicles"].mean()), 2)
        peak_congestion = round(float(history["congestion_score"].max()), 2)
        dominant_level = str(history["congestion_level"].mode().iloc[0])
        source_files = int(history["source_csv"].nunique())

        insights = [
            f"Analyzed {len(history)} frame-level records from {source_files} analytics files.",
            f"Peak active vehicles reached {peak_active}.",
            f"Average active vehicles per frame is {average_active}.",
            f"Peak congestion score is {peak_congestion}.",
            f"Dominant congestion pattern is {dominant_level}.",
        ]

        if peak_congestion >= 65.0:
            insights.append("High congestion patterns exist in the historical data.")
        elif peak_congestion >= 35.0:
            insights.append("Medium congestion appears occasionally and should be monitored.")
        else:
            insights.append("Historical data mostly reflects low congestion conditions.")

        return IntelligenceSummaryResponse(
            total_rows=int(len(history)),
            source_files=source_files,
            peak_active_vehicles=peak_active,
            average_active_vehicles=average_active,
            peak_congestion_score=peak_congestion,
            dominant_congestion_level=dominant_level,
            insight_summary=insights,
        )

