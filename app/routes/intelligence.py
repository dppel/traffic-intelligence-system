from fastapi import APIRouter, Query

from app.schemas.ai_schema import ExplanationResponse, IntelligenceSummaryResponse
from app.services.explainability_service import ExplainabilityService
from app.services.intelligence_service import IntelligenceService


router = APIRouter(prefix="/intelligence", tags=["ai-intelligence"])
intelligence_service = IntelligenceService()
explainability_service = ExplainabilityService()


@router.get("/summary", response_model=IntelligenceSummaryResponse)
def get_intelligence_summary(csv_path: str | None = Query(default=None)) -> IntelligenceSummaryResponse:
    return intelligence_service.summarize_patterns(csv_path)


@router.get("/explanations", response_model=ExplanationResponse)
def explain_prediction(csv_path: str | None = Query(default=None)) -> ExplanationResponse:
    return explainability_service.explain(csv_path)

