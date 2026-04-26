# Messaging Reliability Lab

This mini-project groups the data-processing demos into a lab on **event delivery**, **batch throughput**, **failure handling**, **ETL pipelines**, and **workflow orchestration**.

## What you will practice

1. How pub/sub decouples producers from consumers
2. How batching improves throughput for large workloads
3. How stream processing applies near-real-time transforms and windows
4. How dead-letter queues isolate poison messages
5. How ETL pipelines extract, clean, and load data incrementally
6. How a DAG-based orchestrator schedules tasks, handles failures, and supports backfill

## Quick start

Run all demos at once:

```bash
cd projects/messaging_reliability_lab
./run.sh
```

Or run individual demos from the repository root:

```bash
python scripts/data_processing/pub_sub_example.py
python scripts/data_processing/batch_processing_example.py
python scripts/data_processing/stream_processing_example.py
python scripts/data_processing/dead_letter_queue_example.py
python scripts/data_processing/etl_pipeline_example.py
python scripts/data_processing/workflow_orchestration_example.py
```

## Suggested walkthrough

### 1. Publish/subscribe fan-out

```bash
python scripts/data_processing/pub_sub_example.py
```

Focus on:

- how one published event reaches multiple subscribers
- why publishers do not need direct knowledge of consumers
- where topic-based routing fits in event-driven systems

Read next:

- [`scripts/data_processing/pub_sub_example.py`](../../scripts/data_processing/pub_sub_example.py)
- [`notes/06_data_processing/01_pub_sub_vs_queue.md`](../../notes/06_data_processing/01_pub_sub_vs_queue.md)

### 2. Batch processing

```bash
python scripts/data_processing/batch_processing_example.py
```

Focus on:

- how batch size affects throughput and overhead
- why batching helps with memory efficiency and back-pressure
- how multi-stage pipelines transform and aggregate records

Read next:

- [`scripts/data_processing/batch_processing_example.py`](../../scripts/data_processing/batch_processing_example.py)
- [`notes/06_data_processing/03_batch_processing.md`](../../notes/06_data_processing/03_batch_processing.md)

### 3. Stream processing

```bash
python scripts/data_processing/stream_processing_example.py
```

Focus on:

- how tumbling and sliding windows summarize event streams
- why streaming systems attach timestamps to events
- how alert-style logic can be layered into a processing pipeline

Read next:

- [`scripts/data_processing/stream_processing_example.py`](../../scripts/data_processing/stream_processing_example.py)
- [`notes/06_data_processing/04_stream_processing.md`](../../notes/06_data_processing/04_stream_processing.md)

### 4. Dead-letter queues

```bash
python scripts/data_processing/dead_letter_queue_example.py
```

Focus on:

- why retries should have a limit
- how poison jobs are removed from the hot path
- what operators can inspect after a job lands in the DLQ

Read next:

- [`scripts/data_processing/dead_letter_queue_example.py`](../../scripts/data_processing/dead_letter_queue_example.py)

### 5. ETL pipeline

```bash
python scripts/data_processing/etl_pipeline_example.py
```

Focus on:

- how incremental extraction with a watermark avoids full re-reads
- how the transform stage cleans messy data and routes invalid records to a quarantine table
- why upsert (merge) semantics make the load phase idempotent and safe to retry

Read next:

- [`scripts/data_processing/etl_pipeline_example.py`](../../scripts/data_processing/etl_pipeline_example.py)
- [`notes/06_data_processing/05_etl_and_pipelines.md`](../../notes/06_data_processing/05_etl_and_pipelines.md)

### 6. Workflow orchestration

```bash
python scripts/data_processing/workflow_orchestration_example.py
```

Focus on:

- how a DAG's topological sort determines the execution order
- how independent tasks are grouped into parallel waves
- how failures propagate to downstream tasks and prevent partial results
- how exponential backoff limits the blast radius of transient errors
- how backfill runs re-process historical date partitions

Read next:

- [`scripts/data_processing/workflow_orchestration_example.py`](../../scripts/data_processing/workflow_orchestration_example.py)
- [`notes/06_data_processing/07_workflow_orchestration.md`](../../notes/06_data_processing/07_workflow_orchestration.md)

## Extension ideas

- Add exponential backoff to the DLQ retry loop
- Track per-topic lag or throughput in the pub/sub demo
- Compare tumbling and sliding windows on the same stream with different sizes
- Extend the ETL pipeline to write a schema-validation report alongside the quarantine table
- Add a sensor task to the orchestration demo that blocks execution until a mock API becomes available
