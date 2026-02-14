"""
Dead-letter queue (DLQ) flow demonstration.

Retries failed jobs a fixed number of times, then sends persistent failures to
a dead-letter queue for later inspection.

Usage:
    python dead_letter_queue_example.py
"""

from collections import deque


def main():
    queue = deque([
        {"id": "job-1", "attempts": 0, "should_fail": False},
        {"id": "job-2", "attempts": 0, "should_fail": True},
    ])
    dlq = []
    max_attempts = 3

    while queue:
        job = queue.popleft()
        job["attempts"] += 1
        if job["should_fail"]:
            if job["attempts"] >= max_attempts:
                dlq.append(job)
                print(f"{job['id']} -> moved to DLQ")
            else:
                queue.append(job)
                print(f"{job['id']} -> retry {job['attempts']}")
        else:
            print(f"{job['id']} -> processed")

    print("DLQ contents:", [j["id"] for j in dlq])
    print("Key takeaway: DLQ isolates poison messages from main processing.")


if __name__ == "__main__":
    main()
