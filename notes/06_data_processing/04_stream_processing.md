## Stream Processing

Stream processing involves ingesting, analyzing, and acting on data **as it is produced**. Instead of waiting for a complete batch of data to be collected, a stream processing system handles events continuously as they arrive.

This approach is useful when applications need quick responses to constantly changing information. Examples include IoT sensor readings, financial transactions, application logs, user activity events, clickstreams, social media activity, and monitoring data.

Stream processing can generate alerts, update dashboards, enrich records, detect fraud, synchronize databases, or trigger automated workflows with minimal delay.

```text id="73bkhx"
ASCII DIAGRAM: Stream Processing Overview

+---------------+      +---------------------------------+      +--------------+
|               |      | Stream Processing               |      |              |
| Data Sources  +----->+    Real-time/Near-real-time     +----->+ Final Output |
| Sensors, etc. |      |   +-----+   +-----+   +-----+   |      | Dashboard,  |
+---------------+      |   | P1  |   | P2  |   | P3  |   |      | Alerts, etc.|
                       +----+-----+---+-----+---+-----+---+      +--------------+
```

Example incoming event:

```json id="giiudw"
{
  "deviceId": "sensor-17",
  "temperature": 82.4,
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Example processed output:

```json id="p3dbz1"
{
  "deviceId": "sensor-17",
  "temperature": 82.4,
  "status": "warning",
  "alert": "Temperature exceeded threshold"
}
```

A data stream is continuously produced by sources such as logs, sensors, transactions, or user actions. A stream processing system consumes these events, applies transformations or calculations, and emits results such as alerts, metrics, enriched records, or dashboard updates.

---

### Message Brokers

Message brokers provide asynchronous communication between services. Producers send messages to the broker, and consumers read messages from the broker. This makes systems more flexible because producers and consumers do not need to communicate directly with each other.

In stream processing, message brokers often act as the backbone of the pipeline. They buffer events, route messages, support multiple consumers, and help systems continue operating even when one component is temporarily slow or unavailable.

Common broker capabilities include:

* **Load Balancing**: Distributes messages across multiple consumers.
* **Fan-out**: Sends a copy of each message to multiple subscribers.
* **Queue vs. Pub-Sub**: A queue usually delivers each message to one consumer, while pub-sub delivers messages to multiple subscribers.

```text id="qwpz7a"
ASCII DIAGRAM: Message Broker in the Pipeline

  Publisher(s)             Message Broker           Consumer(s)
+------------+     Push      +-----------+     Pull  +------------+
|  Service A |  ---------->  |   Topic   |  <------- |  Service B |
+------------+               +-----+-----+           +------------+
                                     \
                                      +------------+
                                      | Service C  |
                                      +------------+
```

Example published message:

```json id="ey4ny9"
{
  "eventType": "OrderCreated",
  "orderId": "order-123",
  "userId": "user-456",
  "amount": 79.99
}
```

Example consumer output:

```json id="zjakqs"
{
  "consumer": "billing-service",
  "eventReceived": "OrderCreated",
  "orderId": "order-123",
  "action": "created_invoice"
}
```

In this example, one service publishes an `OrderCreated` event. Other services can consume the event and react independently. A billing service might create an invoice, an analytics service might update revenue metrics, and a notification service might send a confirmation email.

This design reduces direct coupling between services. The producer does not need to know which consumers exist or what they will do with the message.

---

### Log-Based Message Brokers

Log-based brokers, such as Apache Kafka, store messages in an immutable, append-only log. Instead of removing a message immediately after it is consumed, the broker keeps messages for a configured retention period.

Consumers track their own position in the log using an **offset**. This allows consumers to replay messages, recover after failures, or process the same stream at different speeds.

```text id="qrjt7t"
ASCII DIAGRAM: Log-Based Broker Conceptual View

               +-------------+
Producer --->  | Partition 0 | ---> Consumer Group 1
               +-------------+
Producer --->  | Partition 1 | ---> Consumer Group 2
               +-------------+
Producer --->  | Partition 2 | ---> Consumer Group 2
               +-------------+
