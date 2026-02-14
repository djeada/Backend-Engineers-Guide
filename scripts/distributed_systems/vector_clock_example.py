"""
Vector clock implementation for causality tracking.

Implements vector clocks for a set of distributed processes, shows how
local events, message sends, and message receives update the clocks,
and demonstrates how vector clocks detect concurrent vs causally-ordered
events.

No external dependencies required.

Usage:
    python vector_clock_example.py
"""


# ---------- Vector clock ----------

class VectorClock:
    """A vector clock for a set of known process IDs."""

    def __init__(self, process_ids):
        self.clock = {pid: 0 for pid in process_ids}

    def copy(self):
        vc = VectorClock([])
        vc.clock = dict(self.clock)
        return vc

    def increment(self, process_id: str):
        """Tick the clock for a local event on *process_id*."""
        self.clock[process_id] += 1

    def merge(self, other: "VectorClock"):
        """Merge another vector clock (element-wise max)."""
        for pid in self.clock:
            self.clock[pid] = max(self.clock[pid], other.clock.get(pid, 0))

    def __le__(self, other: "VectorClock") -> bool:
        """True if self is causally ≤ other (happened-before or equal)."""
        return all(self.clock[pid] <= other.clock.get(pid, 0) for pid in self.clock)

    def __lt__(self, other: "VectorClock") -> bool:
        """True if self happened strictly before other."""
        return self <= other and self.clock != other.clock

    def __eq__(self, other: "VectorClock") -> bool:
        return self.clock == other.clock

    def __repr__(self):
        entries = ", ".join(f"{pid}:{v}" for pid, v in sorted(self.clock.items()))
        return f"<{entries}>"


# ---------- Process model ----------

class Process:
    """A simulated distributed process with a vector clock."""

    def __init__(self, pid: str, all_pids):
        self.pid = pid
        self.clock = VectorClock(all_pids)
        self.log = []

    def local_event(self, description: str):
        """Record a local event."""
        self.clock.increment(self.pid)
        snap = self.clock.copy()
        self.log.append((description, snap))
        print(f"  {self.pid}: local   '{description}'  =>  {snap}")
        return snap

    def send(self, description: str):
        """Record a send event and return the clock snapshot to attach."""
        self.clock.increment(self.pid)
        snap = self.clock.copy()
        self.log.append((f"send: {description}", snap))
        print(f"  {self.pid}: send    '{description}'  =>  {snap}")
        return snap

    def receive(self, description: str, sender_clock: VectorClock):
        """Record a receive event, merging the sender's clock."""
        self.clock.increment(self.pid)
        self.clock.merge(sender_clock)
        snap = self.clock.copy()
        self.log.append((f"recv: {description}", snap))
        print(f"  {self.pid}: receive '{description}'  =>  {snap}")
        return snap


# ---------- Causality comparison ----------

def compare_events(label_a: str, vc_a: VectorClock,
                   label_b: str, vc_b: VectorClock):
    """Print the causal relationship between two events."""
    if vc_a < vc_b:
        rel = f"'{label_a}' → '{label_b}'  (A happened before B)"
    elif vc_b < vc_a:
        rel = f"'{label_b}' → '{label_a}'  (B happened before A)"
    elif vc_a == vc_b:
        rel = "identical clocks (same event)"
    else:
        rel = f"'{label_a}' ∥ '{label_b}'  (concurrent — no causal order)"
    print(f"  {rel}")


# ---------- Main ----------

def main():
    pids = ["A", "B", "C"]

    print("=" * 62)
    print("Vector Clock Causality Tracking Demo")
    print("=" * 62)
    print()
    print(f"Processes: {pids}")
    print(f"Initial clocks: all zeros")
    print()

    # Create processes
    procs = {pid: Process(pid, pids) for pid in pids}
    A, B, C = procs["A"], procs["B"], procs["C"]

    # --- Scenario ---
    print("-" * 62)
    print("Event sequence")
    print("-" * 62)
    print()

    e1 = A.local_event("compute X")
    msg1 = A.send("msg1 to B")
    e2 = B.local_event("compute Y")
    e3 = B.receive("msg1 from A", msg1)
    e4 = C.local_event("compute Z")
    msg2 = B.send("msg2 to C")
    e5 = C.receive("msg2 from B", msg2)
    e6 = A.local_event("compute W")
    msg3 = C.send("msg3 to A")
    e7 = A.receive("msg3 from C", msg3)
    print()

    # --- Causality analysis ---
    print("-" * 62)
    print("Causality analysis")
    print("-" * 62)
    print()

    print("a) A's 'compute X' vs B's receive of msg1:")
    compare_events("compute X", e1, "recv msg1", e3)
    print()

    print("b) C's 'compute Z' vs B's 'compute Y':")
    compare_events("compute Z", e4, "compute Y", e2)
    print()

    print("c) A's 'compute X' vs C's receive of msg2:")
    compare_events("compute X", e1, "recv msg2", e5)
    print()

    print("d) A's 'compute W' vs C's 'compute Z':")
    compare_events("compute W", e6, "compute Z", e4)
    print()

    print("e) A's receive of msg3 vs C's send of msg3:")
    compare_events("send msg3", msg3, "recv msg3", e7)
    print()

    # --- Final clock states ---
    print("-" * 62)
    print("Final vector clock states")
    print("-" * 62)
    print()
    for pid in pids:
        print(f"  Process {pid}: {procs[pid].clock}")
    print()

    print("Key takeaway: Vector clocks track causality across distributed")
    print("processes — if one clock is element-wise ≤ another the events are")
    print("causally ordered; otherwise they are concurrent.")


if __name__ == "__main__":
    main()
