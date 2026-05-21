from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.video_schema import VideoListResponse
from app.services.video_library_service import VideoLibraryService


router = APIRouter(prefix="/videos", tags=["videos"])
video_library_service = VideoLibraryService()


@router.get("", response_model=VideoListResponse)
def list_videos() -> VideoListResponse:
    return video_library_service.list_videos()


@router.get("/{video_name}/stream")
def stream_video(video_name: str) -> FileResponse:
    video_path = video_library_service.get_video_path(video_name)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found in library.")
    return FileResponse(str(video_path), media_type="video/mp4")


