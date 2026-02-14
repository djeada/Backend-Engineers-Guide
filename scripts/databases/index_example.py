"""
SQLite index performance demonstration.

Creates an in-memory SQLite database, inserts a large number of rows,
then benchmarks SELECT queries with and without indexes.  Uses
EXPLAIN QUERY PLAN to show how SQLite chooses a full table scan vs. an
index lookup.

No external dependencies required.

Usage:
    python index_example.py
"""

import random
import sqlite3
import string
import time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROW_COUNT = 100_000
QUERY_RUNS = 50


def random_name(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email(name):
    domains = ["example.com", "test.org", "demo.net"]
    return f"{name}@{random.choice(domains)}"


def benchmark(cur, sql, params, runs=QUERY_RUNS):
    """Run a query multiple times and return average elapsed seconds."""
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        cur.execute(sql, params)
        _ = cur.fetchall()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return sum(times) / len(times)


def explain(cur, sql, params):
    """Return the EXPLAIN QUERY PLAN output as a readable string."""
    cur.execute(f"EXPLAIN QUERY PLAN {sql}", params)
    rows = cur.fetchall()
    return "\n".join(f"    {r[-1]}" for r in rows)


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def create_and_populate(cur):
    print("=" * 60)
    print("Setting Up the Database")
    print("=" * 60)

    cur.execute("""
        CREATE TABLE users (
            id    INTEGER PRIMARY KEY,
            name  TEXT NOT NULL,
            email TEXT NOT NULL,
            age   INTEGER NOT NULL
        )
    """)

    print(f"  Inserting {ROW_COUNT:,} rows …", end=" ", flush=True)
    start = time.perf_counter()
    rows = []
    for i in range(ROW_COUNT):
        name = random_name()
        rows.append((i, name, random_email(name), random.randint(18, 80)))
    cur.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", rows)
    elapsed = time.perf_counter() - start
    print(f"done in {elapsed:.2f}s")
    print()


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def demo_without_index(cur):
    print("=" * 60)
    print("1) Query WITHOUT Index  (full table scan)")
    print("=" * 60)

    sql = "SELECT * FROM users WHERE age = ?"
    params = (30,)

    plan = explain(cur, sql, params)
    print(f"  EXPLAIN QUERY PLAN:\n{plan}")

    avg = benchmark(cur, sql, params)
    print(f"  Avg query time ({QUERY_RUNS} runs): {avg*1000:.3f} ms")
    print()
    return avg


def demo_with_index(cur):
    print("=" * 60)
    print("2) Query WITH Index  (index lookup)")
    print("=" * 60)

    print("  Creating index on 'age' column …")
    start = time.perf_counter()
    cur.execute("CREATE INDEX idx_users_age ON users(age)")
    elapsed = time.perf_counter() - start
    print(f"  Index created in {elapsed*1000:.1f} ms")

    sql = "SELECT * FROM users WHERE age = ?"
    params = (30,)

    plan = explain(cur, sql, params)
    print(f"  EXPLAIN QUERY PLAN:\n{plan}")

    avg = benchmark(cur, sql, params)
    print(f"  Avg query time ({QUERY_RUNS} runs): {avg*1000:.3f} ms")
    print()
    return avg


def demo_composite_index(cur):
    print("=" * 60)
    print("3) Composite Index  (age + name)")
    print("=" * 60)

    cur.execute("CREATE INDEX idx_users_age_name ON users(age, name)")
    sql = "SELECT * FROM users WHERE age = ? AND name = ?"
    params = (30, "abcdefgh")

    plan = explain(cur, sql, params)
    print(f"  EXPLAIN QUERY PLAN:\n{plan}")

    avg = benchmark(cur, sql, params)
    print(f"  Avg query time ({QUERY_RUNS} runs): {avg*1000:.3f} ms")
    print()


def demo_covering_index(cur):
    print("=" * 60)
    print("4) Covering Index  (index-only scan)")
    print("=" * 60)

    print("  A covering index includes all columns the query needs,")
    print("  so SQLite never has to look up the actual table row.\n")

    cur.execute("CREATE INDEX idx_cover ON users(age, email)")
    sql = "SELECT email FROM users WHERE age = ?"
    params = (25,)

    plan = explain(cur, sql, params)
    print(f"  EXPLAIN QUERY PLAN:\n{plan}")

    avg = benchmark(cur, sql, params)
    print(f"  Avg query time ({QUERY_RUNS} runs): {avg*1000:.3f} ms")
    print()


def main():
    random.seed(42)
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    create_and_populate(cur)

    avg_no_idx = demo_without_index(cur)
    avg_with_idx = demo_with_index(cur)
    demo_composite_index(cur)
    demo_covering_index(cur)

    if avg_no_idx > 0:
        speedup = avg_no_idx / avg_with_idx if avg_with_idx > 0 else float("inf")
        print(f"Single-column index speedup: ~{speedup:.1f}x faster")
        print()

    conn.close()

    print("Key takeaway: Indexes trade extra storage and write overhead for")
    print("dramatically faster reads by letting the database jump directly to")
    print("matching rows instead of scanning the entire table.")


if __name__ == "__main__":
    main()
