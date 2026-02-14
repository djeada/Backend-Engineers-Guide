"""
Load balancer simulation.

Demonstrates common load-balancing strategies – round-robin, weighted
round-robin, and least-connections – that are used by reverse proxies
such as Nginx, HAProxy, and cloud load balancers.

No external dependencies required.

Usage:
    python load_balancer_example.py
"""

import random
import time
from dataclasses import dataclass, field


@dataclass
class Backend:
    """Represents an upstream server behind a load balancer."""

    name: str
    weight: int = 1
    active_connections: int = 0
    total_requests: int = 0


# ---------- Strategies ----------


class RoundRobin:
    """Distribute requests to backends in order, one after another."""

    def __init__(self, backends: list[Backend]):
        self.backends = backends
        self._index = 0

    def next_backend(self) -> Backend:
        backend = self.backends[self._index % len(self.backends)]
        self._index += 1
        return backend


class WeightedRoundRobin:
    """Like round-robin but backends with higher weight receive more traffic."""

    def __init__(self, backends: list[Backend]):
        self._expanded: list[Backend] = []
        for b in backends:
            self._expanded.extend([b] * b.weight)
        self._index = 0

    def next_backend(self) -> Backend:
        backend = self._expanded[self._index % len(self._expanded)]
        self._index += 1
        return backend


class LeastConnections:
    """Send each request to the backend with the fewest active connections."""

    def __init__(self, backends: list[Backend]):
        self.backends = backends

    def next_backend(self) -> Backend:
        return min(self.backends, key=lambda b: b.active_connections)


# ---------- Simulation helpers ----------


def simulate(strategy_name: str, strategy, backends: list[Backend], requests: int):
    """Run a batch of simulated requests through the given strategy."""
    print(f"--- {strategy_name} ---")
    for b in backends:
        b.active_connections = 0
        b.total_requests = 0

    random.seed(42)
    for _ in range(requests):
        backend = strategy.next_backend()
        backend.total_requests += 1
        backend.active_connections += 1
        # Simulate variable request duration by randomly completing the request
        if random.random() < 0.6:
            backend.active_connections = max(0, backend.active_connections - 1)

    for b in backends:
        print(f"  {b.name} (weight={b.weight}): {b.total_requests} requests")
    print()


# ---------- Main ----------


def main():
    print("=" * 55)
    print("Load Balancer Strategy Simulation")
    print("=" * 55)
    print()

    num_requests = 30

    # --- Round Robin ---
    backends = [Backend("server-A"), Backend("server-B"), Backend("server-C")]
    rr = RoundRobin(backends)
    simulate("Round Robin", rr, backends, num_requests)

    # --- Weighted Round Robin ---
    backends = [
        Backend("server-A", weight=3),
        Backend("server-B", weight=2),
        Backend("server-C", weight=1),
    ]
    wrr = WeightedRoundRobin(backends)
    simulate("Weighted Round Robin", wrr, backends, num_requests)

    # --- Least Connections ---
    backends = [Backend("server-A"), Backend("server-B"), Backend("server-C")]
    lc = LeastConnections(backends)
    simulate("Least Connections", lc, backends, num_requests)

    print("Key takeaway: Load balancers distribute traffic across backends;")
    print("the best strategy depends on workload characteristics and server capacity.")


if __name__ == "__main__":
    main()
