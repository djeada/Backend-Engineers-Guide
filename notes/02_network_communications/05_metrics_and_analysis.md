## Metrics and Analysis
In modern distributed systems, the performance and reliability of communication channels, APIs, and network infrastructure are critical factors that determine user experience. Metrics and analysis offer insights into system behavior under varying loads, help identify bottlenecks, and guide capacity planning. Capturing the right metrics and interpreting them correctly leads to robust, scalable architectures. This document explores the core metrics for communication, API usage, and network layers, alongside common formulas, analysis techniques, and best practices in monitoring and diagnostics.

### Why Metrics Matter  
Data-driven decisions about scaling, optimization, and resource allocation rely on the proper collection and interpretation of metrics. Without measurable indicators, developers and operators are left guessing about system performance and reliability. Metrics also facilitate:

1. **Troubleshooting**: Pinpointing service or network segments causing latency spikes or errors.  
2. **Capacity Planning**: Predicting future infrastructure needs based on historical load.  
3. **Service-Level Objectives (SLOs)**: Establishing performance targets and tracking whether services meet those targets.  
4. **Trend Analysis**: Spotting gradual performance degradations before they become outages.  

### Common Terminology and Formulas  

#### Latency and Response Times  
**Latency** is the time it takes for a request to travel from a client to a server and for the server to respond, often including network travel time and server processing. Commonly measured as:

- **p50 (Median)**: Half of requests complete below this time.  
- **p95, p99**: High percentiles that reveal the “worst” performance user experiences.  
- **p100 (Max)**: Maximum observed latency (sometimes too spiky to be useful).

A simplified latency equation for an HTTP request might be:

```
Total_Latency = RTT_network + Server_Processing_Time + (Possible_Queueing_Delay)
```

- **RTT_network**: Round-trip time for packets to travel between client and server.  
- **Server_Processing_Time**: The time the server spends handling the request (compute, I/O, DB calls, etc.).  
- **Possible_Queueing_Delay**: Delays in load balancers, proxies, or OS-level buffers.

#### Throughput and Requests per Second (RPS/QPS)  
**Throughput** indicates how many requests or messages a system can handle over a given time, often expressed as Requests per Second (RPS) or Queries per Second (QPS). If `N_req` is the total number of requests within a measurement window `T`, throughput can be approximated as:

```
Throughput = N_req / T
```

#### Concurrency  
**Concurrency** measures how many requests or connections a system is serving simultaneously. A system that supports large concurrency can handle many in-flight requests at once, but each active request may consume memory and CPU resources.

#### Error Rates  
Common ways to measure errors:

- **4XX Error Rate**: Fraction of client errors (e.g., 400, 404, 401).  
- **5XX Error Rate**: Fraction of server errors (e.g., 500, 503).  
- **Overall Error Rate**: `(Number_of_Error_Responses) / (Total_Requests)`.  

#### Uptime and Availability  
Often expressed as a percentage of time the service is fully operational:

```
Availability (%) = 100 * (Uptime / Total_Time)
```

For critical services, SLOs might require 99.9% or 99.99% availability, corresponding to allowable downtime of minutes or seconds per month.

#### Packet Loss and Network Metrics  
In lower-level network contexts (TCP, UDP), metrics like **packet loss**, **retransmissions**, and **bandwidth utilization** are key:

```
Packet_Loss_Rate = (Packets_Lost / Packets_Sent) * 100
```

Excessive packet loss degrades application performance, especially for real-time or streaming protocols.

### Metrics for APIs  

#### HTTP/RESTful APIs  
For RESTful services, typical metrics include:

1. **Request Latencies** by endpoint and method (GET, POST, etc.).  
2. **Request Throughput** in requests per second or per minute.  
3. **Response Codes**: Monitoring distribution of 2xx, 4xx, 5xx for quick error detection.  
4. **Payload Sizes**: Large payloads can affect network usage and latency.  
5. **Caching Metrics**: Cache hit/miss rates if a caching layer is in use.

