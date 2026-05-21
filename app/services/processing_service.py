from app.schemas.analytics_schema import ProcessVideoRequest, ProcessVideoResponse
from app.schemas.run_schema import RunProcessRequest
from app.services.run_service import RunService


class ProcessingService:
    def process_video(self, request: ProcessVideoRequest) -> ProcessVideoResponse:
        run_response = RunService().process_video(
            RunProcessRequest(
                video_path=request.video_path,
                max_frames=request.max_frames,
                save_output=request.save_output,
                display=request.display,
            )
        )
        summary = dict(run_response.run.summary)
        summary["run_id"] = run_response.run.run_id
        summary["analytics_csv"] = run_response.run.analytics_csv_path or ""
        summary["report"] = run_response.run.report_path or ""
        return ProcessVideoResponse(message="Video processed and stored successfully.", summary=summary)
