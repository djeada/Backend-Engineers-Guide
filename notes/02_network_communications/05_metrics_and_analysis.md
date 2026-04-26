## Metrics and Analysis

In modern distributed systems, the performance and reliability of communication channels, APIs, and network infrastructure directly affect user experience. A user may not know whether a delay comes from a database, an overloaded API server, packet loss, or a slow dependency, but they will notice that the application feels slow or unreliable.

Metrics and analysis help teams understand what is happening inside a system. Instead of guessing, developers and operators can measure latency, throughput, errors, resource usage, network behavior, and availability. These measurements make it easier to identify bottlenecks, plan capacity, and detect failures before they become major incidents.

Good metrics are especially important in distributed systems because a single user request may pass through many components. For example, a request might travel from a browser to a CDN, then to a load balancer, then to an API server, then to a database, cache, or another backend service. Each stage can introduce latency or failure, so each stage should be observable.

### Why Metrics Matter

Metrics matter because they turn system behavior into measurable data. Without metrics, teams may rely on user complaints, manual testing, or assumptions. With metrics, teams can see trends, compare performance before and after changes, and respond to issues more quickly.

Metrics are also useful for long-term planning. If traffic is growing by 20% each month, historical metrics can help predict when additional servers, database capacity, or network bandwidth will be needed. Metrics also help teams decide whether optimization work is actually improving the system.

Metrics support several important activities:

1. **Troubleshooting**: Pinpointing which service, endpoint, database query, or network segment is causing latency spikes or errors.
2. **Capacity Planning**: Predicting future infrastructure needs based on historical load and growth patterns.
3. **Service-Level Objectives**: Establishing performance and reliability targets and checking whether the service meets them.
4. **Trend Analysis**: Detecting gradual degradation before it becomes a visible outage.

Example monitoring snapshot:

```json
{
  "service": "orders-api",
  "requestsPerSecond": 850,
  "p95LatencyMs": 180,
  "p99LatencyMs": 420,
  "errorRate": "0.6%",
  "cpuUsage": "71%",
  "memoryUsage": "64%"
}
```

This output shows a quick view of service health. The service is handling `850` requests per second, most requests are reasonably fast, and the error rate is under 1%. If the p99 latency or error rate suddenly increases, operators can investigate before the issue affects many users.

### Common Terminology and Formulas

Metrics are easier to interpret when the main terms are clearly defined. Backend and network monitoring often focuses on latency, throughput, concurrency, error rates, availability, and packet loss.

These terms are related but not identical. A system can have high throughput but poor latency. It can have low average latency but bad p99 latency. It can also appear healthy at the API layer while experiencing network packet loss or database saturation underneath.

#### Latency and Response Times

**Latency** is the amount of time it takes for a request to travel from a client to a server and for the server to respond. It often includes network travel time, load balancer time, queueing delay, application processing time, database calls, and response transmission time.

Latency is usually measured in milliseconds. Instead of looking only at the average, teams often track percentiles because averages can hide bad user experiences.

* **p50**, or median latency, means half of requests complete below this value.
* **p95** means 95% of requests complete below this value.
* **p99** means 99% of requests complete below this value.
* **p100**, or max latency, is the slowest observed request, though it can be noisy and affected by rare outliers.

A simplified latency equation for an HTTP request might be:

```text
Total_Latency = RTT_network + Server_Processing_Time + Possible_Queueing_Delay
```

Example calculation:

```text
RTT_network = 40ms
Server_Processing_Time = 80ms
Possible_Queueing_Delay = 20ms

Total_Latency = 40ms + 80ms + 20ms
Total_Latency = 140ms
```

Example output:

```json
{
  "totalLatencyMs": 140,
  "networkRttMs": 40,
  "serverProcessingMs": 80,
  "queueingDelayMs": 20
}
```

This example shows that latency is not caused by only one thing. Even if the application code is fast, network delay or queueing can still make the total response time feel slow.

Percentiles help reveal tail latency. For example:

```json
{
  "endpoint": "GET /api/orders",
  "p50LatencyMs": 65,
  "p95LatencyMs": 220,
  "p99LatencyMs": 700
}
```