A representation of data flow with potential metric collection points:

```
Client (Browser/App) ----> [Load Balancer] ----> [API Server(s)] ----> [Database/Cache]
     |                        |                       |                      |
     | metrics??             | metrics??             | metrics??            | metrics??
     v                        v                       v                      v

Logging & Monitoring Infrastructure (e.g., Prometheus, Grafana, ELK stack)
```

At each stage, logs and performance counters gather metrics on request durations, error rates, and resource usage (CPU/memory).

#### GraphQL APIs  
Similar to REST, but the queries can be more dynamic. Important metrics include:

1. **Resolver Latencies**: Identifying slow resolvers.  
2. **Field Usage**: Finding which fields in the schema are frequently queried.  
3. **Depth and Complexity**: Monitoring how complex queries might degrade performance.

#### gRPC  
Because gRPC uses HTTP/2 and Protobuf, typical metrics include:

1. **RPC Latencies** (per method).  
2. **Inbound/Outbound Traffic** (in bytes).  
3. **Deadline/Timeout Exceeded** events.  
4. **Streaming Metrics** (message count, stream duration).

### Network-Level Metrics  

#### TCP Metrics  
- **RTT (Round Trip Time)**: Base measure of latency.  
- **Window Size**: Congestion window for flow control.  
- **Retransmissions**: High retransmissions can indicate congestion or packet loss.  

#### UDP Metrics  
- **Packet Loss**: Particularly relevant in real-time streaming contexts.  
- **Jitter**: Variation in packet arrival times, crucial for voice/video.  
- **Datagram Throughput**: How many datagrams per second can be handled?

#### Bandwidth and Utilization  
**Bandwidth** is the theoretical max data rate, while **utilization** measures how much of that bandwidth is in use. Monitoring helps avoid saturation. If you see throughput near the link’s capacity, you risk increased latency and packet drops.

### Analyzing and Visualizing Metrics  

#### Dashboards and Tools  
Systems like Prometheus, Graphite, InfluxDB, or DataDog store metrics. Tools like Grafana or Kibana help create real-time dashboards. A typical setup might ingest counters and histograms from applications, store them in a time-series database, and visualize them in charts.

#### Histograms vs Averages  
Relying on averages can be misleading—some users might experience extreme delays while the average remains fine. **Histograms** reveal distribution across multiple buckets, giving better insight into tail latencies (p95, p99).

#### Error Budgets and SLIs/SLOs  
- **SLI (Service Level Indicator)**: A measured metric (e.g., request success rate).  
- **SLO (Service Level Objective)**: A target threshold for that SLI (e.g., 99.9% success rate).  
- **Error Budget**: The allowable number of errors/time of unavailability before the SLO is violated.

Example formula for an SLO around error rate:

```
Error_Rate_SLI = (Number_of_Error_Requests / Total_Requests)
Target: Error_Rate_SLI <= 0.1%
```

If the error rate goes beyond 0.1%, you exceed your error budget.

### Load and Stress Testing  
Performance analysis relies on simulating realistic traffic:

1. **Load Testing**: Evaluate normal to peak loads, measuring throughput, latency, and resource usage.  
2. **Stress Testing**: Push the system beyond capacity to see how it fails and recovers.  
3. **Soak/Endurance Testing**: Sustain high load for an extended period, revealing memory leaks or degrade over time.

Tools like **Apache JMeter**, **Locust**, or **k6** let you define test scripts that emulate real client behavior. Metrics from these tests guide capacity planning and highlight scaling bottlenecks.

### Distributed Tracing  
In microservice architectures, a single request can span multiple services. **Distributed tracing** with solutions like Jaeger or Zipkin tracks how requests hop between services. The system collects timestamps and metadata at each node:

```
   [Service A] -- calls --> [Service B] -- calls --> [Service C]
       |                         |                        |
       v                         v                        v
   (Trace A)                (Trace B)                 (Trace C)

Traces aggregated and visualized in a central UI
```

