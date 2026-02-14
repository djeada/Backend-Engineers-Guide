"""
Batch processing pipeline demonstration.

Simulates a data pipeline that reads records in configurable batches,
applies transformations (filter, map, aggregate), and writes results.
Shows how batch processing handles large data sets efficiently compared
to record-by-record processing.

No external dependencies required.

Usage:
    python batch_processing_example.py
"""

import random
import time


# ---------- Data generation ----------

def generate_records(n: int):
    """Generate synthetic sales transaction records."""
    categories = ["Electronics", "Books", "Clothing", "Food", "Toys"]
    regions = ["North", "South", "East", "West"]
    random.seed(42)
    return [
        {
            "id": i,
            "category": random.choice(categories),
            "region": random.choice(regions),
            "amount": round(random.uniform(5.0, 500.0), 2),
            "quantity": random.randint(1, 20),
            "returned": random.random() < 0.1,
        }
        for i in range(1, n + 1)
    ]


# ---------- Pipeline stages ----------

def stage_filter(batch, predicate):
    """Filter stage: keep only records matching a predicate."""
    return [r for r in batch if predicate(r)]


def stage_map(batch, transform):
    """Map stage: apply a transformation to each record."""
    return [transform(r) for r in batch]


def stage_aggregate(accumulator, batch, key_fn, value_fn):
    """Aggregate stage: accumulate values grouped by a key."""
    for record in batch:
        key = key_fn(record)
        accumulator[key] = accumulator.get(key, 0.0) + value_fn(record)
    return accumulator


# ---------- Batch iterator ----------

def iter_batches(records, batch_size):
    """Yield successive batches from a list of records."""
    for start in range(0, len(records), batch_size):
        yield records[start : start + batch_size]


# ---------- Pipeline runner ----------

def run_pipeline(records, batch_size):
    """Run the full batch-processing pipeline and return aggregated results."""
    aggregated = {}
    total_input = 0
    total_after_filter = 0
    total_after_map = 0
    batches_processed = 0

    for batch in iter_batches(records, batch_size):
        total_input += len(batch)

        # Stage 1 – Filter out returned items
        batch = stage_filter(batch, lambda r: not r["returned"])
        total_after_filter += len(batch)

        # Stage 2 – Compute revenue per record
        batch = stage_map(
            batch,
            lambda r: {**r, "revenue": round(r["amount"] * r["quantity"], 2)},
        )
        total_after_map += len(batch)

        # Stage 3 – Aggregate revenue by category
        aggregated = stage_aggregate(
            aggregated, batch, lambda r: r["category"], lambda r: r["revenue"]
        )

        batches_processed += 1

    return {
        "aggregated": aggregated,
        "batches_processed": batches_processed,
        "total_input": total_input,
        "total_after_filter": total_after_filter,
        "total_after_map": total_after_map,
    }


# ---------- Main ----------

def main():
    total_records = 10_000

    print("=" * 60)
    print("Batch Processing Pipeline Demo")
    print("=" * 60)
    print()
    print(f"Generating {total_records:,} synthetic sales records ...")
    records = generate_records(total_records)
    print(f"Sample record: {records[0]}")
    print()

    # --- Run with different batch sizes ---
    for batch_size in [100, 500, 2000]:
        print("-" * 60)
        print(f"Running pipeline with batch_size = {batch_size}")
        print("-" * 60)

        start = time.perf_counter()
        stats = run_pipeline(records, batch_size)
        elapsed = time.perf_counter() - start

        print(f"  Batches processed : {stats['batches_processed']}")
        print(f"  Records in        : {stats['total_input']:,}")
        print(f"  After filter stage: {stats['total_after_filter']:,}  "
              f"(removed {stats['total_input'] - stats['total_after_filter']:,} returned items)")
        print(f"  After map stage   : {stats['total_after_map']:,}")
        print(f"  Time elapsed      : {elapsed:.4f}s")
        print()

        print("  Revenue by category:")
        for category, revenue in sorted(stats["aggregated"].items()):
            print(f"    {category:<15} ${revenue:>12,.2f}")
        print()

    # --- Show why batching matters ---
    print("=" * 60)
    print("Why batch processing?")
    print("=" * 60)
    print()
    print("  1. Memory efficiency : Only one batch is in memory at a time,")
    print("     allowing processing of datasets larger than available RAM.")
    print()
    print("  2. Throughput        : Amortises per-record overhead across a")
    print("     batch (I/O syscalls, network round-trips, serialization).")
    print()
    print("  3. Back-pressure     : Batch sizes provide a natural throttle,")
    print("     preventing downstream systems from being overwhelmed.")
    print()
    print("Key takeaway: Batch processing pipelines break large workloads into")
    print("manageable chunks, enabling efficient, scalable data transformations.")


if __name__ == "__main__":
    main()