```

Example topic events:

```json id="eo3rkd"
[
  {
    "offset": 100,
    "eventType": "UserSignedUp",
    "userId": "user-1"
  },
  {
    "offset": 101,
    "eventType": "UserSignedUp",
    "userId": "user-2"
  },
  {
    "offset": 102,
    "eventType": "UserSignedUp",
    "userId": "user-3"
  }
]
```

Example consumer offset output:

```json id="aq36hl"
{
  "consumerGroup": "analytics-service",
  "topic": "user-events",
  "partition": 0,
  "currentOffset": 102,
  "status": "caught_up"
}
```

Each partition is independent. Reading from one partition does not affect offsets in another partition. If a consumer fails, another consumer in the same group can take over and continue from the last committed offset.

Partitioning also improves scalability. A high-volume topic can be split across multiple partitions, allowing multiple consumers to process events in parallel.

---

### Change Data Capture

Change Data Capture, or **CDC**, captures row-level database changes and turns them into events. Instead of polling a database repeatedly to find out what changed, a CDC system reads the database’s transaction log, binlog, or write-ahead log and emits changes as a stream.

CDC is useful for synchronizing data across systems. For example, a change in the main database can update a search index, cache, analytics platform, audit log, or downstream microservice.

```text id="yznf92"
ASCII DIAGRAM: CDC Flow

   Database            CDC Engine                Message Broker               Consumers
+------------+   +---------------+           +---------------+          +-----------------+
|  Table(s)  |-->| Binlog Reader | --------> |   Topic(s)    |  ----->  | Microservices  |
+------------+   +---------------+           +-------+-------+          +-----------------+
                                                    |
                                                    v
                                             +---------------+
                                             |   Analytics   |
                                             +---------------+