This reveals which segments of a request path consume the most time or fail often. Tracing complements standard metrics by delivering a request-centric timeline rather than aggregated counters.

### The Three Pillars of Observability

The observability ecosystem is often framed around three complementary data types:

1. **Metrics** – Numeric measurements sampled over time (counters, gauges, histograms). Efficient to store; ideal for dashboards and alerts.
2. **Logs** – Timestamped, human-readable (or structured) event records. Rich in context; expensive to store and query at scale.
3. **Traces** – Causal chains of operations across service boundaries, tied together by a shared trace ID. Reveal where time is spent end-to-end.

```
+-----------+     +-----------+     +-----------+
|  Metrics  |     |   Logs    |     |  Traces   |
|  (gauges, |     | (events,  |     | (spans,   |
|  counters,|     |  errors)  |     |  timelines|
|  histos)  |     |           |     |  per req) |
+-----------+     +-----------+     +-----------+
       \                |                /
        \               |               /
         v              v              v
        +----------------------------------+
        |  Observability Platform / UI     |
        |  (Grafana, Jaeger, Kibana, ...)  |
        +----------------------------------+
```

A mature observability strategy correlates all three signals: a spike in latency metrics leads to the relevant trace, and the trace links to the log lines that reveal the root cause.

### OpenTelemetry

**OpenTelemetry (OTel)** is the CNCF project that standardizes how applications emit metrics, logs, and traces. It replaces vendor-specific SDKs (OpenCensus, OpenTracing) with a single, language-neutral API and SDK.

#### Core Concepts

- **API** – A thin interface layer that application code calls. Importing only the API imposes no dependency on a specific backend.
- **SDK** – The implementation of the API, responsible for sampling, batching, and exporting data.
- **Collector** – A standalone agent/proxy that receives, processes, and exports telemetry to one or more backends (Prometheus, Jaeger, Datadog, etc.).
- **OTLP** – OpenTelemetry Protocol; the wire format for transmitting telemetry between components.

```
+------------------+    OTLP    +-------------------+     +------------------+
|  Application     | ---------> |  OTel Collector   | --> |  Prometheus      |
|  (OTel SDK)      |            |  (receive/process |     +------------------+
+------------------+            |   /export)        | --> +------------------+
                                +-------------------+     |  Jaeger          |
                                                          +------------------+
```

#### Instrumenting a Service (Python example)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("my-service")

def handle_request(request_id: str):
    with tracer.start_as_current_span("handle_request") as span:
        span.set_attribute("request.id", request_id)
        # ... business logic ...
```

#### Collector Configuration (YAML)

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"
      http:
        endpoint: "0.0.0.0:4318"

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
  jaeger:
    endpoint: "jaeger-collector:14250"
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [jaeger]
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
```

### Prometheus

**Prometheus** is the de-facto open-source metrics system for cloud-native environments. It follows a **pull model**: the Prometheus server periodically scrapes HTTP endpoints (`/metrics`) exposed by instrumented services.

#### Data Model

Every time series is identified by a metric name and a set of key-value labels:

```
http_requests_total{method="GET", endpoint="/api/users", status="200"} 4523
http_requests_total{method="POST", endpoint="/api/users", status="500"} 12
```

The four metric types are:

| Type | Description | Example |
|------|-------------|---------|
| Counter | Monotonically increasing value | `requests_total` |
| Gauge | Arbitrary up/down value | `memory_usage_bytes` |
| Histogram | Observed value distribution in configurable buckets | `request_duration_seconds` |
| Summary | Client-side quantile calculation | `request_duration_quantile` |

#### Scrape Configuration (`prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: "api-service"
    static_configs:
      - targets: ["api-service:8080"]
    metrics_path: /metrics
    scheme: http

  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
```

#### PromQL Queries

PromQL is Prometheus's functional query language:

```promql
# Request rate over the last 5 minutes
rate(http_requests_total[5m])

