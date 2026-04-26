"""
ETL pipeline demonstration.

Implements a small Extract-Transform-Load pipeline that:
  - Extracts synthetic sales records from an in-memory "source"
  - Transforms them (clean, enrich, validate, deduplicate)
  - Loads them into an in-memory "destination" using an upsert strategy

Also demonstrates incremental extraction via a watermark (last_seen_id).

No external dependencies required.

Usage:
    python etl_pipeline_example.py
"""

import random
import time
from copy import deepcopy


# ---------------------------------------------------------------------------
# Simulated source data
# ---------------------------------------------------------------------------

CATEGORIES = ["Electronics", "Books", "Clothing", "Food", "Toys"]
REGIONS = ["North", "South", "East", "West"]

def _make_record(record_id: int, seed: int) -> dict:
    rng = random.Random(seed)
    return {
        "id": record_id,
        "customer": f"customer_{record_id:04d}",
        "category": rng.choice(CATEGORIES),
        "region": rng.choice(REGIONS),
        # Intentionally messy: whitespace, wrong case, None values
        "amount": rng.choice([
            f" {round(rng.uniform(5.0, 500.0), 2)} ",  # leading/trailing spaces
            None,                                        # missing value
            str(round(rng.uniform(5.0, 500.0), 2)),     # valid as string
        ]),
        "currency": rng.choice(["USD", " usd ", "EUR", None]),
        "quantity": rng.randint(1, 20),
        "returned": rng.random() < 0.08,
    }


class SourceDatabase:
    """In-memory simulated source that supports incremental reads via a record_id watermark."""

    def __init__(self, total_records: int = 200):
        random.seed(0)
        self._records = [_make_record(i, seed=i * 7) for i in range(1, total_records + 1)]

    def read_incremental(self, after_id: int, limit: int = 50) -> list[dict]:
        """Return up to *limit* records with id > after_id."""
        return [deepcopy(r) for r in self._records if r["id"] > after_id][:limit]


# ---------------------------------------------------------------------------
# Extract phase
# ---------------------------------------------------------------------------

class Extractor:
    """Reads records from the source using an incremental watermark."""

    def __init__(self, source: SourceDatabase):
        self._source = source
        self._watermark = 0  # last successfully processed id

    def extract_batch(self, batch_size: int = 50) -> list[dict]:
        records = self._source.read_incremental(after_id=self._watermark, limit=batch_size)
        return records

    def advance_watermark(self, records: list[dict]) -> None:
        if records:
            self._watermark = max(r["id"] for r in records)

    @property
    def watermark(self) -> int:
        return self._watermark


# ---------------------------------------------------------------------------
# Transform phase
# ---------------------------------------------------------------------------

class TransformResult:
    def __init__(self):
        self.clean: list[dict] = []
        self.quarantined: list[dict] = []

    @property
    def clean_count(self) -> int:
        return len(self.clean)

    @property
    def quarantine_count(self) -> int:
        return len(self.quarantined)


def _clean_string(value) -> str | None:
    """Strip whitespace and normalise to lower-case."""
    if value is None:
        return None
    return str(value).strip().lower()


def _parse_amount(raw) -> float | None:
    """Parse amount from a potentially messy string."""
    if raw is None:
        return None
    try:
        return float(str(raw).strip())
    except ValueError:
        return None


def transform(records: list[dict]) -> TransformResult:
    """
    Apply a sequence of transformations:
      1. Parse and clean fields
      2. Apply defaults for missing values
      3. Validate required fields
      4. Enrich with a computed revenue field
      5. Filter out returned items
    """
    result = TransformResult()
    seen_ids: set[int] = set()

    for raw in records:
        record = deepcopy(raw)

        # --- Deduplication ---
        if record["id"] in seen_ids:
            continue
        seen_ids.add(record["id"])

        # --- Parse and clean ---
        record["amount"] = _parse_amount(record.get("amount"))
        record["currency"] = _clean_string(record.get("currency")) or "usd"
        record["category"] = _clean_string(record.get("category")) or "unknown"
        record["region"] = _clean_string(record.get("region")) or "unknown"

        # --- Validate required fields ---
        if record["amount"] is None or record["amount"] <= 0:
            record["_quarantine_reason"] = "invalid_amount"
            result.quarantined.append(record)
            continue

        if record.get("customer") is None:
            record["_quarantine_reason"] = "missing_customer"
            result.quarantined.append(record)
            continue

        # --- Filter returned items ---
        if record.get("returned"):
            record["_quarantine_reason"] = "returned_item"
            result.quarantined.append(record)
            continue

        # --- Enrich ---
        record["revenue"] = round(record["amount"] * record.get("quantity", 1), 2)
        record.pop("returned", None)

        result.clean.append(record)

    return result