```

Example database change:

```sql id="wiafjk"
UPDATE users
SET email = 'alice.new@example.com'
WHERE id = 123;
```

Example CDC event:

```json id="62jjrs"
{
  "operation": "update",
  "table": "users",
  "before": {
    "id": 123,
    "email": "alice@example.com"
  },
  "after": {
    "id": 123,
    "email": "alice.new@example.com"
  },
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Example downstream output:

```json id="1jeq0m"
{
  "consumer": "search-indexer",
  "action": "updated_user_document",
  "userId": 123,
  "newEmail": "alice.new@example.com"
}
```

CDC is especially helpful when systems need near-real-time synchronization without placing heavy query load on the source database. It is commonly used for read replicas, caches, search indexes, event-driven microservices, and analytics pipelines.

---

### Event Sourcing

Event sourcing stores every state change as an event instead of storing only the latest state. The event log becomes the source of truth. The current state is reconstructed by replaying events in order.

This approach is useful when auditability and history are important. Instead of only knowing that an account balance is currently `120`, the system knows every deposit, withdrawal, transfer, or correction that led to that balance.

Example event log:

```json id="zlikfw"
[
  {
    "eventType": "AccountOpened",
    "accountId": "acct-1",
    "initialBalance": 0
  },
  {
    "eventType": "MoneyDeposited",
    "accountId": "acct-1",
    "amount": 100
  },
  {
    "eventType": "MoneyWithdrawn",
    "accountId": "acct-1",
    "amount": 30
  }
]
```

Example reconstructed state:

```json id="4a123d"
{
  "accountId": "acct-1",
  "currentBalance": 70
}
```

The current balance is reconstructed by replaying all events in order. The application does not simply overwrite the account record; it appends a new event for each change.

Event sourcing provides strong audit trails and makes debugging easier because developers can inspect exactly how state changed over time. However, it also adds complexity. Systems may need snapshots, event versioning, replay tools, and careful handling of schema changes.

---

### Streams and Time

Time management is one of the most important parts of stream processing. Events may arrive late, out of order, or with timestamps from different machines. Network delays, retries, clock drift, and batching can all affect when events are processed.

Stream systems often use windows to group events over time. A window defines the time range used for aggregation, counting, joining, or alerting.

There are several common windowing strategies.

---

#### 1. Hopping Windows

A hopping window has a fixed size and a fixed hop interval. If the hop interval is larger than the window size, there are gaps between windows. If the hop interval is smaller than the window size, windows overlap.

In the notes here, the example uses a 6-minute window with a 10-minute hop, creating gaps.

```text id="386tcj"
Hopping Window Size = 6 minutes
Hop = 10 minutes

[0---6]             [10--16]            [20--26]
```

Example input events:

```json id="86nkey"
[
  { "timestampMinute": 1, "value": 10 },
  { "timestampMinute": 3, "value": 20 },
  { "timestampMinute": 11, "value": 5 }
]
```

Example window output:

```json id="57x5ti"
[
  {
    "window": "0-6",
    "sum": 30
  },
  {
    "window": "10-16",
    "sum": 5
  }
]
```

Events that fall outside the active windows may not be included, depending on the configuration.

---

#### 2. Sliding Windows

Sliding windows overlap. Each window covers a fixed duration, but new windows start at smaller intervals. This allows more continuous analysis.

```text id="9nc5m4"
Sliding Window Size = 6 minutes
Slide = 2 minutes

[0---6]
   [2---8]
      [4---10]
         [6---12]
```

Example input events:

```json id="s8zf79"
[
  { "timestampMinute": 2, "value": 10 },
  { "timestampMinute": 4, "value": 20 },
  { "timestampMinute": 6, "value": 30 }
]
```

Example window output:

```json id="fgu5h8"
[
  {
    "window": "0-6",
    "sum": 30
  },
  {
    "window": "2-8",
    "sum": 60
  },
  {
    "window": "4-10",
    "sum": 50
  }
]
```

Sliding windows are useful when applications need smooth, continuous metrics, such as moving averages or rolling counts.

---

#### 3. Tumbling Windows

Tumbling windows are fixed-size, consecutive, non-overlapping windows. Every event belongs to exactly one window.

```text id="whrny1"
Tumbling Window Size = 6 minutes

[0---6][6---12][12--18][18--24]
```

Example input events:

```json id="z809mk"
[
  { "timestampMinute": 1, "value": 10 },
  { "timestampMinute": 4, "value": 20 },
  { "timestampMinute": 7, "value": 5 }
]
```

Example window output:

```json id="w5nl8m"
[
  {
    "window": "0-6",
    "sum": 30
  },
  {
    "window": "6-12",
    "sum": 5
  }
]
```

Tumbling windows are simple and common for metrics such as “events per minute,” “orders per hour,” or “errors per 5-minute interval.”

---

### Stream Joins

Stream joins combine data from multiple sources. They allow systems to correlate events, enrich records, or connect real-time activity with reference data.

For example, an order stream may need to be joined with a payment stream to detect whether an order was paid. A clickstream may be joined with a user profile table to enrich events with user region or subscription tier.

Common join types include:

* **Stream-Stream Join**: Joins events from two live streams within a time window.
* **Stream-Table Join**: Joins a live stream with a static or slowly changing table.
* **Table-Table Join**: Joins two changing datasets, often maintained through CDC or event sourcing.

```text id="9pnq8p"
ASCII DIAGRAM: Stream-Stream Join Conceptual View

Stream A Orders          Join on OrderID          Stream B Payments
     A1  ------------------>  +--------------+  <---------------- B1
     A2  ------------------>  |  Join State  |  <---------------- B2
     A3  ------------------>  +--------------+  <---------------- B3
```

Example order event:

```json id="w8uo2b"
{
  "eventType": "OrderCreated",
  "orderId": "order-123",
  "userId": "user-456",
  "amount": 79.99,
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Example payment event:

```json id="49da3a"
{
  "eventType": "PaymentReceived",
  "orderId": "order-123",
  "paymentId": "pay-999",
  "amount": 79.99,
  "timestamp": "2026-04-25T12:00:05Z"
}
```

Example joined output:

```json id="odzwvy"
{
  "orderId": "order-123",
  "userId": "user-456",
  "orderAmount": 79.99,
  "paymentId": "pay-999",
  "paymentStatus": "paid"
}
```

Stream-stream joins require intermediate state because one side may arrive before the other. The processor must temporarily store unmatched events until the matching event arrives or the join window expires.

---

### Fault Tolerance

Fault tolerance ensures that stream processing continues correctly when machines, networks, or services fail. This is critical because stream systems often process continuous business events that cannot simply be lost.

Common fault-tolerance techniques include:

* **Micro-batching**: Groups short spans of stream data into small batches, making recovery easier.
* **Checkpointing**: Periodically saves offsets and processing state to durable storage.
* **Idempotent operations**: Allows events to be processed again without duplicating side effects.

```text id="6gmovg"
ASCII DIAGRAM: Checkpointing Example

        Stream
          |
          v
+---------+---------+
| Stream Processing |
+---------+---------+
          |
          | Periodic Save State
          v
+------------------+
|  Checkpoint Store|
+------------------+
```

Example checkpoint:

```json id="0hrgyb"
{
  "job": "fraud-detector",
  "topic": "transactions",
  "partition": 3,
  "lastProcessedOffset": 982341,
  "stateSnapshot": "s3://checkpoints/fraud-detector/982341"
}
```

Example recovery output:

```json id="qaq3ju"
{
  "job": "fraud-detector",
  "recoveredFromOffset": 982341,
  "eventsReplayed": 128,
  "status": "running"
}
```

When a node fails, the stream processor can restart from the latest checkpoint and replay only the events that happened after that point. This reduces data loss and avoids starting over from the beginning.

Idempotency is also important. If a processor replays an event, it should not accidentally charge a customer twice, send duplicate emails, or create duplicate records.

Example idempotent output:

```json id="t1xcta"
{
  "eventId": "evt-123",
  "status": "already_processed",
  "sideEffectRepeated": false
}
```

## Stream Processing Technologies

Many tools support stream processing, but they differ in architecture, latency, state management, deployment complexity, and ecosystem.

### Apache Kafka

Apache Kafka is a widely used log-based message broker. It stores events in topics and partitions, supports consumer groups, and provides replay through offsets. Kafka Streams and ksqlDB can be used to process Kafka topics directly.

Example Kafka-style event:

```json id="kzpbwa"
{
  "topic": "orders",
  "partition": 2,
  "offset": 45122,
  "eventType": "OrderCreated"
}
```

Kafka is commonly used as the central event backbone for microservices, analytics pipelines, CDC, and event-driven systems.

### Apache Flink

Apache Flink is a stream processing engine focused on low-latency, high-throughput processing with advanced state management. It supports event-time processing, windows, checkpoints, and complex event processing.

Example Flink-style job output:

```json id="2jq090"
{
  "job": "real-time-fraud-detection",
  "eventsPerSecond": 25000,
  "checkpointStatus": "completed",
  "averageProcessingLatencyMs": 45
}
```

Flink is often chosen for advanced stateful streaming workloads, especially when event-time accuracy and low latency matter.

### Apache Spark Streaming

Apache Spark Streaming processes streams using a micro-batch model. Data is collected into small batches and processed using Spark’s distributed computation engine.

Example micro-batch output:

```json id="462r8t"
{
  "batchIntervalSeconds": 5,
  "recordsProcessed": 120000,
  "processingTimeSeconds": 3.2
}
```

Spark Streaming is useful when teams already use Spark for batch analytics and want near-real-time processing with similar tooling.

---

### Apache Pulsar

Apache Pulsar combines messaging and streaming capabilities. It supports topics, subscriptions, message retention, geo-replication, and separation of serving and storage layers.

Example Pulsar-style output:

```json id="smcxb8"
{
  "topic": "persistent://production/orders/events",
  "subscription": "analytics",
  "messagesProcessed": 50000,
  "geoReplication": "enabled"
}
```

Pulsar is useful for systems that need scalable messaging, multi-tenant isolation, or geo-replicated event streams.

### When to Use Stream Processing

Stream processing is a good fit when the value of data decreases if processing is delayed. If decisions, alerts, or dashboards need to update quickly, stream processing is often better than waiting for nightly or hourly batch jobs.

Common use cases include:

* **Real-time Analytics**: Dashboards showing up-to-date traffic, sales, sensor readings, or system metrics.
* **Fraud Detection**: Transactions analyzed as they happen so suspicious activity can be blocked or flagged quickly.
* **Monitoring and Alerting**: Logs and metrics processed continuously to detect outages or performance issues.
* **Personalization**: Recommendations updated based on recent user behavior.
* **Data Synchronization**: CDC events used to update caches, search indexes, and downstream systems.

Example fraud detection input:

```json id="cxld40"
{
  "transactionId": "txn-123",
  "userId": "user-456",
  "amount": 2500,
  "country": "DE",
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Example fraud detection output:

```json id="8f8vdd"
{
  "transactionId": "txn-123",
  "riskScore": 0.91,
  "action": "manual_review_required"
}
```

Stream processing is not always necessary. If the business can wait minutes, hours, or days for results, batch processing may be simpler and cheaper. Stream processing is most valuable when low-latency action, continuous updates, or real-time visibility are required.