This means most users get a fast response, but the slowest 1% of requests are much slower. That may indicate database contention, garbage collection pauses, overloaded dependencies, or network instability.

#### Throughput and Requests per Second

**Throughput** measures how much work a system completes in a given time. For APIs, this is often shown as requests per second, or RPS. For databases, it may be queries per second, or QPS. For messaging systems, it may be messages per second.

If `N_req` is the total number of requests during a measurement window `T`, throughput can be approximated as:

```text
Throughput = N_req / T
```

Example calculation:

```text
N_req = 12,000 requests
T = 60 seconds

Throughput = 12,000 / 60
Throughput = 200 requests per second
```

Example output:

```json
{
  "requests": 12000,
  "windowSeconds": 60,
  "throughputRps": 200
}
```

Throughput is useful for understanding load. If throughput rises while latency remains stable, the system is handling growth well. If throughput rises and latency increases sharply, the system may be nearing a bottleneck.

Example throughput trend:

```json
{
  "09:00": { "rps": 250, "p95LatencyMs": 120 },
  "10:00": { "rps": 500, "p95LatencyMs": 160 },
  "11:00": { "rps": 900, "p95LatencyMs": 480 }
}
```

This suggests that the system starts to degrade as traffic approaches `900` requests per second.

#### Concurrency

**Concurrency** measures how many requests, jobs, streams, or connections are active at the same time. A system may have low throughput but high concurrency if requests stay open for a long time. WebSockets, streaming APIs, long-polling, and slow database queries can all increase concurrency.

Concurrency is important because each active request or connection consumes resources. These resources may include memory, file descriptors, threads, database connections, CPU time, or network buffers.

Example concurrency snapshot:

```json
{
  "activeHttpRequests": 320,
  "openWebSocketConnections": 18500,
  "activeDatabaseConnections": 78,
  "workerThreadsBusy": 145
}
```

This output shows several forms of concurrency. The service may be handling only a few hundred active HTTP requests, but it is also maintaining thousands of WebSocket connections. That has memory and infrastructure implications.

A simple concurrency relationship can be described as:

```text
Concurrency ≈ Throughput * Average_Request_Duration
```

Example calculation:

```text
Throughput = 500 requests/second
Average_Request_Duration = 0.2 seconds

Concurrency ≈ 500 * 0.2
Concurrency ≈ 100 in-flight requests
```

Example output:

```json
{
  "estimatedInFlightRequests": 100
}
```

If request duration increases, concurrency also increases even if traffic stays the same. This is one reason slow dependencies can quickly overload a system.

#### Error Rates

Error rates show how often requests fail. They can be measured overall or separated by category. HTTP APIs often separate `4xx` and `5xx` responses because they usually mean different things.

* **4xx errors** usually indicate client-side problems, such as invalid input, missing authentication, forbidden access, or not found resources.
* **5xx errors** usually indicate server-side problems, such as crashes, dependency failures, timeouts, or overload.
* **Overall error rate** measures all failed responses compared with total requests.

Formula:

```text
Overall_Error_Rate = Number_of_Error_Responses / Total_Requests
```

Example calculation:

```text
Number_of_Error_Responses = 75
Total_Requests = 10,000

Overall_Error_Rate = 75 / 10,000
Overall_Error_Rate = 0.0075
Overall_Error_Rate = 0.75%
```

Example output:

```json
{
  "totalRequests": 10000,
  "errorResponses": 75,
  "overallErrorRate": "0.75%"
}
```

A sudden increase in `5xx` errors is often more urgent than a rise in `404` errors. For example:

```json
{
  "2xx": 9400,
  "4xx": 520,
  "5xx": 80
}
```

This response distribution shows that most requests succeed, but some client and server errors are occurring. If the `5xx` count grows quickly, it may indicate an outage or dependency issue.

#### Uptime and Availability

**Availability** measures how much time a service is operational and able to serve requests successfully. It is usually expressed as a percentage.

Formula:

```text
Availability (%) = 100 * (Uptime / Total_Time)
```

Example calculation:

```text
Uptime = 43,170 minutes
Total_Time = 43,200 minutes

Availability = 100 * (43,170 / 43,200)
Availability ≈ 99.93%
```

