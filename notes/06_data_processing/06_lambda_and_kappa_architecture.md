## Lambda and Kappa Architecture

As data volumes grew and real-time analytics became a business requirement, engineers needed architectural patterns that could handle both **historical re-computation** and **low-latency stream processing** reliably. Lambda and Kappa architectures are the two dominant answers to that challenge.

### Lambda Architecture

Lambda architecture, popularised by Nathan Marz, splits processing into three independent layers that run simultaneously. The key insight is that **immutable raw data** stored in the batch layer is the single source of truth, while the speed layer only provides low-latency approximations that are eventually superseded by accurate batch results.

```
Lambda Architecture

  Incoming Data Stream
         |
         v
+--------+--------+
|                 |
|   Batch Layer   |  <-- immutable raw store (HDFS, S3, Delta Lake)
|                 |      recomputes full views periodically
+--------+--------+
         |
         v (batch views, hours to days old)
+--------+--------+
|                 |
|  Serving Layer  |  <-- merges batch view + speed view to answer queries
|                 |
+--------+--------+
         ^
         | (real-time view, seconds to minutes old)
+--------+--------+
|                 |
|   Speed Layer   |  <-- stream processor (Kafka + Flink / Spark Streaming)
|                 |      low-latency, eventually replaced by batch view
+-----------------+
```

#### Batch Layer

The batch layer stores all raw, immutable data and periodically runs large-scale compute jobs to produce **batch views** – pre-aggregated, correct, complete results.

- All incoming events are **appended** to the master dataset; nothing is ever updated or deleted.
- Batch jobs process the entire history from scratch to compute views, eliminating complex incremental update logic.
- Results are written to read-optimised storage (Parquet files, columnar tables) accessible by the serving layer.
- Technologies: **Apache Hadoop MapReduce**, **Apache Spark**, **Apache Hive**, **Presto/Trino**.

#### Speed Layer

The speed layer compensates for the high latency of batch jobs by processing new events in real time and producing **speed views** that cover the gap since the last batch run.

- Only the most **recent** data (since the last completed batch view) needs to be processed.
- Because accuracy is eventually guaranteed by the batch layer, the speed layer can use approximate or simplified algorithms.
- Speed views are **discarded** and replaced once a new batch view incorporating that period has been computed.
- Technologies: **Apache Kafka**, **Apache Flink**, **Apache Storm**, **Spark Streaming**.

#### Serving Layer

The serving layer merges batch views and speed views at query time, presenting a unified, consistent result to consumers.

- **Batch view** provides complete, accurate data up to the last batch run.
- **Speed view** provides approximate or partial data for events since the last batch run.
- A query joins or unions both views so consumers always see **up-to-date** results.
- Technologies: **Apache Druid**, **Apache HBase**, **Cassandra**, **Elasticsearch**, **Pinot**.

```
Query Answering in Lambda

  User Query
      |
      v
  Serving Layer
      |
      +--------> Batch View  (complete, accurate, covers T-0 to T-batch)
      |                 \
      +--------> Speed View  (recent, approximate, covers T-batch to now)
                         \
                    Merge & Return Result
```

#### Lambda Architecture Trade-offs

| Aspect               | Advantage                                          | Challenge                                           |
| -------------------- | -------------------------------------------------- | --------------------------------------------------- |
| **Accuracy**         | Batch layer guarantees correctness over full history | Speed layer may be approximate until batch catches up |
| **Latency**          | Speed layer provides low-latency real-time views   | Batch layer has high latency (hours to days)         |
| **Complexity**       | Clear separation of concerns                       | Two separate codebases for batch and streaming logic |
| **Re-processing**    | Trivial – recompute batch views from raw data      | Speed view state must be carefully managed           |
| **Fault tolerance**  | Immutable batch store simplifies recovery          | Speed layer state recovery can be complex            |

### Kappa Architecture

Kappa architecture, proposed by Jay Kreps (co-creator of Kafka), eliminates the batch layer entirely. The central thesis is that **a well-designed streaming system can replace batch processing** if the stream log is retained long enough to enable historical re-computation by replaying it from the beginning.

```
Kappa Architecture

  Incoming Data Stream
         |
         v
+--------+--------+
|                 |
|  Stream Log     |  <-- durable, replayable log (Apache Kafka, Kinesis)
|  (retained)     |      acts as the single source of truth
+--------+--------+
         |
         v
+--------+--------+
|                 |
| Stream Processor|  <-- single processing layer (Flink, Kafka Streams)
| (current code)  |      handles both real-time and historical replay
+--------+--------+
         |
         v
+--------+--------+
|                 |
|  Serving Store  |  <-- queryable output (Cassandra, Elasticsearch, etc.)
|                 |
+-----------------+
```