# 99th-percentile latency
histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m]))

# Error ratio
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# CPU saturation across all pods
1 - avg by (pod) (rate(container_cpu_usage_seconds_total[1m]))
```

#### Alerting Rules

```yaml
# alert_rules.yml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
            / sum(rate(http_requests_total[5m])) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 1% for 2 minutes"
          description: "Current error rate: {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p99 latency above 1s"
```

#### Exporters

Prometheus uses exporters to expose metrics from systems that cannot be instrumented directly:

| Exporter | What It Monitors |
|----------|-----------------|
| `node_exporter` | Host CPU, memory, disk, network |
| `blackbox_exporter` | HTTP/HTTPS/TCP/DNS probe results |
| `postgres_exporter` | PostgreSQL query stats, connections |
| `redis_exporter` | Redis memory, commands, keyspace |
| `kafka_exporter` | Kafka broker and consumer group lag |

```bash
# Run node_exporter on the host
docker run -d \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host
```

### Grafana

**Grafana** is the standard open-source platform for building observability dashboards. It connects to dozens of data sources (Prometheus, Loki, Tempo, ClickHouse, Elasticsearch, and more) through a plugin system.

#### Architecture

```
+------------------+    Query    +------------------+
|   Grafana UI     | ----------> |   Prometheus     |
|   (browser)      |             +------------------+
|                  | ----------> +------------------+
|   Dashboards,    |             |   Loki (logs)    |
|   Alerts,        |             +------------------+
|   Annotations    | ----------> +------------------+
+------------------+             |   Tempo (traces) |
                                 +------------------+
```

#### Provisioning Datasources and Dashboards

Grafana supports infrastructure-as-code provisioning via YAML files:

```yaml
# /etc/grafana/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: "15s"
      exemplarTraceIdDestinations:
        - name: trace_id
          datasourceUid: tempo
```

#### Key Panel Types

| Panel | Best For |
|-------|----------|
| Time series | Throughput, latency, error rates over time |
| Stat | Single current value (e.g., uptime, RPS) |
| Gauge | Value relative to a min/max range |
| Bar chart | Comparing values across dimensions |
| Table | Multi-dimensional aggregations |
| Logs | Raw log lines (Loki datasource) |
| Traces | Waterfall span view (Tempo datasource) |

#### Grafana Alerting

Grafana Alerting (unified alerting) evaluates alert rules against any datasource, not just Prometheus:

```yaml
# Grafana alerting rule via API or provisioning
apiVersion: 1
groups:
  - orgId: 1
    name: Backend Alerts
    folder: Production
    interval: 1m
    rules:
      - uid: high-latency-rule
        title: High p99 Latency
        condition: C
        data:
          - refId: A
            datasourceUid: prometheus
            model:
              expr: >
                histogram_quantile(0.99,
                  rate(request_duration_seconds_bucket[5m]))
          - refId: C
            datasourceUid: __expr__
            model:
              type: threshold
              conditions:
                - evaluator:
                    params: [1.0]
                    type: gt
```

### Jaeger

**Jaeger** is a CNCF distributed tracing system originally built by Uber. It collects spans from instrumented services and provides a UI for visualizing trace timelines across microservices.

#### Architecture

```
+-------------+   Spans    +--------------+   +------------------+
|  Service A  | ---------> |              |   |  Jaeger Query    |
+-------------+            |  Jaeger      |   |  (UI + API)      |
+-------------+   Spans    |  Collector   | ->|                  |
|  Service B  | ---------> |              |   +------------------+
+-------------+            +--------------+            |
+-------------+   Spans         |                      v
|  Service C  | ---------> (optional                +------------------+
+-------------+   Kafka         |                   |  Storage         |
                 buffer)        v                   | (Cassandra /     |
                            +-----------+           |  Elasticsearch / |
                            |  Ingester |           |  Badger)         |
                            +-----------+           +------------------+
