from fastapi import APIRouter, BackgroundTasks, Query, HTTPException
from fastapi.responses import FileResponse

from app.schemas.run_schema import (
    RunAnalyticsResponse,
    RunEventsResponse,
    RunListResponse,
    RunProcessRequest,
    RunProcessResponse,
    RunRecord,
)
from app.services.run_service import RunService


router = APIRouter(prefix="/runs", tags=["runs"])
run_service = RunService()


@router.post("/process", response_model=RunProcessResponse)
def process_run(request: RunProcessRequest, background_tasks: BackgroundTasks) -> RunProcessResponse:
    run = run_service.enqueue_video_processing(request)
    background_tasks.add_task(run_service.execute_processing_run, run.run_id, request)
    return RunProcessResponse(message="Video processing queued.", run=run)


@router.post("/process-sync", response_model=RunProcessResponse)
def process_run_sync(request: RunProcessRequest) -> RunProcessResponse:
    return run_service.process_video(request)


@router.get("", response_model=RunListResponse)
def list_runs(limit: int = Query(default=50, ge=1, le=200)) -> RunListResponse:
    return run_service.list_runs(limit=limit)


@router.get("/{run_id}", response_model=RunRecord)
def get_run(run_id: str) -> RunRecord:
    return run_service.get_run(run_id)


@router.get("/{run_id}/analytics", response_model=RunAnalyticsResponse)
def get_run_analytics(
    run_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
) -> RunAnalyticsResponse:
    return run_service.get_run_analytics(run_id=run_id, limit=limit)


@router.get("/{run_id}/events", response_model=RunEventsResponse)
def get_run_events(run_id: str) -> RunEventsResponse:
    return run_service.get_run_events(run_id)


@router.get("/{run_id}/report")
def get_run_report(run_id: str) -> dict[str, str]:
    return run_service.get_run_report(run_id)


@router.get("/{run_id}/video")
def get_run_video(run_id: str) -> FileResponse:
    video_path = run_service.get_run_video_path(run_id)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Run video file not found.")
    return FileResponse(str(video_path), media_type="video/mp4")

