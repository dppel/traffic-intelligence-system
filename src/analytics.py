from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class FrameAnalytics:
    frame_index: int
    timestamp_seconds: float
    active_vehicles: int
    unique_vehicles: int
    incoming_vehicles: int
    outgoing_vehicles: int
    average_speed_pixels_per_frame: float
    congestion_score: float
    congestion_level: str


class TrafficAnalyticsRecorder:
    """Stores frame-level analytics and exports CSV/summary reports."""

    def __init__(self) -> None:
        self.frames: list[FrameAnalytics] = []

    def add_frame(self, analytics: FrameAnalytics) -> None:
        self.frames.append(analytics)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(frame) for frame in self.frames])

    def export_csv(self, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_csv(output_path, index=False)
        return output_path

    def summary(self) -> dict[str, float | int | str]:
        if not self.frames:
            return {
                "processed_frames": 0,
                "total_unique_vehicles": 0,
                "incoming_vehicles": 0,
                "outgoing_vehicles": 0,
                "average_active_vehicles": 0.0,
                "peak_active_vehicles": 0,
                "peak_congestion_score": 0.0,
                "dominant_congestion_level": "Unknown",
            }

        dataframe = self.to_dataframe()
        return {
            "processed_frames": int(len(dataframe)),
            "total_unique_vehicles": int(dataframe["unique_vehicles"].max()),
            "incoming_vehicles": int(dataframe["incoming_vehicles"].max()) if "incoming_vehicles" in dataframe else 0,
            "outgoing_vehicles": int(dataframe["outgoing_vehicles"].max()) if "outgoing_vehicles" in dataframe else 0,
            "average_active_vehicles": round(float(dataframe["active_vehicles"].mean()), 2),
            "peak_active_vehicles": int(dataframe["active_vehicles"].max()),
            "peak_congestion_score": round(float(dataframe["congestion_score"].max()), 2),
            "dominant_congestion_level": str(dataframe["congestion_level"].mode().iloc[0]),
        }

    def export_summary(self, output_path: str | Path, extra_summary: dict[str, int] | None = None) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary = self.summary()
        if extra_summary:
            summary.update(extra_summary)

        lines = ["Traffic Intelligence Phase 2 Report", ""]
        lines.extend(f"{key}: {value}" for key, value in summary.items())
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

