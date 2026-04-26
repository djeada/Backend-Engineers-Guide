## ETL and ELT Pipelines

**ETL** (Extract, Transform, Load) and **ELT** (Extract, Load, Transform) are foundational patterns for moving and reshaping data between systems. They are the workhorses behind data warehouses, analytics platforms, and machine learning feature stores, providing a structured way to ingest raw data and deliver clean, well-modelled datasets to consumers.

```
ETL Pipeline Overview

+------------------+    +------------------+    +------------------+    +------------------+
|                  |    |                  |    |                  |    |                  |
|  Source Systems  +--->+    Extract       +--->+   Transform      +--->+   Destination    |
| (DBs, APIs, Files|    | (read raw data)  |    | (clean, enrich,  |    | (DW, Data Lake,  |
|  Streams, etc.)  |    |                  |    |  aggregate, join)|    |  Analytics DB)   |
+------------------+    +------------------+    +------------------+    +------------------+
```

- The **extract** step reads raw data from one or more heterogeneous sources without modifying them.
- The **transform** step applies business rules, cleans dirty records, enriches with lookup data, and reshapes structures.
- The **load** step writes the processed data into the target system in an efficient, bulk-friendly manner.

### ETL vs ELT

In classic **ETL** the transformation happens *before* the data lands in the destination, which is important when the target system is expensive or when sensitive data must be masked during transit. **ELT** reverses the order: raw data is loaded first into a powerful columnar warehouse (Snowflake, BigQuery, Redshift), and transformations run *inside* the warehouse using SQL.

| Aspect              | ETL                                           | ELT                                              |
| ------------------- | --------------------------------------------- | ------------------------------------------------ |
| **Transform where** | Intermediate staging server / compute cluster | Inside the destination data warehouse            |
| **Tooling**         | Informatica, Talend, Apache Spark, dbt + Airbyte | Fivetran + dbt, Airbyte + dbt, native SQL jobs |
| **Raw data kept**   | Often discarded after transform               | Raw layer preserved for re-transformation        |
| **Latency**         | Higher – transform must complete before load  | Lower initial load; transforms run asynchronously |
| **Cost model**      | Compute cost on ETL cluster                   | Compute cost on warehouse (pay per query/slot)   |
| **Re-processing**   | Requires re-running the full ETL job          | Re-run SQL transforms against stored raw layer   |
| **Best for**        | Regulated data, limited warehouse compute     | Cloud warehouses with abundant compute           |

### Extract Phase

The extract phase must be **resilient**: sources may be unavailable, schemas may change, or data volumes may spike.

- **Full extraction** reads the entire source dataset on every run; simple but expensive for large tables.
- **Incremental extraction** reads only rows changed since the last run, relying on a watermark column (`updated_at`) or a log-sequence-number.
- **Change Data Capture (CDC)** streams row-level database changes directly from the write-ahead log, enabling near-real-time extraction with minimal source load.

```
Incremental Extraction with Watermark

  Source Table                             ETL Engine
  +------+------+---------------------+   
  |  id  | ...  | updated_at          |   1. Read MAX(updated_at) from checkpoint store
  +------+------+---------------------+   2. SELECT * WHERE updated_at > checkpoint
  |  1   | ...  | 2024-01-10 08:00    |   3. Process extracted rows
  |  2   | ...  | 2024-01-11 09:15    |   4. Write new MAX(updated_at) back to checkpoint
  |  3   | ...  | 2024-01-12 07:30    |   
  +------+------+---------------------+   
```

### Transform Phase

Transforms cover a wide range of operations applied to the extracted data:

- **Cleaning** – remove nulls, trim whitespace, standardise casing, parse malformed dates.
- **Deduplication** – identify and remove duplicate records introduced by at-least-once delivery or source bugs.
- **Enrichment** – join with reference data (currency rates, product dimensions, geo lookups).
- **Aggregation** – compute sums, averages, counts at the granularity required by the destination.
- **Schema mapping** – rename columns, split or merge fields, convert data types.
- **Validation** – enforce constraints and route invalid records to a quarantine table for manual review.

