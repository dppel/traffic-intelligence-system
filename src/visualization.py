import cv2

from src.congestion import CongestionResult
from src.tracker import TrackedVehicle


def draw_tracked_vehicles(frame, vehicles: list[TrackedVehicle]) -> None:
    for vehicle in vehicles:
        x1, y1, x2, y2 = vehicle.box
        label = f"ID {vehicle.track_id} {vehicle.label} {vehicle.confidence:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 0), 2)
        cv2.circle(frame, vehicle.center, 4, (0, 255, 255), -1)
        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 180, 0),
            2,
        )


def draw_traffic_overlay(
    frame,
    active_vehicle_count: int,
    unique_vehicle_count: int,
    congestion: CongestionResult,
    fps: float,
    incoming_count: int = 0,
    outgoing_count: int = 0,
) -> None:
    overlay_lines = [
        f"Active vehicles: {active_vehicle_count}",
        f"Unique (Crossed): {unique_vehicle_count}",
        f"Incoming flow: {incoming_count}",
        f"Outgoing flow: {outgoing_count}",
        f"Congestion: {congestion.level} ({congestion.score:.1f})",
        f"FPS: {fps:.1f}",
    ]

    x, y = 20, 35
    line_height = 30
    panel_width = 420
    panel_height = 20 + line_height * len(overlay_lines)

    cv2.rectangle(frame, (10, 10), (10 + panel_width, 10 + panel_height), (20, 20, 20), -1)
    cv2.rectangle(frame, (10, 10), (10 + panel_width, 10 + panel_height), (220, 220, 220), 1)

    for index, line in enumerate(overlay_lines):
        cv2.putText(
            frame,
            line,
            (x, y + index * line_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )


def draw_counting_line(
    frame,
    line: tuple[tuple[int, int], tuple[int, int]] | None,
) -> None:
    if line is None:
        return

    A, B = line
    # Draw a thick neon-cyan tripwire line
    cv2.line(frame, A, B, (255, 255, 0), 3)

    # Draw dynamic indicators near the center of the line
    center_x = (A[0] + B[0]) // 2
    center_y = (A[1] + B[1]) // 2

    cv2.putText(
        frame,
        "OUTGOING ^",
        (center_x - 110, center_y - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 165, 255),
        2,
    )
    cv2.putText(
        frame,
        "INCOMING v",
        (center_x + 20, center_y + 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2,
    )


