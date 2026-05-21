from fastapi import HTTPException

from ai.prediction.congestion_predictor import CongestionPredictor
from ai.training.train_congestion_model import CongestionModelTrainer
from app.schemas.ai_schema import PredictionResponse, TrainModelResponse


class PredictionService:
    def __init__(self) -> None:
        self.trainer = CongestionModelTrainer()
        self.predictor = CongestionPredictor()

    def train(self, csv_path: str | None = None) -> TrainModelResponse:
        try:
            metrics = self.trainer.train(csv_path)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return TrainModelResponse(**metrics)

    def predict(self, csv_path: str | None = None) -> PredictionResponse:
        try:
            prediction = self.predictor.predict_latest(csv_path)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return PredictionResponse(**prediction)

