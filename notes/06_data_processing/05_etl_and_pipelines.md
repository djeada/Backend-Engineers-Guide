## ETL and ELT Pipelines

**ETL** and **ELT** are foundational patterns for moving, cleaning, reshaping, and delivering data between systems.

**ETL** means **Extract, Transform, Load**. Data is extracted from source systems, transformed in a processing layer, and then loaded into the destination.

**ELT** means **Extract, Load, Transform**. Data is extracted from source systems and loaded into the destination first. Transformations then happen inside the destination system, usually a cloud data warehouse.

These patterns are used behind data warehouses, dashboards, analytics platforms, reporting systems, machine learning feature stores, customer data platforms, and business intelligence workflows.

```text
ETL Pipeline Overview

+------------------+    +------------------+    +------------------+    +------------------+
|                  |    |                  |    |                  |    |                  |
|  Source Systems  +--->+    Extract       +--->+   Transform      +--->+   Destination    |
| DBs, APIs, Files |    | read raw data    |    | clean, enrich,   |    | DW, Data Lake,   |
| Streams, etc.    |    |                  |    | aggregate, join  |    | Analytics DB     |
+------------------+    +------------------+    +------------------+    +------------------+
```

Example source record:

```json
{
  "id": "007",
  "email": " A@B.COM ",
  "amount": "1,234.5",
  "country": null,
  "ts": "01/12/2024"
}
```

Example processed output:

```json
{
  "id": 7,
  "email": "a@b.com",
  "amount": 1234.5,
  "country": "UNKNOWN",
  "ts": "2024-01-12"
}
```

The source record is messy and inconsistent. The processed output is cleaner, typed correctly, and easier for downstream analytics systems to use.

---

### ETL vs ELT

ETL and ELT use the same general steps, but the order is different.

In classic **ETL**, transformation happens before the data reaches the destination. This is useful when data must be cleaned, masked, filtered, or standardized before landing in a warehouse or analytics environment.

In **ELT**, raw data is loaded into the destination first. Transformations then happen inside the data warehouse using SQL or warehouse-native compute. This is common with modern cloud warehouses such as Snowflake, BigQuery, Redshift, and Databricks.

| Aspect              | ETL                                                                  | ELT                                                           |
| ------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Transform where** | Intermediate staging server or compute cluster                       | Inside the destination data warehouse                         |
| **Tooling**         | Informatica, Talend, Apache Spark, dbt + Airbyte                     | Fivetran + dbt, Airbyte + dbt, native SQL jobs                |
| **Raw data kept**   | Often discarded after transform                                      | Raw layer preserved for re-transformation                     |
| **Latency**         | Higher because transform must complete before load                   | Lower initial load; transforms can run asynchronously         |
| **Cost model**      | Compute cost on ETL cluster                                          | Compute cost on warehouse                                     |
| **Re-processing**   | Often requires re-running the full ETL job                           | Re-run SQL transforms against stored raw layer                |
| **Best for**        | Regulated data, limited warehouse compute, strict pre-load cleansing | Cloud warehouses with scalable compute and raw data retention |

Example ETL flow:

```text
Source database → Spark transform job → Clean warehouse table
```

Example ELT flow:

```text
Source database → Raw warehouse table → dbt SQL models → Clean analytics table
```

Example output:

```json
{
  "etl": "transforms before loading into destination",
  "elt": "loads raw data first and transforms inside the destination"
}
```

The choice depends on cost, compliance, data volume, warehouse capability, and how much raw data the organization wants to preserve.

---

### Extract Phase

The extract phase reads data from source systems. These sources may include relational databases, NoSQL stores, SaaS APIs, flat files, object storage, logs, event streams, or message queues.

Extraction should be resilient. Source systems may be temporarily unavailable, APIs may rate-limit requests, schemas may change, and data volumes may spike. A good extraction process handles retries, checkpoints, pagination, authentication, and schema changes carefully.

