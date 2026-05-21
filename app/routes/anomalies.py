from fastapi import APIRouter, Query

from app.schemas.ai_schema import AnomalyResponse
from app.services.anomaly_service import AnomalyService


router = APIRouter(prefix="/anomalies", tags=["ai-anomalies"])
anomaly_service = AnomalyService()


@router.get("", response_model=list[AnomalyResponse])
def detect_anomalies(
    csv_path: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[AnomalyResponse]:
    return anomaly_service.detect(csv_path=csv_path, limit=limit)
