import argparse

import cv2

from src.detector import VehicleDetector
from src.utils import validate_file
from src.video_processor import VideoProcessor


def draw_detections(frame, detections):
    for detection in detections:
        x1, y1, x2, y2 = detection.box
        label = f"{detection.label} {detection.confidence:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 0), 2)
        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 180, 0),
            2,
        )

    cv2.putText(
        frame,
        f"Vehicles detected: {len(detections)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 0, 255),
        2,
    )


def run_first_frame_test(video_path: str, model_path: str, confidence: float) -> None:
    validated_video_path = validate_file(video_path)
    capture = cv2.VideoCapture(str(validated_video_path))

    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {validated_video_path}")

    success, frame = capture.read()
    capture.release()

    if not success:
        raise RuntimeError(f"Could not read first frame from video: {validated_video_path}")

    detector = VehicleDetector(model_path=model_path, confidence=confidence)
    detections = detector.detect(frame)
    draw_detections(frame, detections)

    print(f"Detected {len(detections)} vehicles in the first frame.")
    cv2.imshow("Traffic Intelligence - First YOLO Test", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Traffic Intelligence & Vehicle Detection System")
    parser.add_argument(
        "--mode",
        choices=["first-frame", "video"],
        default="video",
        help="Run the Phase 1 first-frame test or the Phase 2 video analytics pipeline.",
    )
    parser.add_argument("--video", required=True, help="Path to a local traffic video file.")
    parser.add_argument("--model", default="models/yolov8n.pt", help="Path to YOLO model weights.")
    parser.add_argument("--confidence", type=float, default=0.35, help="Detection confidence threshold.")
    parser.add_argument("--save-output", action="store_true", help="Save processed video to data/outputs.")
    parser.add_argument("--output", default="data/outputs/phase2_processed.mp4", help="Processed video output path.")
    parser.add_argument("--analytics-csv", default="data/analytics/frame_metrics.csv", help="Frame analytics CSV path.")
    parser.add_argument("--report", default="reports/traffic_summary.txt", help="Summary report path.")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional limit for faster test runs.")
    parser.add_argument("--no-display", action="store_true", help="Process without opening an OpenCV window.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.mode == "first-frame":
        run_first_frame_test(args.video, args.model, args.confidence)
    else:
        processor = VideoProcessor(
            model_path=args.model,
            confidence=args.confidence,
            display=not args.no_display,
            save_output=args.save_output,
        )
        summary = processor.process(
            video_path=args.video,
            output_video_path=args.output,
            analytics_csv_path=args.analytics_csv,
            report_path=args.report,
            max_frames=args.max_frames,
        )
        print("Phase 2 processing complete.")
        for key, value in summary.items():
            print(f"{key}: {value}")