Common extraction strategies include full extraction, incremental extraction, and Change Data Capture.

---

#### Full Extraction

Full extraction reads the entire source dataset each time the pipeline runs. This is simple because the pipeline does not need to track which records changed.

Example full extraction query:

```sql
SELECT * FROM customers;
```

Example output:

```json
{
  "extractMode": "full",
  "rowsRead": 250000,
  "source": "customers"
}
```

Full extraction is easy to understand, but it can become expensive and slow for large tables. It may also place unnecessary load on the source system.

---

#### Incremental Extraction

Incremental extraction reads only records that changed since the last successful run. This usually depends on a watermark column such as `updated_at`, `created_at`, or a log sequence number.

```text
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

Example query:

```sql
SELECT *
FROM orders
WHERE updated_at > '2024-01-11 09:15:00';
```

Example output:

```json
{
  "extractMode": "incremental",
  "checkpoint": "2024-01-11 09:15:00",
  "rowsRead": 1842,
  "newCheckpoint": "2024-01-12 07:30:00"
}
```

Incremental extraction is more efficient than full extraction, but it requires reliable change-tracking fields. If timestamps are missing, delayed, or overwritten incorrectly, changes may be skipped.

---

#### Change Data Capture

Change Data Capture, or CDC, streams row-level database changes from database logs. Instead of repeatedly querying tables, CDC reads changes such as inserts, updates, and deletes from the database’s transaction log, binlog, or write-ahead log.

Example CDC event:

```json
{
  "operation": "update",
  "table": "orders",
  "before": {
    "id": 42,
    "status": "pending"
  },
  "after": {
    "id": 42,
    "status": "paid"
  },
  "timestamp": "2024-01-12T07:30:00Z"
}
```

Example output:

```json
{
  "extractMode": "cdc",
  "source": "database_transaction_log",
  "latency": "near-real-time"
}
```

CDC is useful when teams need low-latency synchronization with minimal source database load. It is common for keeping warehouses, caches, search indexes, and downstream services up to date.

---

### Transform Phase

The transform phase converts raw extracted data into a clean, useful, and reliable shape. This is where business rules are applied.

Transforms may fix data quality problems, convert data types, standardize names, remove duplicates, enrich records, join datasets, aggregate metrics, mask sensitive data, or validate constraints.

```text
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

Common transformations include:

* **Cleaning**: Remove nulls, trim whitespace, standardize casing, and parse malformed dates.
* **Deduplication**: Remove duplicate records caused by retries, at-least-once delivery, or source bugs.
* **Enrichment**: Join with reference data such as currency rates, product dimensions, or geographic mappings.
* **Aggregation**: Calculate sums, averages, counts, and grouped metrics.
* **Schema mapping**: Rename columns, split fields, merge fields, and convert data types.
* **Validation**: Enforce constraints and route invalid records to quarantine.

Example transform input:

```json
{
  "customer_id": "0012",
  "email": " ALICE@EXAMPLE.COM ",
  "country_code": "de"
}
```

Example transform output:

```json
{
  "customer_id": 12,
  "email": "alice@example.com",
  "country_code": "DE",
  "country_name": "Germany"
}
```

The transformed record is easier to query, join, validate, and report on.

---

### Load Phase

The load phase writes data into the destination system. The destination may be a data warehouse, data lake, analytics database, search index, feature store, or reporting table.

Loading must be efficient and reliable. Large datasets should often be written in bulk rather than row by row. The load phase should also avoid partial writes, duplicates, and inconsistent destination state.

Common load strategies include full load, append, upsert, and slowly changing dimensions.

---

#### Full Load

A full load replaces the destination table entirely. This is simple and reliable for small datasets.

Example full load pattern:

```sql
TRUNCATE TABLE reporting.customers;
INSERT INTO reporting.customers
SELECT * FROM staging.customers_clean;
```

Example output:

```json
{
  "loadMode": "full",
  "table": "reporting.customers",
  "rowsLoaded": 250000
}
```

