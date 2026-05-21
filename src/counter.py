from collections import Counter
from dataclasses import dataclass, field

from src.tracker import TrackedVehicle


@dataclass
class VehicleCounter:
    """Counts unique tracked vehicles when they cross a virtual tripwire."""

    counting_line: tuple[tuple[int, int], tuple[int, int]] | None = None
    seen_track_ids: set[int] = field(default_factory=set)
    crossed_ids: set[int] = field(default_factory=set)
    previous_centroids: dict[int, tuple[int, int]] = field(default_factory=dict)
    class_counts: Counter = field(default_factory=Counter)
    incoming_count: int = 0
    outgoing_count: int = 0

    def update(self, vehicles: list[TrackedVehicle]) -> None:
        for vehicle in vehicles:
            curr_center = vehicle.center
            prev_center = self.previous_centroids.get(vehicle.track_id)
            self.previous_centroids[vehicle.track_id] = curr_center

            if prev_center is None:
                continue

            if self.counting_line is not None:
                A, B = self.counting_line
                if self._intersect(A, B, prev_center, curr_center):
                    if vehicle.track_id not in self.crossed_ids:
                        self.crossed_ids.add(vehicle.track_id)
                        
                        # Determine direction: dy > 0 means moving downwards (incoming)
                        dy = curr_center[1] - prev_center[1]
                        if dy > 0:
                            self.incoming_count += 1
                        else:
                            self.outgoing_count += 1

                        self.seen_track_ids.add(vehicle.track_id)
                        self.class_counts[vehicle.label] += 1

    def _ccw(self, A: tuple[int, int], B: tuple[int, int], C: tuple[int, int]) -> bool:
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def _intersect(self, A: tuple[int, int], B: tuple[int, int], C: tuple[int, int], D: tuple[int, int]) -> bool:
        return self._ccw(A, C, D) != self._ccw(B, C, D) and self._ccw(A, B, C) != self._ccw(A, B, D)

    @property
    def total_unique(self) -> int:
        return len(self.seen_track_ids)

    def summary(self) -> dict[str, int]:
        return {
            "total_unique_vehicles": self.total_unique,
            "incoming_vehicles": self.incoming_count,
            "outgoing_vehicles": self.outgoing_count,
            **{f"{label}_count": count for label, count in sorted(self.class_counts.items())},
        }


