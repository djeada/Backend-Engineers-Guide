## Workflow Orchestration

As data pipelines grow beyond a single script, they become networks of interdependent steps that must run in the right order, on a schedule, with retries on failure, and with observable state. **Workflow orchestration** is the discipline of managing this complexity: defining the execution order of tasks, scheduling runs, tracking dependencies, handling failures, and providing visibility into pipeline health.

```
Workflow Orchestration Overview

  Schedule / Trigger
        |
        v
+-------+---------+
|                 |
|   Orchestrator  |  <-- schedules runs, resolves dependencies, handles retries
|   (Airflow,     |
|    Prefect,     |
|    Dagster, ...) |
+---+---+---+-----+
    |   |   |
    |   |   +---> Task C (depends on A and B)
    |   |
    |   +-------> Task B (depends on A)
    |
    +-----------> Task A (no dependencies, runs first)
```

- An orchestrator treats a pipeline as a **Directed Acyclic Graph (DAG)**: nodes are tasks and edges are dependencies.
- It ensures tasks run only after their upstream dependencies have succeeded.
- It provides centralised **retry logic**, **alerting**, **logging**, and a UI for monitoring pipeline state.
- Tasks themselves are kept **thin** – they delegate heavy computation to specialised systems (Spark, dbt, databases), while the orchestrator manages the control flow.

### Directed Acyclic Graphs (DAGs)

A DAG is the fundamental building block of workflow orchestration. The **directed** property means data flows in one direction (upstream to downstream), and the **acyclic** property means no task can depend on itself directly or transitively.

```
Example DAG: Daily Sales Report Pipeline

  extract_crm ----\
                   +--> join_sources --> transform_revenue --> load_warehouse --> notify_team
  extract_erp ----/
                        |
                        v
                   validate_data (runs in parallel with transform_revenue after join_sources)
```

- Nodes with no incoming edges (**source tasks**) are the entry points; they run as soon as a trigger fires.
- Nodes with no outgoing edges (**sink tasks**) are the final steps; the DAG is complete when they finish.
- Tasks at the same level with no mutual dependencies can run **in parallel**, improving throughput.
- If a task fails, the orchestrator marks all downstream tasks as **blocked** and begins retry logic or raises an alert.

### Core Orchestration Concepts

#### Scheduling

Orchestrators support multiple trigger mechanisms:

- **Cron-based scheduling** – run at a fixed time, such as `0 2 * * *` (daily at 02:00 UTC).
- **Event-driven triggers** – start when a file arrives in S3, a message lands in Kafka, or an upstream pipeline completes.
- **Sensor tasks** – poll an external condition (file existence, API status) and unblock downstream tasks when satisfied.
- **Manual / API triggers** – start a run on demand from the UI or a CI/CD pipeline.

#### Task State Machine

Each task instance transitions through a well-defined set of states:

```
Task State Transitions

  SCHEDULED --> QUEUED --> RUNNING --> SUCCESS
                               |
                               +--> FAILED --> (retry logic)
                               |         \
                               |          +--> RETRYING --> RUNNING
                               |                      \
                               |                       +--> FAILED (max retries exceeded)
                               |                                \
                               |                                 +--> DEAD_LETTER / ALERT
                               |
                               +--> SKIPPED  (upstream condition not met)
                               |
                               +--> UPSTREAM_FAILED (dependency failed, task blocked)
```

#### Retry Logic and Backoff

Transient failures (network timeouts, API rate limits) can be handled automatically:

- **Max retries** – limit the number of attempts before marking a task permanently failed.
- **Retry delay** – wait before re-attempting to give transient conditions time to resolve.
- **Exponential backoff** – double the delay between each successive attempt to avoid hammering a struggling dependency.

```
Exponential Backoff Example

  Attempt 1 (failed) --> wait 30s
  Attempt 2 (failed) --> wait 60s
  Attempt 3 (failed) --> wait 120s
  Attempt 4 (failed) --> wait 240s
  Attempt 5 (failed) --> max retries exceeded --> ALERT
```

#### Backfilling

When a pipeline has been down, or when business logic changes require re-processing historical data, orchestrators support **backfills** – running a DAG for a past time range:

- The orchestrator creates a run for each historical **execution date** in the requested range.
- Tasks process data scoped to their execution date, ensuring idempotency.
- Backfill runs can be parallelised or throttled to avoid overloading downstream systems.

### Data Lineage and Observability

Orchestrators track which tasks consume and produce which datasets, building a graph of **data lineage** that answers questions like "which downstream reports are affected if this table changes?"

```
Lineage Example

  raw_orders (table)
       |
       v
  transform_orders (task) --> clean_orders (table)
                                    |
                                    +-----> daily_revenue_report (task)
                                    |
                                    +-----> customer_churn_model (task)
```

Key observability signals to monitor:

