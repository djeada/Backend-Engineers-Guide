"""
Sliding-window stream processing pipeline.

Simulates a real-time event stream with tumbling and sliding window
aggregations.  Events arrive with timestamps and the pipeline computes
windowed counts, sums, and averages — common patterns in metrics and
log processing backends.

No external dependencies required.

Usage:
    python stream_processing_example.py
"""

from collections import deque


class Event:
    def __init__(self, timestamp: float, key: str, value: float):
        self.timestamp = timestamp
        self.key = key
        self.value = value

    def __repr__(self):
        return f"Event(t={self.timestamp:.1f}, {self.key}={self.value})"


class TumblingWindow:
    """Fixed-size, non-overlapping time windows."""

    def __init__(self, size: float):
        self.size = size
        self.buckets: dict[int, list[Event]] = {}

    def add(self, event: Event):
        bucket_id = int(event.timestamp // self.size)
        self.buckets.setdefault(bucket_id, []).append(event)

    def results(self):
        for bucket_id in sorted(self.buckets):
            events = self.buckets[bucket_id]
            start = bucket_id * self.size
            end = start + self.size
            total = sum(e.value for e in events)
            avg = total / len(events) if events else 0
            yield {
                "window": f"[{start:.0f}, {end:.0f})",
                "count": len(events),
                "sum": total,
                "avg": round(avg, 2),
            }


class SlidingWindow:
    """Time-based sliding window that evicts expired events."""

    def __init__(self, duration: float):
        self.duration = duration
        self.events: deque[Event] = deque()

    def add(self, event: Event):
        self.events.append(event)
        self._evict(event.timestamp)

    def _evict(self, now: float):
        while self.events and self.events[0].timestamp < now - self.duration:
            self.events.popleft()

    def snapshot(self, now: float):
        self._evict(now)
        values = [e.value for e in self.events]
        total = sum(values)
        return {
            "window": f"({now - self.duration:.0f}, {now:.0f}]",
            "count": len(values),
            "sum": total,
            "avg": round(total / len(values), 2) if values else 0,
        }


class Pipeline:
    """A simple chain of transform stages applied to each event."""

    def __init__(self):
        self.stages: list = []

    def add_stage(self, name: str, fn):
        self.stages.append((name, fn))

    def process(self, event: Event) -> Event | None:
        current = event
        for name, fn in self.stages:
            current = fn(current)
            if current is None:
                return None
        return current


def main():
    print("=" * 60)
    print("Stream Processing Pipeline Demo")
    print("=" * 60)
    print()

    raw_events = [
        Event(1.0,  "cpu", 45.2),
        Event(2.5,  "cpu", 62.8),
        Event(3.0,  "cpu", 58.1),
        Event(4.2,  "mem", 71.0),
        Event(5.0,  "cpu", 90.5),
        Event(6.1,  "cpu", 32.0),
        Event(7.5,  "mem", 65.3),
        Event(8.0,  "cpu", 78.4),
        Event(9.3,  "cpu", 55.9),
        Event(10.0, "cpu", 88.2),
        Event(11.5, "mem", 40.1),
        Event(12.0, "cpu", 95.7),
    ]

    # Build pipeline: filter to CPU events and flag high values
    pipeline = Pipeline()
    pipeline.add_stage("filter_cpu", lambda e: e if e.key == "cpu" else None)

    def flag_high(e):
        if e.value > 80:
            print(f"    ALERT: high {e.key} = {e.value} at t={e.timestamp}")
        return e
    pipeline.add_stage("alert_high", flag_high)

    print("--- Pipeline processing (CPU events only, alert >80) ---")
    cpu_events = []
    for ev in raw_events:
        result = pipeline.process(ev)
        if result:
            cpu_events.append(result)
    print(f"  Passed pipeline: {len(cpu_events)} / {len(raw_events)} events\n")

    # Tumbling windows
    print("--- Tumbling windows (size=5s) ---")
    tw = TumblingWindow(size=5.0)
    for ev in cpu_events:
        tw.add(ev)
    for w in tw.results():
        print(f"  {w['window']}  count={w['count']}  sum={w['sum']:.1f}  avg={w['avg']}")
    print()

    # Sliding window snapshots
    print("--- Sliding window (duration=4s) snapshots ---")
    sw = SlidingWindow(duration=4.0)
    snapshot_times = [4.0, 6.0, 8.0, 10.0, 12.0]
    event_iter = iter(cpu_events)
    next_event = next(event_iter, None)

    for snap_time in snapshot_times:
        while next_event and next_event.timestamp <= snap_time:
            sw.add(next_event)
            next_event = next(event_iter, None)
        s = sw.snapshot(snap_time)
        print(f"  t={snap_time:5.1f}  {s['window']}  count={s['count']}  avg={s['avg']}")
    print()

    print("Key takeaway: stream processing applies filters, transforms, and")
    print("windowed aggregations to unbounded event streams in near-real-time.")


if __name__ == "__main__":
    main()
