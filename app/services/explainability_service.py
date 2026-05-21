from fastapi import HTTPException

from ai.explainability.shap_explainer import ShapExplanationService
from app.schemas.ai_schema import ExplanationResponse


class ExplainabilityService:
    def __init__(self) -> None:
        self.explainer = ShapExplanationService()

    def explain(self, csv_path: str | None = None) -> ExplanationResponse:
        try:
            explanation = self.explainer.explain_latest_prediction(csv_path)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return ExplanationResponse(**explanation)