# ---------------------------------------------------------------------------
# Load phase (in-memory destination with upsert semantics)
# ---------------------------------------------------------------------------

class DestinationStore:
    """In-memory store that supports upsert by primary key."""

    def __init__(self):
        self._rows: dict[int, dict] = {}
        self.inserts = 0
        self.updates = 0

    def upsert(self, records: list[dict]) -> None:
        for record in records:
            key = record["id"]
            if key in self._rows:
                self._rows[key] = record
                self.updates += 1
            else:
                self._rows[key] = record
                self.inserts += 1

    @property
    def row_count(self) -> int:
        return len(self._rows)

    def aggregate_revenue_by_category(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for row in self._rows.values():
            cat = row.get("category", "unknown")
            totals[cat] = round(totals.get(cat, 0.0) + row.get("revenue", 0.0), 2)
        return totals


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_full_etl(batch_size: int = 50) -> None:
    source = SourceDatabase(total_records=200)
    extractor = Extractor(source)
    destination = DestinationStore()

    total_extracted = 0
    total_clean = 0
    total_quarantined = 0
    batch_num = 0

    print("-" * 60)
    print(f"Starting ETL pipeline  (batch_size={batch_size})")
    print("-" * 60)

    while True:
        # --- Extract ---
        raw_records = extractor.extract_batch(batch_size=batch_size)
        if not raw_records:
            break

        batch_num += 1
        total_extracted += len(raw_records)

        # --- Transform ---
        result = transform(raw_records)
        total_clean += result.clean_count
        total_quarantined += result.quarantine_count

        # --- Load ---
        destination.upsert(result.clean)

        # --- Advance watermark after successful load ---
        extractor.advance_watermark(raw_records)

        print(
            f"  Batch {batch_num:02d} | "
            f"extracted={len(raw_records):3d}  "
            f"clean={result.clean_count:3d}  "
            f"quarantined={result.quarantine_count:3d}  "
            f"watermark={extractor.watermark}"
        )

    print()
    print("Pipeline complete")
    print(f"  Batches processed : {batch_num}")
    print(f"  Total extracted   : {total_extracted}")
    print(f"  Total clean loaded: {total_clean}")
    print(f"  Total quarantined : {total_quarantined}")
    print(f"  Destination rows  : {destination.row_count}")
    print(f"  Inserts           : {destination.inserts}")
    print(f"  Updates           : {destination.updates}")
    print()
    print("  Revenue by category:")
    for cat, rev in sorted(destination.aggregate_revenue_by_category().items()):
        print(f"    {cat:<15} ${rev:>10,.2f}")


# ---------------------------------------------------------------------------
# Idempotency demonstration
# ---------------------------------------------------------------------------

def demonstrate_idempotency() -> None:
    """Show that running the same batch twice produces the same destination state."""
    print()
    print("-" * 60)
    print("Idempotency demonstration")
    print("-" * 60)

    source = SourceDatabase(total_records=20)
    raw = source.read_incremental(after_id=0, limit=20)
    result = transform(raw)

    dest = DestinationStore()

    # Load once
    dest.upsert(result.clean)
    rows_after_first = dest.row_count

    # Load the same records again (simulates a retry)
    dest.upsert(result.clean)
    rows_after_second = dest.row_count

    print(f"  Rows after first load  : {rows_after_first}")
    print(f"  Rows after second load : {rows_after_second}  (same – upsert is idempotent)")
    assert rows_after_first == rows_after_second, "Idempotency violation!"
    print("  Assertion passed: upsert is idempotent ✓")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("ETL Pipeline Demo")
    print("=" * 60)
    print()
    print("Phase overview:")
    print("  Extract  – incremental read from source using a watermark")
    print("  Transform – clean, validate, deduplicate, enrich")
    print("  Load     – upsert into destination by primary key")
    print()

    start = time.perf_counter()
    run_full_etl(batch_size=40)
    elapsed = time.perf_counter() - start
    print(f"\n  Elapsed: {elapsed:.4f}s")

    demonstrate_idempotency()

    print()
    print("Key takeaways:")
    print("  1. Watermark-based extraction avoids reprocessing the full source every run.")
    print("  2. Transform stages clean messy data and quarantine unprocessable records.")
    print("  3. Upsert semantics in the load phase make the pipeline idempotent and")
    print("     safe to retry after failures.")


if __name__ == "__main__":
    main()
