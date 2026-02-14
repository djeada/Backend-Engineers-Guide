"""
Circuit breaker demonstration for flaky remote calls.

Shows CLOSED -> OPEN -> HALF_OPEN transitions to protect a backend from
repeated failures of a downstream dependency.

Usage:
    python circuit_breaker_example.py
"""

import time


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 1.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"
        self.opened_at = None

    def allow(self) -> bool:
        if self.state == "OPEN":
            if time.monotonic() - self.opened_at >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            self.opened_at = time.monotonic()


def main():
    breaker = CircuitBreaker()
    outcomes = [False, False, False, True, True]

    for i, ok in enumerate(outcomes, start=1):
        if not breaker.allow():
            print(f"request {i}: blocked (state={breaker.state})")
            time.sleep(1.1)
            continue

        if ok:
            breaker.record_success()
            print(f"request {i}: success (state={breaker.state})")
        else:
            breaker.record_failure()
            print(f"request {i}: failure (state={breaker.state})")

    print("Key takeaway: circuit breakers fail fast during outages.")


if __name__ == "__main__":
    main()
