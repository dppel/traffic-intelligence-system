import cv2
from pathlib import Path

from app.schemas.video_schema import VideoFile, VideoListResponse
from app.utils.paths import VIDEOS_DIR


class VideoLibraryService:
    def list_videos(self) -> VideoListResponse:
        videos: list[VideoFile] = []

        for video_path in sorted(VIDEOS_DIR.glob("*.mp4")):
            capture = cv2.VideoCapture(str(video_path))
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) if capture.isOpened() else 0
            fps = float(capture.get(cv2.CAP_PROP_FPS)) if capture.isOpened() else 0.0
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) if capture.isOpened() else 0
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) if capture.isOpened() else 0
            capture.release()

            videos.append(
                VideoFile(
                    name=video_path.name,
                    path=f"data/videos/{video_path.name}",
                    size_bytes=video_path.stat().st_size,
                    frame_count=frame_count,
                    fps=round(fps, 2),
                    width=width,
                    height=height,
                )
            )

        return VideoListResponse(videos=videos)

    def get_video_path(self, video_name: str) -> Path:
        return VIDEOS_DIR / video_name


