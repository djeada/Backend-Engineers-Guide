# Messaging Reliability Lab

This mini-project groups the data-processing demos into a lab on **event delivery**, **batch throughput**, and **failure handling**.

## What you will practice

1. How pub/sub decouples producers from consumers
2. How batching improves throughput for large workloads
3. How stream processing applies near-real-time transforms and windows
4. How dead-letter queues isolate poison messages

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

## Extension ideas

- Add exponential backoff to the DLQ retry loop
- Track per-topic lag or throughput in the pub/sub demo
- Compare tumbling and sliding windows on the same stream with different sizes
