from fastapi import APIRouter, Query

from app.schemas.ai_schema import PredictionResponse, TrainModelResponse
from app.services.prediction_service import PredictionService


router = APIRouter(prefix="/predictions", tags=["ai-predictions"])
prediction_service = PredictionService()


@router.post("/train", response_model=TrainModelResponse)
def train_congestion_model(csv_path: str | None = Query(default=None)) -> TrainModelResponse:
    return prediction_service.train(csv_path)


@router.get("", response_model=PredictionResponse)
def predict_congestion(csv_path: str | None = Query(default=None)) -> PredictionResponse:
    return prediction_service.predict(csv_path)