Example output:

```json
{
  "uptimeMinutes": 43170,
  "totalMinutes": 43200,
  "availability": "99.93%"
}
```

Availability is often connected to SLOs, or Service-Level Objectives. A service might have an SLO of 99.9% availability, meaning it can be unavailable for only a limited amount of time during a measurement period.

Example monthly availability targets:

```text
99.9% availability  ≈ 43.2 minutes of downtime per 30-day month
99.99% availability ≈ 4.32 minutes of downtime per 30-day month
```

Example output:

```json
{
  "slo": "99.9%",
  "allowedDowntimePerMonth": "about 43.2 minutes"
}
```

Higher availability targets require more resilient architecture, better monitoring, failover, redundancy, and operational discipline.

#### Packet Loss and Network Metrics

At the network layer, packet loss, retransmissions, jitter, and bandwidth utilization can strongly affect application performance. These metrics are especially important for TCP, UDP, streaming, real-time communication, and high-throughput services.

Packet loss happens when packets are sent but never reach their destination. TCP may recover by retransmitting lost packets, but this increases latency and can reduce throughput. UDP does not retransmit by default, so packet loss may directly affect application quality.

Formula:

```text
Packet_Loss_Rate = (Packets_Lost / Packets_Sent) * 100
```

Example calculation:

```text
Packets_Sent = 100,000
Packets_Lost = 500

Packet_Loss_Rate = (500 / 100,000) * 100
Packet_Loss_Rate = 0.5%
```

Example output:

```json
{
  "packetsSent": 100000,
  "packetsLost": 500,
  "packetLossRate": "0.5%"
}
```

A packet loss rate that seems small can still be harmful for latency-sensitive systems. For video calls, gaming, or live dashboards, even small amounts of loss or jitter can reduce quality.

Example network health snapshot:

```json
{
  "rttMs": 35,
  "packetLossRate": "0.2%",
  "jitterMs": 8,
  "bandwidthUtilization": "72%"
}
```

This output suggests the network is mostly healthy, though teams should watch utilization and jitter if real-time traffic is involved.

### Metrics for APIs

API metrics help teams understand how clients are using the system and how well the system is responding. They also help reveal whether problems are happening at the API layer, application layer, database layer, cache layer, or network layer.

Good API metrics are usually broken down by endpoint, method, status code, region, client type, and service version. Aggregated metrics are useful, but detailed labels help identify the exact source of problems.

#### HTTP/RESTful APIs

RESTful services usually expose multiple endpoints, each with different behavior and performance characteristics. A `GET /posts` endpoint may be fast and cacheable, while a `POST /orders` endpoint may involve validation, payment processing, inventory checks, and database writes.

Typical REST API metrics include:

1. **Request latencies** by endpoint and method.
2. **Request throughput** in requests per second or per minute.
3. **Response code distribution** across `2xx`, `4xx`, and `5xx`.
4. **Payload sizes** for requests and responses.
5. **Caching metrics**, such as cache hit rate and miss rate.

```text
Client (Browser/App) ----> [Load Balancer] ----> [API Server(s)] ----> [Database/Cache]
     |                        |                       |                      |
     | metrics??              | metrics??             | metrics??            | metrics??
     v                        v                       v                      v

Logging & Monitoring Infrastructure (e.g., Prometheus, Grafana, ELK stack)
```

Example REST metrics:

```json
{
  "endpoint": "GET /api/posts",
  "rps": 420,
  "p50LatencyMs": 45,
  "p95LatencyMs": 130,
  "p99LatencyMs": 310,
  "statusCodes": {
    "2xx": 9820,
    "4xx": 140,
    "5xx": 40
  },
  "averageResponseBytes": 2450,
  "cacheHitRate": "68%"
}
```

This output shows that the endpoint is mostly successful, with a low number of server errors. The cache hit rate is high, which likely reduces load on the API server and database.

If latency increases, teams can inspect each stage. The load balancer may show queueing, the API server may show CPU pressure, or the database may show slow queries.

#### GraphQL APIs

