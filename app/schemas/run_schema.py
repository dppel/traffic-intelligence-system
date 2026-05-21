from pydantic import BaseModel, Field

from app.schemas.analytics_schema import ProcessVideoRequest, TrafficEvent


class RunRecord(BaseModel):
    run_id: str
    video_path: str
    status: str
    created_at: str
    completed_at: str | None = None
    max_frames: int | None = None
    analytics_csv_path: str | None = None
    report_path: str | None = None
    output_video_path: str | None = None
    json_report_path: str | None = None
    summary: dict[str, int | float | str] = Field(default_factory=dict)
    events: list[dict[str, int | float | str]] = Field(default_factory=list)
    error_message: str | None = None


class RunListResponse(BaseModel):
    runs: list[RunRecord]


class RunProcessRequest(ProcessVideoRequest):
    pass


class RunProcessResponse(BaseModel):
    message: str
    run: RunRecord


class RunAnalyticsResponse(BaseModel):
    run_id: str
    summary: dict[str, int | float | str]
    timeline: list[dict[str, int | float | str]]


class RunEventsResponse(BaseModel):
    run_id: str
    events: list[TrafficEvent]
