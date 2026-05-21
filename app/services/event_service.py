import pandas as pd

from app.schemas.analytics_schema import TrafficEvent


class EventDetectionService:
    """Detects dashboard-ready traffic events from frame-level metrics."""

    def detect_events(self, dataframe: pd.DataFrame) -> list[TrafficEvent]:
        events: list[TrafficEvent] = []
        if dataframe.empty:
            return events

        events.extend(self._detect_high_congestion(dataframe))
        events.extend(self._detect_traffic_spikes(dataframe))
        events.extend(self._detect_abnormal_density(dataframe))
        return sorted(events, key=lambda event: event.timestamp_seconds)

    def _detect_high_congestion(self, dataframe: pd.DataFrame) -> list[TrafficEvent]:
        high_rows = dataframe[dataframe["congestion_score"] >= 65.0]
        return [
            TrafficEvent(
                event_type="high_congestion",
                timestamp_seconds=float(row.timestamp_seconds),
                frame_index=int(row.frame_index),
                severity="high",
                summary=f"High congestion detected with score {float(row.congestion_score):.1f}.",
                value=float(row.congestion_score),
            )
            for row in high_rows.itertuples(index=False)
        ]

    def _detect_traffic_spikes(self, dataframe: pd.DataFrame) -> list[TrafficEvent]:
        if len(dataframe) < 2:
            return []

        active_diff = dataframe["active_vehicles"].diff().fillna(0)
        spike_rows = dataframe[active_diff >= 3]
        return [
            TrafficEvent(
                event_type="traffic_spike",
                timestamp_seconds=float(row.timestamp_seconds),
                frame_index=int(row.frame_index),
                severity="medium",
                summary=f"Traffic spike detected: active vehicles increased to {int(row.active_vehicles)}.",
                value=float(row.active_vehicles),
            )
            for row in spike_rows.itertuples(index=False)
        ]

    def _detect_abnormal_density(self, dataframe: pd.DataFrame) -> list[TrafficEvent]:
        mean_density = float(dataframe["active_vehicles"].mean())
        std_density = float(dataframe["active_vehicles"].std() or 0.0)
        threshold = mean_density + (2.0 * std_density)

        if threshold <= 0:
            return []

        dense_rows = dataframe[dataframe["active_vehicles"] > threshold]
        return [
            TrafficEvent(
                event_type="abnormal_density",
                timestamp_seconds=float(row.timestamp_seconds),
                frame_index=int(row.frame_index),
                severity="medium",
                summary=f"Abnormal density detected with {int(row.active_vehicles)} active vehicles.",
                value=float(row.active_vehicles),
            )
            for row in dense_rows.itertuples(index=False)
        ]