Full loads are easy to reason about, but they can be expensive for large tables.

---

#### Incremental Append

An append load inserts only new records. This is fast when data is immutable, such as event logs, clickstreams, or transaction history.

Example append:

```sql
INSERT INTO analytics.events
SELECT *
FROM staging.new_events;
```

Example output:

```json
{
  "loadMode": "append",
  "rowsInserted": 12000
}
```

Append-only loads are efficient, but they do not handle updates or deletes unless additional logic is added.

---

#### Upsert or Merge

An upsert updates existing rows and inserts new rows. It is useful when source records can change over time.

```text
Upsert Merge Logic

  Incoming Record key=42              Destination Table
  +-----+---------------+             +-----+---------------+--------+
  | key | value_new     |             | key | value_old     | active |
  +-----+---------------+             +-----+---------------+--------+
  |  42 | updated_value |   MERGE --> |  42 | old_value     | true   |
  +-----+---------------+             +-----+---------------+--------+
                                             row updated in place
```

Example SQL merge:

```sql
MERGE INTO dim_customers target
USING staging.customers source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
  UPDATE SET email = source.email, updated_at = source.updated_at
WHEN NOT MATCHED THEN
  INSERT (customer_id, email, updated_at)
  VALUES (source.customer_id, source.email, source.updated_at);
```

Example output:

```json
{
  "loadMode": "merge",
  "rowsUpdated": 850,
  "rowsInserted": 120
}
```

Merge logic is more complex than append, but it is more accurate for changing business entities.

---

#### Slowly Changing Dimensions

Slowly Changing Dimensions, or SCDs, track historical changes to reference data. For example, a customer’s address, subscription tier, or region may change over time.

Instead of overwriting the old value, an SCD table can keep history.

Example SCD output:

```json
[
  {
    "customer_id": 42,
    "address": "Old Street 1",
    "valid_from": "2023-01-01",
    "valid_to": "2024-01-11",
    "active": false
  },
  {
    "customer_id": 42,
    "address": "New Street 9",
    "valid_from": "2024-01-12",
    "valid_to": null,
    "active": true
  }
]
```

This allows analysts to answer historical questions accurately, such as “What region was this customer in when the order was placed?”

---

### Data Quality and Validation

Data quality checks prevent bad data from spreading downstream. If a pipeline silently loads invalid records, dashboards, reports, machine learning models, and business decisions may become unreliable.

Quality checks should be embedded directly into the pipeline. They should run before data is published to trusted tables.

Common checks include:

* **Schema validation**: Confirm expected column names, data types, and nullability.
* **Range and format checks**: Verify that amounts are positive, dates are realistic, and enums are valid.
* **Referential integrity**: Confirm foreign keys match known dimension records.
* **Statistical assertions**: Alert when row counts or totals deviate from historical norms.
* **Quarantine tables**: Store invalid records separately for investigation.

Example validation rules:

```json
{
  "amount": {
    "type": "number",
    "minimum": 0
  },
  "email": {
    "type": "string",
    "format": "email"
  },
  "country_code": {
    "allowedValues": ["DE", "FR", "US", "GB"]
  }
}
```

Example invalid record:

```json
{
  "email": "not-an-email",
  "amount": -500,
  "country_code": "UNKNOWN"
}
```

Example quarantine output:

```json
{
  "destination": "quarantine.invalid_orders",
  "reason": [
    "invalid email format",
    "amount must be non-negative",
    "unknown country code"
  ]
}
```

Quarantining invalid records allows the pipeline to continue while still preserving evidence for investigation.

---

### Idempotency and Restartability

A good pipeline should be safe to rerun after a failure. If a job fails halfway through, rerunning it should not create duplicate rows, double-count metrics, or corrupt the destination.

**Idempotency** means that running the same operation multiple times produces the same final result as running it once.

**Restartability** means the pipeline can resume from a known safe point, such as the last successful checkpoint, partition, or offset.

