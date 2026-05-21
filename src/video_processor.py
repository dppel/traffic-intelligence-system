from pathlib import Path
from time import perf_counter

import cv2

from src.analytics import FrameAnalytics, TrafficAnalyticsRecorder
from src.congestion import CongestionEstimator
from src.counter import VehicleCounter
from src.tracker import VehicleTracker
from src.utils import validate_file
from src.visualization import draw_traffic_overlay, draw_tracked_vehicles, draw_counting_line


class VideoProcessor:
    """Coordinates tracking, counting, congestion estimation, and analytics export."""

    def __init__(
        self,
        model_path: str = "models/yolov8n.pt",
        confidence: float = 0.35,
        display: bool = True,
        save_output: bool = False,
    ):
        self.tracker = VehicleTracker(model_path=model_path, confidence=confidence)
        self.counter = VehicleCounter()
        self.congestion_estimator = CongestionEstimator()
        self.analytics = TrafficAnalyticsRecorder()
        self.display = display
        self.save_output = save_output

    def process(
        self,
        video_path: str,
        output_video_path: str | None = None,
        analytics_csv_path: str = "data/analytics/frame_metrics.csv",
        report_path: str = "reports/traffic_summary.txt",
        max_frames: int | None = None,
    ) -> dict[str, float | int | str]:
        validated_video_path = validate_file(video_path)
        capture = cv2.VideoCapture(str(validated_video_path))

        if not capture.isOpened():
            raise RuntimeError(f"Could not open video: {validated_video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if self.counter.counting_line is None:
            # Default horizontal line at 55% frame height
            y = int(height * 0.55)
            self.counter.counting_line = ((0, y), (width, y))

        writer = self._create_writer(output_video_path, fps, width, height)
        frame_index = 0
        previous_time = perf_counter()

        while True:
            success, frame = capture.read()
            if not success:
                break

            vehicles = self.tracker.track(frame)
            self.counter.update(vehicles)
            congestion = self.congestion_estimator.estimate(vehicles, frame.shape)
            current_time = perf_counter()
            measured_fps = 1.0 / max(current_time - previous_time, 1e-6)
            previous_time = current_time

            average_speed = self._average_speed(vehicles)
            self.analytics.add_frame(
                FrameAnalytics(
                    frame_index=frame_index,
                    timestamp_seconds=round(frame_index / fps, 3),
                    active_vehicles=len(vehicles),
                    unique_vehicles=self.counter.total_unique,
                    incoming_vehicles=self.counter.incoming_count,
                    outgoing_vehicles=self.counter.outgoing_count,
                    average_speed_pixels_per_frame=round(average_speed, 3),
                    congestion_score=congestion.score,
                    congestion_level=congestion.level,
                )
            )

            draw_tracked_vehicles(frame, vehicles)
            draw_counting_line(frame, self.counter.counting_line)
            draw_traffic_overlay(
                frame=frame,
                active_vehicle_count=len(vehicles),
                unique_vehicle_count=self.counter.total_unique,
                congestion=congestion,
                fps=measured_fps,
                incoming_count=self.counter.incoming_count,
                outgoing_count=self.counter.outgoing_count,
            )

            if writer is not None:
                writer.write(frame)

            if self.display:
                cv2.imshow("Traffic Intelligence - Phase 2", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_index += 1
            if max_frames is not None and frame_index >= max_frames:
                break

        capture.release()
        if writer is not None:
            writer.release()
        if self.display:
            cv2.destroyAllWindows()

        csv_path = self.analytics.export_csv(analytics_csv_path)
        report = self.analytics.export_summary(report_path, self.counter.summary())
        summary = self.analytics.summary()
        summary["analytics_csv"] = str(csv_path)
        summary["report"] = str(report)
        return summary

    def _create_writer(self, output_video_path: str | None, fps: float, width: int, height: int):
        if not self.save_output:
            return None

        if output_video_path is None:
            output_video_path = "data/outputs/phase2_processed.mp4"

        output_path = Path(output_video_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Try H.264 (avc1) first for web compatibility
        try:
            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            if writer.isOpened():
                return writer
        except Exception:
            pass

        # Fallback to mp4v if avc1 fails
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        return cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    def _average_speed(self, vehicles) -> float:
        if not vehicles:
            return 0.0
        return sum(vehicle.speed_pixels_per_frame for vehicle in vehicles) / len(vehicles)

