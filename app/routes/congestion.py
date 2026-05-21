from fastapi import APIRouter, Query

from app.schemas.analytics_schema import TrafficEvent
from app.services.analytics_service import AnalyticsService
from app.services.event_service import EventDetectionService


router = APIRouter(tags=["traffic-events"])
analytics_service = AnalyticsService()
event_service = EventDetectionService()


@router.get("/events", response_model=list[TrafficEvent])
def get_events(csv_path: str | None = Query(default=None)) -> list[TrafficEvent]:
    dataframe, _ = analytics_service.load_frame_metrics(csv_path)
    return event_service.detect_events(dataframe)


@router.get("/congestion")
def get_congestion(csv_path: str | None = Query(default=None)) -> dict[str, int | float | str]:
    dataframe, source_path = analytics_service.load_frame_metrics(csv_path)
    if dataframe.empty:
        return {
            "source_csv": str(source_path),
            "peak_congestion_score": 0.0,
            "dominant_congestion_level": "Unknown",
            "high_congestion_frames": 0,
            "medium_congestion_frames": 0,
        }

    return {
        "source_csv": str(source_path),
        "peak_congestion_score": round(float(dataframe["congestion_score"].max()), 2),
        "dominant_congestion_level": str(dataframe["congestion_level"].mode().iloc[0]),
        "high_congestion_frames": int((dataframe["congestion_score"] >= 65.0).sum()),
        "medium_congestion_frames": int(
            ((dataframe["congestion_score"] >= 35.0) & (dataframe["congestion_score"] < 65.0)).sum()
        ),
    }