- **Run duration** – alert when a pipeline takes significantly longer than its SLA.
- **Task failure rate** – track the percentage of failed tasks over time.
- **Data freshness** – measure the age of the latest record in destination tables.
- **Queue depth** – number of tasks waiting to be executed; high values indicate worker shortage.
- **Retry rate** – frequent retries indicate an unhealthy upstream dependency.

### Popular Orchestration Tools

#### Apache Airflow

Apache Airflow is the most widely adopted open-source orchestrator. Pipelines are defined as Python DAGs, providing full programmability.

```python
# Minimal Airflow DAG example (illustrative, not runnable without Airflow)
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    print("Extracting data from source...")

def transform():
    print("Transforming data...")

def load():
    print("Loading data into warehouse...")

with DAG("daily_etl", start_date=datetime(2024, 1, 1), schedule="@daily") as dag:
    t_extract   = PythonOperator(task_id="extract",   python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform)
    t_load      = PythonOperator(task_id="load",      python_callable=load)

    t_extract >> t_transform >> t_load
```

- **Scheduler** parses DAG files, creates task instances on schedule, and places them on the queue.
- **Workers** (Celery, Kubernetes pods, or local processes) execute individual task instances.
- **Web UI** provides a Gantt chart, tree view, and logs for every task run.
- **XCom** (cross-communication) allows tasks to pass small pieces of data to downstream tasks.

#### Prefect

Prefect offers a Python-native API with a strong focus on developer experience. Flows and tasks are plain Python functions decorated with `@flow` and `@task`.

```python
# Minimal Prefect flow example (illustrative)
from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
def extract():
    return {"records": 100}

@task
def transform(data):
    return {**data, "cleaned": True}

@task
def load(data):
    print(f"Loaded {data['records']} clean records")

@flow
def daily_etl():
    raw = extract()
    clean = transform(raw)
    load(clean)
```

#### Dagster

Dagster is an asset-centric orchestrator that models pipelines in terms of **data assets** (tables, files, models) rather than just tasks, making lineage and dependency management explicit.

- **Software-defined assets** declare what each job produces, enabling automatic lineage graphs.
- **Partitions** express that an asset has a slice per time period, geography, or other dimension.
- **Sensors** watch for new data and trigger materialisation of downstream assets automatically.

#### Other Tools

| Tool              | Model              | Best For                                               |
| ----------------- | ------------------ | ------------------------------------------------------ |
| **Apache Airflow**| Task-centric DAG   | Large organisations, rich operator ecosystem           |
| **Prefect**       | Flow / task Python | Teams that want pythonic, testable workflows            |
| **Dagster**       | Asset-centric      | Data engineering teams needing strong lineage and typing|
| **Luigi**         | Task dependency    | Lightweight pipelines, Spotify-originated              |
| **Argo Workflows**| Kubernetes-native  | Cloud-native teams already running on Kubernetes        |
| **Temporal**      | Durable execution  | Long-running workflows with complex compensation logic  |
| **dbt**           | SQL transform DAG  | Analytics engineering, warehouse-centric transforms    |

### Patterns and Best Practices

#### Idempotent Tasks

Every task should produce the same result whether it runs once or multiple times for the same input. This makes retries and backfills safe.

```
Idempotency Approaches

  INSERT OR REPLACE INTO results SELECT ... WHERE date = '{{ ds }}'
        ^
        Use execution date as partition key so re-runs overwrite, not append
```

#### Parametric Pipelines

Pipelines should accept runtime parameters (date ranges, target environments, feature flags) rather than hardcoding values, enabling flexible backfills and multi-environment deployments.

#### Decoupling Orchestration from Computation

The orchestrator should be a **thin control plane**:

- Tasks trigger Spark jobs, dbt runs, SQL queries, or API calls rather than doing heavy computation inline.
- This keeps the orchestrator lightweight and lets compute scale independently.
- Separating concerns makes it easier to swap orchestrators or compute engines without rewriting business logic.

#### Testing Pipelines

- **Unit-test task functions** in isolation by mocking external systems.
- **Integration-test DAGs** against a test environment with synthetic data.
- **Validate DAG structure** programmatically (Airflow's `dag.test()` mode, Prefect's `flow.visualize()`).
- Include **data quality assertions** as dedicated tasks that fail the pipeline if data violates expectations.

#### Secret Management

- Never hardcode credentials in DAG code; use the orchestrator's native secrets backend (Airflow Connections, Prefect Blocks, environment variables injected at runtime).
- Rotate secrets automatically where possible and audit access.

### Monitoring and Alerting

```
Alert Escalation Flow

  Task Failure Detected
          |
          v
  Send alert to #data-alerts Slack channel
          |
          v (if not acknowledged in 15 min)
  Page on-call engineer via PagerDuty
          |
          v (if SLA breach detected)
  Auto-create incident ticket in Jira
```

- Configure **SLA miss callbacks** so the orchestrator proactively notifies teams before business stakeholders notice stale dashboards.
- Emit task execution metrics to **Prometheus** or **Datadog** for long-term trend analysis.
- Archive task logs to object storage (S3, GCS) so they are available even after the orchestrator's local log retention period expires.