```

#### Span Model

Each **span** represents a unit of work and contains:

- **Trace ID** – Unique identifier shared by all spans in one request.
- **Span ID** – Unique identifier for this particular operation.
- **Parent Span ID** – Links to the parent call.
- **Operation Name** – Human-readable label (e.g., `db.query`, `http.get`).
- **Start Time / Duration** – When the operation began and how long it took.
- **Tags** – Key-value attributes (e.g., `http.status_code=200`).
- **Logs** – Structured events within the span (e.g., cache miss, retry).

```
Trace: order-checkout  [total 230ms]
 |
 +-- http.server "POST /checkout"         [0ms -> 230ms]
      |
      +-- db.query "SELECT inventory"     [10ms -> 40ms]
      |
      +-- http.client "POST /payment-svc" [45ms -> 180ms]
      |    |
      |    +-- db.query "INSERT payment"  [50ms -> 120ms]
      |
      +-- cache.set "order:789"           [185ms -> 195ms]
```

#### Docker Compose Quick-Start

```yaml
# docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:1.58
    ports:
      - "16686:16686"   # Jaeger UI
      - "14250:14250"   # gRPC collector
      - "4317:4317"     # OTLP gRPC receiver
      - "4318:4318"     # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

#### Sampling Strategies

| Strategy | When to Use |
|----------|-------------|
| Constant (always/never) | Development/debugging |
| Probabilistic | Production with predictable load |
| Rate-limiting | Caps collection at N traces/sec |
| Remote (adaptive) | Dynamic, per-service rate controlled by Jaeger |

```yaml
# jaeger-agent sampling config
default_strategy:
  type: probabilistic
  param: 0.1          # sample 10% of traces

per_operation_strategies:
  - operation: health_check
    type: probabilistic
    param: 0.001       # sample 0.1% of health checks
```

### Perf (Linux Performance Counters)

**`perf`** is the Linux kernel's built-in profiling and tracing tool. It accesses hardware performance counters, kernel tracepoints, and user-space probes without modifying application source code.

#### Common Subcommands

| Command | Purpose |
|---------|---------|
| `perf stat` | Count hardware events (cycles, cache misses, instructions) |
| `perf record` | Sample call stacks and save to `perf.data` |
| `perf report` | Interactive view of profiling data |
| `perf top` | Live, top-like view of hot functions |
| `perf trace` | System-call tracing (like strace, lower overhead) |
| `perf script` | Convert `perf.data` to text for flame graphs |

#### Profiling a Process

```bash
# Count hardware events for 5 seconds
perf stat -e cycles,instructions,cache-misses,cache-references sleep 5

# Sample a running process (PID 1234) at 99 Hz for 10 seconds
perf record -F 99 -p 1234 -g -- sleep 10

# View hot call paths interactively
perf report --stdio

# Generate a flame graph using Brendan Gregg's tools
perf script | stackcollapse-perf.pl | flamegraph.pl > flamegraph.svg
```

#### Key Metrics from `perf stat`

```
 Performance counter stats for 'stress --cpu 4':

      4,123,567,890   cycles
      3,011,234,567   instructions    # 0.73 insns per cycle
         12,345,678   cache-misses    # 2.34% of all cache refs
        527,654,321   cache-references

           5.002103 seconds time elapsed
```

- **IPC (Instructions per Cycle)**: Values below 1.0 often indicate memory or branch misprediction bottlenecks.
- **Cache miss rate**: High values (>5%) signal excessive memory pressure.

#### CPU Flame Graphs

Flame graphs visualize profiling stack samples, with width representing time spent and vertical position showing the call depth:

```
[flamegraph output: wide base = CPU hot path]

   main
    └── serve_request (60%)
         ├── db_query (35%)
         │    └── pg_execute (33%)
         └── json_serialize (20%)
```

```bash
# Continuous profiling for 30 seconds, generate flame graph
perf record -F 99 -a -g -- sleep 30
perf script > /tmp/out.perf
stackcollapse-perf.pl /tmp/out.perf > /tmp/out.folded
flamegraph.pl /tmp/out.folded > /tmp/flamegraph.svg
```