```
Transform Pipeline Stages

  Raw Record                                   Clean Record
  +---------------------+                      +---------------------+
  | id: "007"           |  --> Parse int    --> | id: 7               |
  | email: " A@B.COM "  |  --> Normalise    --> | email: "a@b.com"    |
  | amount: "1,234.5"   |  --> Parse float  --> | amount: 1234.5      |
  | country: null       |  --> Default      --> | country: "UNKNOWN"  |
  | ts: "01/12/2024"    |  --> ISO format   --> | ts: "2024-01-12"    |
  +---------------------+                      +---------------------+
```

### Load Phase

The load phase writes clean data into the destination efficiently.

- **Full load / truncate-and-reload** replaces the destination table entirely on each run; simple but expensive.
- **Incremental (append)** inserts only new records; fast but may leave stale rows if updates are not handled.
- **Upsert (merge)** updates existing rows and inserts new ones using a primary key; correct for slowly changing data.
- **Slowly Changing Dimensions (SCD)** track historical changes to reference data (e.g. a customer's address over time).

```
Upsert (Merge) Logic

  Incoming Record (key=42)             Destination Table
  +-----------+----------+             +-----------+----------+--------+
  | key | value_new      |             | key | value_old      | active |
  +-----+----------------+             +-----+----------------+--------+
  |  42 | updated_value  |   MERGE --> |  42 | old_value      |  true  |
  +-----+----------------+             +-----+----------------+--------+
                                             (row updated in place)
```

### Data Quality and Validation

Embedding quality checks directly into the pipeline prevents bad data from propagating downstream.

- **Schema validation** – assert expected column names, data types, and nullability constraints.
- **Range and format checks** – verify that amounts are positive, dates fall within expected bounds, enums are valid.
- **Referential integrity** – confirm that foreign keys resolve to known dimension rows.
- **Statistical assertions** – alert when row counts or aggregate values deviate significantly from historical norms.
- **Quarantine table** – redirect failing records to a side table for investigation rather than failing the entire run.

### Idempotency and Restartability

A well-designed pipeline should be **safe to re-run** after a failure without producing duplicate or inconsistent data.

- Design each pipeline stage so that running it twice produces the same result as running it once.
- Use checkpoints to record the last successfully processed offset or partition.
- Wrap loads in database transactions or use staging tables with atomic swaps to avoid partial writes.

```
Idempotent Load Pattern

  1. Load data into temporary staging table (stage_orders_20240112)
  2. Run validations against the staging table
  3. Atomically swap staging → production:
       BEGIN;
       DELETE FROM orders WHERE date = '2024-01-12';
       INSERT INTO orders SELECT * FROM stage_orders_20240112;
       COMMIT;
  4. Drop staging table
```

### Common ETL Tools and Frameworks

| Tool / Framework  | Category              | Key Characteristics                                        |
| ----------------- | --------------------- | ---------------------------------------------------------- |
| **Apache Spark**  | Distributed compute   | In-memory processing, large-scale batch and micro-batch    |
| **dbt**           | SQL transform layer   | Version-controlled SQL models, lineage, testing            |
| **Airbyte**       | Connector platform    | 300+ source/destination connectors, open-source            |
| **Fivetran**      | Managed ELT           | Fully managed connectors, automatic schema migration       |
| **Apache NiFi**   | Data flow             | Visual dataflow designer, drag-and-drop routing            |
| **AWS Glue**      | Managed ETL           | Serverless Spark, integrated with AWS ecosystem            |
| **Talend**        | Enterprise ETL        | GUI-driven, broad connector library, data quality built-in |
| **Pentaho**       | Open-source ETL       | Kettle engine, GUI designer, community and enterprise tiers|

### Best Practices

- Keep raw data in a separate **landing zone** before any transformation so the source of truth is always available for re-processing.
- Version control transform logic with tools like **dbt** to enable code review, rollback, and lineage tracking.
- Log every pipeline run with row counts, timings, and any quarantined records to aid debugging and auditing.
- Use **schema registries** (e.g., Confluent Schema Registry, AWS Glue Schema Registry) when sources publish Avro or Protobuf messages to catch schema evolution issues early.
- Monitor **data freshness** – track the age of the latest record in destination tables and alert when pipelines fall behind their SLA.
- Apply **column-level encryption or masking** during the transform phase to protect sensitive fields (PII, payment data) before they land in shared analytics environments.
