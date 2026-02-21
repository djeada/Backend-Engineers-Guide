"""
Bully algorithm leader election simulation.

Simulates a cluster of processes that elect a leader using the bully
algorithm.  When the current leader is removed the remaining processes
detect the failure and a new election round promotes the highest-ID
surviving process.

No external dependencies required.

Usage:
    python leader_election_example.py
"""


class Process:
    """A process that participates in bully-algorithm leader elections."""

    def __init__(self, pid: int):
        self.pid = pid
        self.alive = True
        self.leader: int | None = None

    def __repr__(self):
        state = "alive" if self.alive else "dead"
        return f"Process(pid={self.pid}, {state}, leader={self.leader})"


class Cluster:
    """A set of processes that can run bully-algorithm elections."""

    def __init__(self, pids: list[int]):
        self.processes = {pid: Process(pid) for pid in pids}

    def alive_processes(self) -> list[Process]:
        return sorted(
            (p for p in self.processes.values() if p.alive),
            key=lambda p: p.pid,
        )

    def kill(self, pid: int):
        self.processes[pid].alive = False

    def revive(self, pid: int):
        self.processes[pid].alive = True

    def elect(self, initiator_pid: int):
        """Run a bully election starting from *initiator_pid*."""
        print(f"\n  Process {initiator_pid} starts an election")
        higher = [p for p in self.alive_processes() if p.pid > initiator_pid]

        if higher:
            for p in higher:
                print(f"    -> {initiator_pid} sends ELECTION to {p.pid}")
            winner = max(higher, key=lambda p: p.pid)
            print(f"    <- {winner.pid} responds OK (highest)")
            self._set_leader(winner.pid)
        else:
            print(f"    No higher-ID process alive")
            self._set_leader(initiator_pid)

    def _set_leader(self, leader_pid: int):
        for p in self.alive_processes():
            p.leader = leader_pid
        print(f"  => Leader is now Process {leader_pid}")

    def status(self):
        for p in sorted(self.processes.values(), key=lambda p: p.pid):
            print(f"    {p}")


def main():
    print("=" * 60)
    print("Bully Algorithm Leader Election Demo")
    print("=" * 60)

    cluster = Cluster([1, 2, 3, 4, 5])

    print("\n--- Initial election (Process 1 notices no leader) ---")
    cluster.elect(initiator_pid=1)
    print("\n  Cluster state:")
    cluster.status()

    print("\n--- Process 5 (leader) crashes ---")
    cluster.kill(5)
    print("  Process 2 detects the failure and starts election")
    cluster.elect(initiator_pid=2)
    print("\n  Cluster state:")
    cluster.status()

    print("\n--- Process 4 also crashes ---")
    cluster.kill(4)
    cluster.elect(initiator_pid=1)
    print("\n  Cluster state:")
    cluster.status()

    print("\n--- Process 5 recovers and starts election ---")
    cluster.revive(5)
    cluster.elect(initiator_pid=5)
    print("\n  Cluster state:")
    cluster.status()

    print("\nKey takeaway: the bully algorithm always elects the highest-ID")
    print("alive process; when a failed leader recovers it can reclaim")
    print("leadership immediately.")


if __name__ == "__main__":
    main()
