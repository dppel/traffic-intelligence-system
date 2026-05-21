from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    processed_frames: int
    total_unique_vehicles: int
    incoming_vehicles: int = 0
    outgoing_vehicles: int = 0
    average_active_vehicles: float
    peak_active_vehicles: int
    peak_congestion_score: float
    dominant_congestion_level: str
    source_csv: str


class TrafficTimelinePoint(BaseModel):
    frame_index: int
    timestamp_seconds: float
    active_vehicles: int
    unique_vehicles: int
    incoming_vehicles: int = 0
    outgoing_vehicles: int = 0
    average_speed_pixels_per_frame: float
    congestion_score: float
    congestion_level: str


class TrafficEvent(BaseModel):
    event_type: str
    timestamp_seconds: float
    frame_index: int
    severity: str
    summary: str
    value: float = Field(description="Metric value that triggered the event.")


class ProcessVideoRequest(BaseModel):
    video_path: str = "data/videos/road_city_5s_360p.mp4"
    max_frames: int | None = 120
    save_output: bool = True
    display: bool = False


class ProcessVideoResponse(BaseModel):
    message: str
    summary: dict[str, int | float | str]