#### eBPF and BCC (Modern Perf Alternative)

The **BCC** toolkit and **bpftrace** use eBPF for kernel-level tracing with lower overhead than `perf`:

```bash
# Trace all new process executions
execsnoop

# Trace slow disk I/O (>10ms)
biolatency -m 10

# Profile CPU off-CPU time
offcputime -f 30

# Count syscalls by process
syscount -p 1234

# Trace TCP connections
tcpconnect
```

### ClickHouse

**ClickHouse** is a column-oriented OLAP database designed for real-time analytics at scale. Its high compression ratios and vectorized query execution make it well-suited for storing and querying large volumes of log and trace data.

#### Why ClickHouse for Observability

| Feature | Benefit |
|---------|---------|
| Columnar storage | Only reads columns needed by the query |
| LZ4/ZSTD compression | 5–10× storage reduction for log data |
| MergeTree engine | Efficient time-range scans and data TTL |
| Vectorized SIMD execution | Sub-second aggregations over billions of rows |
| Materialized views | Pre-aggregate metrics at ingest time |
| Kafka integration | Native table engine for streaming ingest |

#### Schema for Log Storage

```sql
CREATE TABLE logs
(
    timestamp    DateTime64(3, 'UTC'),
    service      LowCardinality(String),
    level        LowCardinality(String),   -- INFO, WARN, ERROR
    trace_id     FixedString(32),
    span_id      FixedString(16),
    message      String,
    attributes   Map(String, String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (service, level, timestamp)
TTL timestamp + INTERVAL 30 DAY DELETE
SETTINGS index_granularity = 8192;
```

#### Schema for Metrics (Prometheus Remote Write)

```sql
CREATE TABLE metrics
(
    timestamp   DateTime,
    name        LowCardinality(String),
    labels      Map(String, String),
    value       Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (name, timestamp)
TTL timestamp + INTERVAL 90 DAY DELETE;
```

#### Analytical Queries

```sql
-- Error rate per service over the last hour
SELECT
    service,
    countIf(level = 'ERROR') / count() AS error_rate
FROM logs
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY service
ORDER BY error_rate DESC;

-- p99 latency from trace spans
SELECT
    service,
    quantile(0.99)(duration_ms) AS p99_latency_ms,
    count()                     AS span_count
FROM spans
WHERE timestamp >= now() - INTERVAL 24 HOUR
GROUP BY service
ORDER BY p99_latency_ms DESC;

-- Top error messages in the last 10 minutes
SELECT
    message,
    count() AS occurrences
FROM logs
WHERE level = 'ERROR'
  AND timestamp >= now() - INTERVAL 10 MINUTE
GROUP BY message
ORDER BY occurrences DESC
LIMIT 20;
```

#### Integrations

- **Grafana**: Official ClickHouse datasource plugin for dashboards and alerts.
- **Vector / Fluent Bit**: Log shippers with ClickHouse output plugins.
- **Prometheus Remote Write**: Proxy (e.g., `clickhouse-prometheus-adapter`) sends metrics to ClickHouse.
- **Altinity Sink Connector**: Kafka-to-ClickHouse connector via Kafka Connect.

### Loki

**Loki** (by Grafana Labs) is a log aggregation system inspired by Prometheus. Instead of indexing log contents, it indexes only **labels** (similar to Prometheus metric labels), keeping storage costs low.

#### Architecture

```
+------------------+    Push     +----------------+    Query    +----------------+
|  Promtail /      | ---------> |  Loki          | <---------- |  Grafana       |
|  Fluent Bit /    |            |  (Distributor  |             |  (LogQL)       |
|  Vector          |            |   Ingester     |             +----------------+
+------------------+            |   Compactor)   |
                                |                |
                                +-------+--------+
                                        |
                                +-------+--------+
                                |  Object Store  |
                                |  (S3 / GCS /   |
                                |   Filesystem)  |
                                +----------------+
```