```text
Idempotent Load Pattern

  1. Load data into temporary staging table stage_orders_20240112
  2. Run validations against the staging table
  3. Atomically swap staging → production:
       BEGIN;
       DELETE FROM orders WHERE date = '2024-01-12';
       INSERT INTO orders SELECT * FROM stage_orders_20240112;
       COMMIT;
  4. Drop staging table
```

Example checkpoint:

```json
{
  "pipeline": "orders_daily",
  "lastSuccessfulPartition": "2024-01-12",
  "status": "checkpoint_saved"
}
```

Example restart output:

```json
{
  "pipeline": "orders_daily",
  "restartFrom": "2024-01-13",
  "duplicateRowsCreated": false
}
```

Transactions, staging tables, atomic swaps, and checkpoints help make pipelines reliable even when failures occur.

---

### Common ETL Tools and Frameworks

Different tools solve different parts of the data pipeline problem. Some focus on extraction, some on transformation, some on orchestration, and others on large-scale compute.

| Tool / Framework | Category            | Key Characteristics                                               |
| ---------------- | ------------------- | ----------------------------------------------------------------- |
| **Apache Spark** | Distributed compute | In-memory processing, large-scale batch and micro-batch workloads |
| **dbt**          | SQL transform layer | Version-controlled SQL models, lineage, testing, documentation    |
| **Airbyte**      | Connector platform  | Open-source connectors for many sources and destinations          |
| **Fivetran**     | Managed ELT         | Fully managed connectors, automatic schema migration              |
| **Apache NiFi**  | Data flow           | Visual dataflow designer, routing, backpressure, provenance       |
| **AWS Glue**     | Managed ETL         | Serverless Spark integrated with AWS services                     |
| **Talend**       | Enterprise ETL      | GUI-driven pipelines, broad connectors, data quality features     |
| **Pentaho**      | Open-source ETL     | Kettle engine, GUI designer, community and enterprise options     |

Example modern ELT stack:

```text
Fivetran or Airbyte → Raw warehouse tables → dbt models → BI dashboards
```

Example output:

```json
{
  "extractLoadTool": "Airbyte",
  "transformTool": "dbt",
  "destination": "Snowflake",
  "consumer": "BI dashboard"
}
```

Tool selection depends on team skills, data volume, latency requirements, cost, connector needs, and governance requirements.

---

### Best Practices

Strong ETL and ELT pipelines are reliable, observable, restartable, and easy to change. They should preserve raw data, validate outputs, protect sensitive fields, and provide clear lineage.

Recommended practices include:

1. **Keep raw data in a landing zone**
   Store source data before transformation so it can be reprocessed later.

2. **Version control transform logic**
   Tools such as dbt allow SQL models to be reviewed, tested, documented, and rolled back.

3. **Log pipeline runs**
   Track row counts, timings, failed records, source checkpoints, and destination tables.

4. **Use schema registries for event data**
   Schema registries help detect incompatible changes in Avro, Protobuf, or JSON event streams.

5. **Monitor data freshness**
   Track the newest record in each destination table and alert when pipelines fall behind their SLA.

6. **Protect sensitive fields**
   Apply masking, hashing, tokenization, or encryption for PII, payment data, and credentials.

Example pipeline run log:

```json
{
  "pipeline": "orders_to_warehouse",
  "runId": "run-20240112-001",
  "rowsExtracted": 120000,
  "rowsTransformed": 119950,
  "rowsQuarantined": 50,
  "rowsLoaded": 119950,
  "durationSeconds": 420,
  "status": "success"
}
```

Example freshness alert:

```json
{
  "table": "analytics.orders",
  "latestRecordTimestamp": "2024-01-12T07:30:00Z",
  "freshnessSlaMinutes": 60,
  "status": "within_sla"
}
```

Good pipelines are not just about moving data. They are about delivering trustworthy, timely, well-documented data that downstream users can rely on.
