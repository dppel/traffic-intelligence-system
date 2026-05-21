import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from app.schemas.run_schema import (
    RunAnalyticsResponse,
    RunEventsResponse,
    RunListResponse,
    RunProcessRequest,
    RunProcessResponse,
    RunRecord,
)
from app.services.analytics_service import AnalyticsService
from app.services.event_service import EventDetectionService
from app.storage.run_repository import RunRepository
from app.utils.paths import ANALYTICS_DIR, OUTPUTS_DIR, REPORTS_DIR, resolve_project_path
from src.video_processor import VideoProcessor


class RunService:
    """Coordinates persisted processing runs and historical analytics lookup."""

    def __init__(self) -> None:
        self.repository = RunRepository()
        self.analytics_service = AnalyticsService()
        self.event_service = EventDetectionService()

    def process_video(self, request: RunProcessRequest) -> RunProcessResponse:
        run = self.enqueue_video_processing(request)
        run = self.execute_processing_run(run.run_id, request, raise_on_error=True)
        return RunProcessResponse(message="Video processed and stored successfully.", run=run)

    def enqueue_video_processing(self, request: RunProcessRequest) -> RunRecord:
        run_id = self._create_run_id()
        paths = self._build_run_paths(run_id)
        run = self.repository.create_run(
            run_id=run_id,
            video_path=request.video_path,
            max_frames=request.max_frames,
            analytics_csv_path=str(paths["analytics_csv"]),
            report_path=str(paths["report"]),
            output_video_path=str(paths["output_video"]),
        )
        return RunRecord(**run)

    def execute_processing_run(
        self,
        run_id: str,
        request: RunProcessRequest,
        raise_on_error: bool = False,
    ) -> RunRecord:
        paths = self._build_run_paths(run_id)
        try:
            processor = VideoProcessor(display=request.display, save_output=request.save_output)
            summary = processor.process(
                video_path=request.video_path,
                output_video_path=str(paths["output_video"]),
                analytics_csv_path=str(paths["analytics_csv"]),
                report_path=str(paths["report"]),
                max_frames=request.max_frames,
            )
            dataframe, _ = self.analytics_service.load_frame_metrics(str(paths["analytics_csv"]))
            events = [event.model_dump() for event in self.event_service.detect_events(dataframe)]
            json_report_path = self._write_json_report(paths["json_report"], summary, events)
            run = self.repository.mark_completed(
                run_id=run_id,
                summary=summary,
                events=events,
                json_report_path=str(json_report_path),
            )
        except Exception as exc:
            run = self.repository.mark_failed(run_id, str(exc))
            if raise_on_error:
                raise HTTPException(status_code=500, detail=f"Run failed: {exc}") from exc

        return RunRecord(**run)

    def list_runs(self, limit: int = 50) -> RunListResponse:
        runs = [RunRecord(**run) for run in self.repository.list_runs(limit=limit)]
        return RunListResponse(runs=runs)

    def get_run(self, run_id: str) -> RunRecord:
        return RunRecord(**self._get_run_or_404(run_id))

    def get_run_analytics(self, run_id: str, limit: int = 100) -> RunAnalyticsResponse:
        run = self._get_run_or_404(run_id)
        if run["status"] != "completed":
            raise HTTPException(status_code=409, detail=f"Run is not completed. Current status: {run['status']}")

        csv_path = run["analytics_csv_path"]
        summary = self.analytics_service.get_summary(csv_path).model_dump()
        timeline = [point.model_dump() for point in self.analytics_service.get_timeline(csv_path, limit=limit)]
        return RunAnalyticsResponse(run_id=run_id, summary=summary, timeline=timeline)

    def get_run_events(self, run_id: str) -> RunEventsResponse:
        run = self._get_run_or_404(run_id)
        if run["status"] != "completed":
            raise HTTPException(status_code=409, detail=f"Run is not completed. Current status: {run['status']}")

        dataframe, _ = self.analytics_service.load_frame_metrics(run["analytics_csv_path"])
        events = self.event_service.detect_events(dataframe)
        return RunEventsResponse(run_id=run_id, events=events)

    def get_run_report(self, run_id: str) -> dict[str, str]:
        run = self._get_run_or_404(run_id)
        report_path = resolve_project_path(run["report_path"])
        json_report_path = resolve_project_path(run["json_report_path"]) if run.get("json_report_path") else None

        if not report_path.exists():
            raise HTTPException(status_code=404, detail=f"Report file not found for run: {run_id}")

        return {
            "run_id": run_id,
            "report_path": str(report_path),
            "json_report_path": str(json_report_path) if json_report_path else "",
            "content": report_path.read_text(encoding="utf-8"),
        }

    def get_run_video_path(self, run_id: str) -> Path:
        run = self._get_run_or_404(run_id)
        if not run.get("output_video_path"):
            raise HTTPException(status_code=404, detail=f"No output video registered for run: {run_id}")
        video_path = resolve_project_path(run["output_video_path"])
        return video_path


    def _get_run_or_404(self, run_id: str) -> dict:
        try:
            return self.repository.get_run(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}") from exc

    def _build_run_paths(self, run_id: str) -> dict[str, Path]:
        analytics_dir = ANALYTICS_DIR / "runs"
        reports_dir = REPORTS_DIR / "runs"
        outputs_dir = OUTPUTS_DIR / "runs"
        analytics_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)
        outputs_dir.mkdir(parents=True, exist_ok=True)

        return {
            "analytics_csv": analytics_dir / f"{run_id}_frame_metrics.csv",
            "report": reports_dir / f"{run_id}_summary.txt",
            "json_report": reports_dir / f"{run_id}_dashboard.json",
            "output_video": outputs_dir / f"{run_id}_processed.mp4",
        }

    def _write_json_report(self, output_path: Path, summary: dict, events: list[dict]) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({"summary": summary, "events": events}, indent=2),
            encoding="utf-8",
        )
        return output_path

    def _create_run_id(self) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        suffix = uuid4().hex[:8]
        return f"run_{timestamp}_{suffix}"
