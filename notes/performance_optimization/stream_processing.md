## Stream Processing

Stream processing handles continuous data flow in real-time. Message brokers help manage message streams, providing fault tolerance and preventing message loss.

### Message Brokers
- Message brokers are databases designed for message streams.
- They support clients connecting and disconnecting.
- Provide durability and queue up messages when overloaded.
- Messages are deleted from the queue once delivered.

Two main messaging patterns:
* Load balancing: each message goes to one consumer, sharing work.
* Fan out: messages are sent to all consumers.

### Log Based Message Brokers
- Messages are added to a log.
- Consumers read logs sequentially, waiting for new messages.
- Logs can be divided into queues or topics for specific message types.
- Topics can be partitioned for fault tolerance and load balancing.
- Messages get sequence numbers for ordering.

### Change Data Capture
- Treats a database as the leader to keep other data systems in sync.
- Puts database changes into a log-based message broker.
- Other data sources get updates from the broker.

### Event Sourcing
- Uses an append-only log of user events instead of a database.
- Makes maintaining and debugging other schemas easier.
- Requires asynchronous writes.

### Streams and Time
- Late events can be tricky to manage in a time window.
- User and server clocks can be compared for accuracy.
- Hopping windows, tumbling windows, and sliding windows handle event windows differently.

### Stream Joins
- Joining streams with other datasets is necessary.

#### Stream-Stream Join
- Both streams maintain state (usually within a time window).
- Indexes on join keys help join related events.
- Streams check indexes when events arrive.

#### Stream-Table Join
- Requires a local copy of the database table.
- Stream processor subscribes to database changes, updating the local copy.

#### Table-Table Join
- Change data capture keeps tables updated for each stream.
- Joins may be nondeterministic; unique IDs can help but need more storage.

### Fault Tolerance
- Micro batching and checkpointing help ensure each message is processed exactly once.
- Checkpointing tracks consumer offset for each partition in case of crashes.
- Atomic transactions and idempotence prevent external actions from occurring multiple times.