#### Promtail Configuration

```yaml
# promtail-config.yml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: backend-services
    static_configs:
      - targets:
          - localhost
        labels:
          job: api-service
          env: production
          __path__: /var/log/api-service/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            trace_id: traceId
      - labels:
          level:
          trace_id:
```

#### LogQL Queries

```logql
# Show all ERROR logs for the api-service
{job="api-service", level="ERROR"} |= "timeout"

# Rate of error log lines over 5 minutes
rate({job="api-service", level="ERROR"}[5m])

# Extract and aggregate latency from structured JSON logs
{job="api-service"}
  | json
  | latency_ms > 1000
  | line_format "{{.method}} {{.path}} {{.latency_ms}}ms"

# Count log volume per service
sum by (job) (
  rate({env="production"}[1m])
)
```

### Tempo

**Tempo** (by Grafana Labs) is a scalable, object-storage-backed distributed tracing backend. It accepts spans from OTLP, Jaeger, and Zipkin, and integrates with Grafana for trace visualization.

#### Key Advantages over Jaeger

| Feature | Tempo | Jaeger |
|---------|-------|--------|
| Storage | Object store (S3/GCS) | Cassandra/Elasticsearch |
| Index | TraceID only (no tag index) | Full tag index |
| Cost at scale | Very low | High |
| Grafana integration | Native | Plugin |
| Metrics generation | TraceQL → metrics | Limited |

#### Correlating Logs and Traces

Grafana can automatically navigate from a log line in Loki to the corresponding trace in Tempo using the `trace_id` label:

```yaml
# Grafana datasource: Loki → Tempo correlation
jsonData:
  derivedFields:
    - datasourceUid: tempo
      matcherRegex: '"traceId":"([a-f0-9]+)"'
      name: TraceID
      url: "$${__value.raw}"
```

### Zipkin

**Zipkin** is one of the earliest distributed tracing systems, inspired by Google's Dapper paper. It remains widely deployed in Java ecosystems (Spring Boot has built-in Zipkin integration via Spring Cloud Sleuth / Micrometer Tracing).

#### Integration with Spring Boot

```yaml
# application.yml
management:
  tracing:
    sampling:
      probability: 0.1      # 10% sample rate
  zipkin:
    tracing:
      endpoint: http://zipkin:9411/api/v2/spans
```

### Datadog

**Datadog** is a commercial observability platform that unifies metrics, logs, and APM traces under one SaaS product. It provides:

- **Agent**: Lightweight collector installed on hosts/containers that ships all three signal types.
- **APM**: Auto-instrumentation for common frameworks with flame graphs and service maps.
- **Dashboards**: Drag-and-drop dashboards with out-of-the-box integrations for 700+ technologies.
- **Log Management**: Full-text search, anomaly detection, and log-to-trace correlation.
- **Alerting**: Composite monitors, anomaly detection, and forecasting.

```bash
# Install Datadog agent on a Linux host
DD_API_KEY=<your_api_key> DD_SITE="datadoghq.com" \
  bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"

# Enable APM and log collection
datadog-agent config set apm_config.enabled true
datadog-agent config set logs_config.enabled true
```

### Comparing the Tools

| Tool | Primary Signal | License | Storage | Best For |
|------|---------------|---------|---------|----------|
| Prometheus | Metrics | Apache 2 | Local TSDB | Kubernetes-native alerting |
| Grafana | Visualization | AGPL 3 | None (queries others) | Unified dashboards |
| Jaeger | Traces | Apache 2 | Cassandra / ES / Badger | Microservice tracing |
| Tempo | Traces | AGPL 3 | Object store | Low-cost trace storage |
| Loki | Logs | AGPL 3 | Object store | Prometheus-style log queries |
| Zipkin | Traces | Apache 2 | In-memory / MySQL / ES | Java/Spring ecosystems |
| ClickHouse | Logs / Metrics | Apache 2 | Columnar on-disk | Analytical queries at scale |
| Perf / eBPF | CPU / Kernel | GPL 2 | `perf.data` | On-host CPU profiling |
| OpenTelemetry | All three | Apache 2 | Collector (forwards) | Vendor-neutral instrumentation |
| Datadog | All three | Commercial | Datadog SaaS | Turnkey enterprise observability |

