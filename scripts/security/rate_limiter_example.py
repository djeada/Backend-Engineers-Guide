"""
Token-bucket rate limiter demonstration.

Shows how a backend can allow short bursts while enforcing a long-term request
rate per client.

Usage:
    python rate_limiter_example.py
"""

import time


class TokenBucket:
    def __init__(self, capacity: int, refill_per_second: float):
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()

    def allow(self, tokens: float = 1.0) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.last_refill = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


def main():
    bucket = TokenBucket(capacity=5, refill_per_second=2.0)

    print("Burst phase (10 quick requests):")
    for i in range(1, 11):
        allowed = bucket.allow()
        print(f"  request {i:02d}: {'allowed' if allowed else 'throttled'}")
        time.sleep(0.1)

    print("\nCooldown (1.5s), then 3 more requests:")
    time.sleep(1.5)
    for i in range(11, 14):
        allowed = bucket.allow()
        print(f"  request {i:02d}: {'allowed' if allowed else 'throttled'}")

    print("\nKey takeaway: token bucket enforces average rate with burst tolerance.")


if __name__ == "__main__":
    main()
