## Stream Processing

Stream processing enables real-time computations on data moving through the system, ideal for applications that require prompt responses to constantly changing data.

### Message Brokers

Message brokers facilitate asynchronous communication between systems, working as intermediaries to store, route, and transmit messages:

- **Load balancing**: Distributes messages evenly among multiple consumers, maximizing throughput.
- **Fan out**: Broadcasts each message to all consumers, useful for publish-subscribe models.

### Log-Based Message Brokers

Log-based message brokers append incoming messages to a log:

- Consumers process messages sequentially, maintaining order.
- Topics (distinct message categories) can be partitioned across multiple logs for better scalability and fault tolerance.

### Change Data Capture (CDC)

CDC transforms changes in databases into a series of events, which can then be processed in a message broker:

- Useful for keeping multiple data systems synchronized.

### Event Sourcing

Event sourcing captures changes to application state as a sequence of events:

- Events are stored in an append-only log and replayed to derive the current state.
- This approach offers excellent traceability and auditing capabilities.

### Streams and Time

In a distributed system, handling time is nontrivial due to factors like network latency and clock drift:

- **Hopping windows**: Non-overlapping, fixed-size time windows.
- **Sliding windows**: Overlapping time windows, capturing all events within a certain time range.
- **Tumbling windows**: Non-overlapping, fixed-size time windows, similar to hopping windows, but without overlap.

### Stream Joins

Joins correlate data from different streams or between streams and static data:

- **Stream-Stream Join**: Requires maintaining state in both streams and joining events as they arrive.
- **Stream-Table Join**: Involves joining a stream with a static table, requiring a local copy of the table.
- **Table-Table Join**: Involves joining two tables, often using CDC to keep the tables up to date.

### Fault Tolerance

Fault tolerance techniques ensure the system continues to operate correctly despite failures:

- **Micro batching**: Breaks the stream into small, manageable batches to process.
- **Checkpointing**: Records the progress at regular intervals to recover from a failure.
- **Atomic transactions and idempotence**: Ensure operations are completed exactly once, preventing duplication of side effects.
