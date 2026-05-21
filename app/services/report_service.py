import json
from pathlib import Path

from fastapi import HTTPException

from app.schemas.analytics_schema import TrafficEvent
from app.schemas.report_schema import JsonReportResponse, ReportDetailResponse, ReportListItem, ReportsResponse
from app.services.analytics_service import AnalyticsService
from app.services.event_service import EventDetectionService
from app.utils.paths import ANALYTICS_DIR, REPORTS_DIR, latest_file, resolve_project_path


class ReportService:
    def __init__(self) -> None:
        self.analytics_service = AnalyticsService()
        self.event_service = EventDetectionService()

    def list_reports(self) -> ReportsResponse:
        reports = self._list_files(REPORTS_DIR, "*.txt") + self._list_files(REPORTS_DIR, "*.json")
        analytics_exports = self._list_files(ANALYTICS_DIR, "*.csv")
        return ReportsResponse(reports=reports, analytics_exports=analytics_exports)

    def read_report(self, report_path: str | None = None) -> ReportDetailResponse:
        resolved_path = resolve_project_path(report_path) if report_path else latest_file(REPORTS_DIR, "*.txt")
        if resolved_path is None or not resolved_path.exists():
            raise HTTPException(status_code=404, detail="Report not found.")

        return ReportDetailResponse(
            name=resolved_path.name,
            path=str(resolved_path),
            content=resolved_path.read_text(encoding="utf-8"),
        )

    def generate_json_report(
        self,
        csv_path: str | None = None,
        output_path: str = "reports/dashboard_summary.json",
    ) -> JsonReportResponse:
        dataframe, _ = self.analytics_service.load_frame_metrics(csv_path)
        summary = self.analytics_service.get_summary(csv_path).model_dump()
        events = self.event_service.detect_events(dataframe)

        resolved_output_path = resolve_project_path(output_path)
        resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": summary,
            "events": [event.model_dump() for event in events],
        }
        resolved_output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return JsonReportResponse(
            output_path=str(resolved_output_path),
            summary=summary,
            events=[self._event_to_dict(event) for event in events],
        )

    def _list_files(self, directory: Path, pattern: str) -> list[ReportListItem]:
        files = sorted(directory.glob(pattern), key=lambda file: file.stat().st_mtime, reverse=True)
        return [
            ReportListItem(
                name=file.name,
                path=str(file),
                size_bytes=file.stat().st_size,
                modified_timestamp=file.stat().st_mtime,
            )
            for file in files
        ]

    def _event_to_dict(self, event: TrafficEvent) -> dict[str, int | float | str]:
        return event.model_dump()