### Reference Architecture

A common production observability stack integrates many of these tools together:

```
+---------------------------+
|  Applications / Services  |
|  (OTel SDK instrumented)  |
+-----------+---------------+
            |
            | OTLP (gRPC / HTTP)
            v
+-----------+---------------+
|   OTel Collector          |
|   (receive / filter /     |
|    batch / export)        |
+-+-----------+-----------+-+
  |           |           |
  | Prom      | OTLP      | OTLP
  | remote    | traces    | logs
  v           v           v
+--------+ +--------+ +--------+
|Prom    | |Tempo   | |Loki    |
|(TSDB)  | |(traces)| |(logs)  |
+---+----+ +---+----+ +---+----+
    |           |           |
    +-----------+-----------+
                |
                v
         +------+------+
         |   Grafana   |
         | (dashboards |
         |   alerts)   |
         +-------------+
```

For high-volume log analytics with long-term retention, ClickHouse can replace or complement Loki in the stack by providing richer SQL-based querying:

```
                  Kafka (log stream)
                       |
              +--------+--------+
              |                 |
              v                 v
           Loki           ClickHouse
        (short-term     (long-term analytics
         live search)    and historical queries)
```

### Best Practices and Recommendations

1. **Instrument once, export everywhere**: Use OpenTelemetry as the instrumentation layer so you can swap backends without re-instrumenting services.
2. **Start with RED metrics**: Track **R**ate, **E**rrors, and **D**uration for every service boundary. Add USE (Utilization, Saturation, Errors) for infrastructure nodes.
3. **Capture the Right Granularity**: Overly detailed metrics can overwhelm storage, but too coarse metrics hide issues. Start with endpoint-level latencies, throughput, and error rates.
4. **Measure Tail Latencies**: Focus on p95 or p99 to ensure outliers are not ignored.
5. **Correlate signals**: Ensure log lines carry `trace_id` and `span_id` fields so you can jump from a metric anomaly to the trace and then to the logs.
6. **Define SLOs before dashboards**: Decide on error budget targets (e.g., 99.9% success rate) before building dashboards; build dashboards to track SLO burn rate, not just raw metrics.
7. **Sample traces thoughtfully**: 100% trace capture is expensive. Use head-based sampling at low rates (1–10%) with tail-based sampling to always capture errors and slow outliers.
8. **Use ClickHouse for analytics, not operational monitoring**: ClickHouse excels at historical aggregations and trends. Route real-time alerting through Prometheus/Grafana.
9. **Profile before optimizing**: Use `perf record` or eBPF-based tools to generate flame graphs before assuming where CPU bottlenecks are.
10. **Set data retention policies**: Metrics rarely need more than 1–2 years; logs rarely need more than 30–90 days. Use MergeTree TTLs (ClickHouse) or Prometheus retention flags to enforce limits automatically.
11. **Avoid high-cardinality labels**: Labels like `user_id` or `request_id` in Prometheus explode the number of time series and degrade performance. Use traces or logs for per-request data.
12. **Automate Alerts**: Set up threshold-based or anomaly-based alerts for critical metrics (e.g., 5xx rate spikes, high latencies).
13. **Test your alerting pipeline**: Regularly fire synthetic alerts to verify that the full path (Prometheus → Alertmanager → PagerDuty/Slack) actually works.
14. **Plan for Scale**: As systems grow, you will need a robust architecture for metric collection and storage.
15. **Stress and Chaos Testing**: Explore system limits and resiliency under adverse conditions (random instance termination, network partition).
