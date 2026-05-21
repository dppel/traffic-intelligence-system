from pydantic import BaseModel


class VideoFile(BaseModel):
    name: str
    path: str
    size_bytes: int
    frame_count: int
    fps: float
    width: int
    height: int


class VideoListResponse(BaseModel):
    videos: list[VideoFile]