GraphQL APIs need many of the same metrics as REST APIs, but they also require query-specific and resolver-specific visibility. Because many GraphQL requests go to the same endpoint, such as `/graphql`, endpoint-level metrics alone are not enough.

Important GraphQL metrics include:

1. **Resolver latencies**, to identify slow fields.
2. **Field usage**, to understand which schema fields clients use most often.
3. **Query depth and complexity**, to detect expensive or abusive queries.
4. **Operation names**, to track performance by named query or mutation.
5. **Error rates by resolver**, to identify failing backend paths.

Example GraphQL metrics:

```json
{
  "operationName": "GetBookDetails",
  "totalLatencyMs": 185,
  "queryDepth": 4,
  "complexityScore": 27,
  "resolverLatenciesMs": {
    "Query.book": 20,
    "Book.author": 35,
    "Book.reviews": 95,
    "Review.user": 25
  }
}
```

This output shows that `Book.reviews` is the slowest resolver. Optimization work should probably begin there, perhaps by batching database calls, adding indexes, or using DataLoader.

Example field usage output:

```json
{
  "mostUsedFields": [
    { "field": "Book.title", "count": 120000 },
    { "field": "Book.author", "count": 98000 },
    { "field": "Book.reviews", "count": 43000 }
  ]
}
```

Field usage helps schema owners understand which fields are important and which deprecated fields are still being used.

#### gRPC

gRPC metrics are usually organized by service and method. Since gRPC uses HTTP/2 and Protocol Buffers, teams often monitor both RPC-level behavior and transport-level behavior.

Important gRPC metrics include:

1. **RPC latency** per method.
2. **Inbound and outbound traffic** in bytes.
3. **Status code distribution**, such as `OK`, `UNAVAILABLE`, or `DEADLINE_EXCEEDED`.
4. **Deadline or timeout exceeded events**.
5. **Streaming metrics**, such as stream duration, messages sent, and messages received.

Example gRPC metrics:

```json
{
  "service": "bookstore.Bookstore",
  "method": "GetBook",
  "callsPerSecond": 350,
  "p95LatencyMs": 40,
  "statusCodes": {
    "OK": 9870,
    "NOT_FOUND": 90,
    "DEADLINE_EXCEEDED": 12,
    "UNAVAILABLE": 4
  },
  "inboundBytesPerSecond": 18000,
  "outboundBytesPerSecond": 92000
}
```

This output shows that most calls succeed. A small number of deadline failures may indicate slow downstream dependencies or overly aggressive deadlines.

Example streaming metrics:

```json
{
  "method": "ListBooks",
  "activeStreams": 38,
  "averageStreamDurationSeconds": 12.5,
  "messagesSentPerSecond": 1600,
  "streamErrors": 3
}
```

Streaming metrics are important because long-lived streams behave differently from short request-response calls. A service may have low call volume but still maintain many active streams.

### Network-Level Metrics

Network-level metrics help explain performance problems that application metrics may not fully capture. If an API has high latency, the cause may not be the application code. It could be packet loss, high RTT, retransmissions, saturated links, DNS delays, or unstable routing.

Backend teams often monitor network metrics alongside application metrics so they can separate application bottlenecks from infrastructure or network problems.

#### TCP Metrics

TCP provides reliable delivery, but reliability comes with behavior that can affect performance. When packets are lost, TCP retransmits them. When congestion is detected, TCP may reduce its sending rate. These mechanisms protect the network, but they can increase latency or reduce throughput.

Important TCP metrics include:

* **RTT**, or round-trip time, which measures how long it takes for data to travel to the peer and for an acknowledgment to return.
* **Window size**, especially the congestion window, which affects how much data can be in flight.
* **Retransmissions**, which indicate packet loss, congestion, or unstable links.
* **Connection resets**, which may indicate client disconnects, server errors, or network interruptions.

Example TCP metrics:

```json
{
  "rttMs": 48,
  "tcpRetransmissionsPerSecond": 12,
  "connectionResetsPerMinute": 4,
  "congestionWindowBytes": 65535
}
```

This output indicates moderate latency and some retransmissions. If retransmissions spike, the application may experience slower responses even if the server is healthy.

Example problem signal:

