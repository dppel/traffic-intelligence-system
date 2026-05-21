from pydantic import BaseModel, Field


class TrainModelResponse(BaseModel):
    training_rows: int
    feature_count: int
    mae: float
    r2: float
    model_path: str


class PredictionResponse(BaseModel):
    predicted_congestion_score: float
    predicted_congestion_level: str
    model_path: str
    input_features: dict[str, float]


class AnomalyResponse(BaseModel):
    event_type: str
    timestamp_seconds: float
    frame_index: int
    severity: str
    summary: str
    value: float
    source_csv: str


class IntelligenceSummaryResponse(BaseModel):
    total_rows: int
    source_files: int
    peak_active_vehicles: int
    average_active_vehicles: float
    peak_congestion_score: float
    dominant_congestion_level: str
    insight_summary: list[str] = Field(default_factory=list)


class FeatureContribution(BaseModel):
    feature: str
    value: float
    shap_value: float


class ExplanationResponse(BaseModel):
    base_value: float
    top_features: list[FeatureContribution]
    all_features: list[FeatureContribution]
    interpretation: str

