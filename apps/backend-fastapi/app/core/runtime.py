from __future__ import annotations

from collections import deque
from statistics import mean


class RuntimeMetrics:
    def __init__(self, max_samples: int = 200) -> None:
        self._durations = deque(maxlen=max_samples)
        self._queue_waits = deque(maxlen=max_samples)

    def record(self, duration_ms: float, queue_wait_ms: float) -> None:
        self._durations.append(duration_ms)
        self._queue_waits.append(queue_wait_ms)

    def snapshot(self) -> dict[str, float | int]:
        durations = list(self._durations)
        waits = list(self._queue_waits)
        if not durations:
            return {
                "avg_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "p95_duration_ms": 0.0,
                "avg_queue_wait_ms": 0.0,
                "sample_size": 0,
            }
        sorted_durations = sorted(durations)
        p95_index = min(len(sorted_durations) - 1, max(0, int(len(sorted_durations) * 0.95) - 1))
        return {
            "avg_duration_ms": round(mean(durations), 2),
            "max_duration_ms": round(max(durations), 2),
            "p95_duration_ms": round(sorted_durations[p95_index], 2),
            "avg_queue_wait_ms": round(mean(waits) if waits else 0.0, 2),
            "sample_size": len(durations),
        }


runtime_metrics = RuntimeMetrics()
