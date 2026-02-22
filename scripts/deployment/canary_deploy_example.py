"""
Canary deployment traffic shifting simulation.

Simulates a canary rollout where traffic is gradually shifted from the
old version (v1) to the new version (v2).  At each step the canary's
error rate is evaluated; if it exceeds a threshold the rollout is
automatically rolled back.

No external dependencies required.

Usage:
    python canary_deploy_example.py
"""

import random


class Backend:
    def __init__(self, name: str, error_rate: float = 0.0):
        self.name = name
        self.error_rate = error_rate
        self.requests = 0
        self.errors = 0

    def handle(self) -> bool:
        self.requests += 1
        if random.random() < self.error_rate:
            self.errors += 1
            return False
        return True

    def observed_error_rate(self) -> float:
        return self.errors / self.requests if self.requests else 0.0

    def __repr__(self):
        return (f"{self.name}: {self.requests} reqs, "
                f"{self.errors} errs ({self.observed_error_rate()*100:.1f}%)")


def simulate_traffic(v1: Backend, v2: Backend, canary_pct: float, count: int):
    """Route *count* requests with *canary_pct* going to v2."""
    for _ in range(count):
        if random.random() < canary_pct:
            v2.handle()
        else:
            v1.handle()


def main():
    random.seed(42)

    print("=" * 60)
    print("Canary Deployment Simulation")
    print("=" * 60)
    print()

    error_threshold = 0.05
    requests_per_step = 200

    print("Scenario 1: Successful canary rollout (v2 is healthy)")
    print("-" * 60)
    v1 = Backend("v1-stable", error_rate=0.01)
    v2 = Backend("v2-canary", error_rate=0.02)

    stages = [0.05, 0.10, 0.25, 0.50, 1.00]
    for pct in stages:
        simulate_traffic(v1, v2, pct, requests_per_step)
        err = v2.observed_error_rate()
        status = "OK" if err < error_threshold else "ROLLBACK"
        print(f"  canary={pct*100:5.1f}%  | {v1} | {v2} | {status}")
        if status == "ROLLBACK":
            print("  => Rolling back to v1!")
            break
    else:
        print("  => Canary promoted to 100% — rollout complete!")
    print()

    print("Scenario 2: Canary has elevated errors -> automatic rollback")
    print("-" * 60)
    v1 = Backend("v1-stable", error_rate=0.01)
    v2_bad = Backend("v2-buggy", error_rate=0.15)

    for pct in stages:
        simulate_traffic(v1, v2_bad, pct, requests_per_step)
        err = v2_bad.observed_error_rate()
        status = "OK" if err < error_threshold else "ROLLBACK"
        print(f"  canary={pct*100:5.1f}%  | {v1} | {v2_bad} | {status}")
        if status == "ROLLBACK":
            print("  => Error threshold exceeded — rolling back to v1!")
            break
    else:
        print("  => Canary promoted to 100% — rollout complete!")
    print()

    print("Key takeaway: canary deployments limit blast radius by gradually")
    print("shifting traffic and monitoring error rates, enabling automatic")
    print("rollback before users are widely affected.")


if __name__ == "__main__":
    main()
