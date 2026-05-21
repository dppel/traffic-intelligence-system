from fastapi import APIRouter, Query

from app.schemas.report_schema import JsonReportResponse, ReportDetailResponse, ReportsResponse
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])
report_service = ReportService()


@router.get("", response_model=ReportsResponse)
def list_reports() -> ReportsResponse:
    return report_service.list_reports()


@router.get("/latest", response_model=ReportDetailResponse)
def get_latest_report(report_path: str | None = Query(default=None)) -> ReportDetailResponse:
    return report_service.read_report(report_path)


@router.post("/generate-json", response_model=JsonReportResponse)
def generate_json_report(
    csv_path: str | None = Query(default=None),
    output_path: str = Query(default="reports/dashboard_summary.json"),
) -> JsonReportResponse:
    return report_service.generate_json_report(csv_path=csv_path, output_path=output_path)

