from fastapi import APIRouter, Query

from app.schemas.analytics_schema import (
    AnalyticsSummaryResponse,
    ProcessVideoRequest,
    ProcessVideoResponse,
    TrafficTimelinePoint,
)
from app.services.analytics_service import AnalyticsService
from app.services.processing_service import ProcessingService


router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()
processing_service = ProcessingService()


@router.get("", response_model=AnalyticsSummaryResponse)
def get_analytics(csv_path: str | None = Query(default=None)) -> AnalyticsSummaryResponse:
    return analytics_service.get_summary(csv_path)


@router.get("/timeline", response_model=list[TrafficTimelinePoint])
def get_timeline(
    csv_path: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[TrafficTimelinePoint]:
    return analytics_service.get_timeline(csv_path=csv_path, limit=limit)


@router.post("/process", response_model=ProcessVideoResponse)
def process_video(request: ProcessVideoRequest) -> ProcessVideoResponse:
    return processing_service.process_video(request)