```json
{
  "rttMs": 220,
  "tcpRetransmissionsPerSecond": 900,
  "apiP95LatencyMs": 1400
}
```

This suggests that network conditions may be contributing to high API latency.

#### UDP Metrics

UDP does not provide built-in retransmission, ordering, or congestion control. This makes UDP useful for low-latency traffic, but it also means applications need to monitor packet loss and timing more carefully.

Important UDP metrics include:

* **Packet loss**, especially for streaming and real-time communication.
* **Jitter**, which measures variation in packet arrival times.
* **Datagram throughput**, or how many datagrams are handled per second.
* **Out-of-order packets**, if the application tracks sequence numbers.

Example UDP metrics:

```json
{
  "datagramsPerSecond": 12000,
  "packetLossRate": "1.2%",
  "jitterMs": 18,
  "outOfOrderPacketsPerMinute": 42
}
```

For a real-time voice or video system, jitter and packet loss may matter more than raw throughput. A small amount of packet loss may be tolerable, but high jitter can cause audio gaps, video stutter, or delayed game updates.

Example real-time quality output:

```json
{
  "callQuality": "degraded",
  "packetLossRate": "3.8%",
  "jitterMs": 45,
  "recommendation": "reduce bitrate or switch network path"
}
```

This output shows how network metrics can be translated into operational decisions.

#### Bandwidth and Utilization

**Bandwidth** is the theoretical maximum data rate of a link. **Utilization** measures how much of that capacity is currently being used. High utilization can lead to increased latency, queueing, packet drops, and degraded user experience.

For example, a network link may support 1 Gbps, but if traffic consistently reaches 950 Mbps, the system may be close to saturation.

Formula:

```text
Utilization (%) = 100 * (Current_Throughput / Link_Capacity)
```

Example calculation:

```text
Current_Throughput = 750 Mbps
Link_Capacity = 1000 Mbps

Utilization = 100 * (750 / 1000)
Utilization = 75%
```

Example output:

```json
{
  "currentThroughputMbps": 750,
  "linkCapacityMbps": 1000,
  "utilization": "75%"
}
```

High utilization does not always mean there is a problem, but sustained high utilization can reduce headroom. If traffic spikes suddenly, the link may become saturated.

Example saturation warning:

```json
{
  "linkCapacityMbps": 1000,
  "currentThroughputMbps": 970,
  "utilization": "97%",
  "risk": "increased latency and packet drops"
}
```

This output indicates that the network is close to capacity. Teams may need to add bandwidth, reduce payload sizes, improve caching, enable compression, or shift traffic to other regions.

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

1. Instrument your services once in a flexible way so you can switch monitoring tools later without redoing everything, for example by using OpenTelemetry.
2. Start with the basics: track how often requests happen, how many fail, and how long they take; for infrastructure also watch how busy systems are and whether they’re overloaded.
3. Keep your metrics at a useful level of detail—too much becomes noisy, too little hides issues; a good starting point is endpoint-level performance, traffic, and errors.
4. Don’t rely on averages alone; pay attention to slower edge cases like the 95th or 99th percentile so you catch real user pain.
5. Make sure logs, metrics, and traces are connected so you can quickly move from a problem to its root cause.
6. Decide on reliability goals (like a target success rate) before building dashboards, and design dashboards to show how close you are to missing those goals.
7. Be smart about tracing: capturing everything is expensive, so collect a small sample but always keep errors and slow requests.
8. Use tools like ClickHouse for analyzing historical trends, but rely on systems like Prometheus and Grafana for real-time monitoring and alerts.
9. Measure performance before trying to optimize—use profiling tools to find actual bottlenecks instead of guessing.
10. Set clear data retention rules so metrics and logs don’t grow forever; keep only what’s useful.
11. Avoid adding too many unique labels (like user IDs) to metrics because they can overload your monitoring system; use logs or traces for that level of detail instead.
12. Set up automatic alerts for important issues like spikes in errors or slow responses.
13. Regularly test your alerting setup to make sure notifications actually reach you when something breaks.
14. Plan ahead for growth so your monitoring system can handle more data as your system scales.
15. Test how your system behaves under stress and failure scenarios to understand its limits and improve resilience.

