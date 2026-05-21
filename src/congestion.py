from dataclasses import dataclass

from src.tracker import TrackedVehicle


@dataclass(frozen=True)
class CongestionResult:
    score: float
    level: str


class CongestionEstimator:
    """Rule-based congestion estimator for early-stage traffic intelligence."""

    def __init__(self, medium_threshold: float = 35.0, high_threshold: float = 65.0):
        self.medium_threshold = medium_threshold
        self.high_threshold = high_threshold

    def estimate(
        self,
        vehicles: list[TrackedVehicle],
        frame_shape: tuple[int, int, int],
    ) -> CongestionResult:
        vehicle_count = len(vehicles)
        occupancy = self._estimate_frame_occupancy(vehicles, frame_shape)
        average_speed = self._average_speed(vehicles)

        count_score = min(vehicle_count / 12.0, 1.0) * 45.0
        occupancy_score = min(occupancy / 0.35, 1.0) * 35.0
        slow_speed_score = max(0.0, 1.0 - min(average_speed / 8.0, 1.0)) * 20.0
        score = round(count_score + occupancy_score + slow_speed_score, 2)

        if score >= self.high_threshold:
            level = "High Congestion"
        elif score >= self.medium_threshold:
            level = "Medium Congestion"
        else:
            level = "Low Congestion"

        return CongestionResult(score=score, level=level)

    def _estimate_frame_occupancy(
        self,
        vehicles: list[TrackedVehicle],
        frame_shape: tuple[int, int, int],
    ) -> float:
        frame_height, frame_width = frame_shape[:2]
        frame_area = max(frame_width * frame_height, 1)
        vehicle_area = 0

        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle.box
            vehicle_area += max(x2 - x1, 0) * max(y2 - y1, 0)

        return vehicle_area / frame_area

    def _average_speed(self, vehicles: list[TrackedVehicle]) -> float:
        if not vehicles:
            return 0.0
        return sum(vehicle.speed_pixels_per_frame for vehicle in vehicles) / len(vehicles)