#### Re-processing in Kappa

When business logic changes or a bug must be corrected, Kappa handles re-processing by:

1. Deploying a new version of the stream processing job alongside the existing one.
2. Starting the new job from **offset 0** (the beginning of the retained log).
3. Writing the new job's output to a **new output table** while the old table remains live.
4. Performing an atomic **cutover** to the new output table once the new job has caught up.
5. Shutting down the old job and dropping the old output table.

```
Kappa Re-processing Cutover

  Log (all history retained)
       |
       +-----> Old Job (v1) -------> Output Table v1  (serving live traffic)
       |
       +-----> New Job (v2) -------> Output Table v2  (catching up from offset 0)
                                           |
                                    (when caught up)
                                           |
                                    Atomic swap: v2 becomes primary
                                           |
                                    Old job + v1 table decommissioned
```

#### Kappa Architecture Trade-offs

| Aspect               | Advantage                                          | Challenge                                           |
| -------------------- | -------------------------------------------------- | --------------------------------------------------- |
| **Simplicity**       | Single codebase for all processing                 | Streaming code can be harder to write than batch SQL |
| **Latency**          | Consistently low latency for all queries           | Log retention for full history can be expensive      |
| **Re-processing**    | Replay from any offset in the log                  | Re-processing large history takes significant time   |
| **Fault tolerance**  | Checkpointing and offset management                | Stateful stream operators require careful design     |
| **Tooling**          | Mature streaming frameworks available              | Historical replay at batch scale requires careful tuning |

### Choosing Between Lambda and Kappa

```
Decision Guide

  Is low-latency (< seconds) required?
      |
      +-- No --> Classic Batch ETL is sufficient (simpler)
      |
      Yes
      |
      v
  Is exactly-correct re-computation of history important?
      |
      +-- Yes + team has capacity for two codebases --> Lambda
      |
      +-- Yes + team prefers single codebase + log retention feasible --> Kappa
      |
      +-- Approximate / near-correct is acceptable --> Speed layer only (simplified Lambda)
```

| Factor                        | Favour Lambda                          | Favour Kappa                              |
| ----------------------------- | -------------------------------------- | ----------------------------------------- |
| **Team size / complexity**    | Larger teams with specialised roles    | Smaller teams preferring unified code     |
| **Correctness requirements**  | Strict – batch layer guarantees accuracy | Achievable through idempotent streaming  |
| **Log retention cost**        | Not required to retain full history    | Full history must be kept in stream log   |
| **Re-processing frequency**   | Infrequent, scheduled batch runs OK    | Frequent logic changes need fast replay   |
| **Data volume**                | Petabyte-scale where streaming is hard | Manageable with stream parallelism        |
| **Existing infrastructure**   | Hadoop / Spark ecosystem in place      | Kafka-centric organisation                |

### Real-World Implementations

- **LinkedIn** uses a Kappa-inspired architecture built around Kafka and Samza to power its activity feed, notifications, and analytics at scale.
- **Netflix** combines a Lambda-style batch layer (Spark on S3) with a speed layer (Flink + Kafka) for its recommendation and A/B testing systems.
- **Uber** operates a Lambda-like system where batch Hive/Spark jobs produce accurate aggregate metrics, while Flink provides real-time surge pricing signals.
- **Twitter** moved parts of its analytics from Hadoop batch jobs toward a streaming-first Kappa model with Kafka and Heron (a Flink/Storm successor).

### Modern Hybrid Approaches

Newer frameworks blur the line between Lambda and Kappa:

- **Apache Flink** processes both bounded (batch) and unbounded (stream) datasets with a unified API, making it natural to implement Lambda-like correctness with a single codebase.
- **Apache Spark Structured Streaming** uses the same DataFrame API for both batch and streaming jobs, reducing the dual-codebase problem.
- **Delta Lake / Apache Iceberg / Apache Hudi** provide transactional ACID semantics on object storage, enabling **streaming writes** and **batch reads** from the same table without the complexity of separate serving layers.
- **Materialize / RisingWave** are streaming SQL databases that maintain incremental query results in real time, aiming to make streaming as accessible as SQL batch queries.
