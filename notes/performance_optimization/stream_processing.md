
## Stream Processing

Stream processing is a way to process a continuous flow of data in real-time. Message brokers are commonly used to handle message streams, which provide fault tolerance and handle message loss.

### Message Brokers
Message brokers are a type of database optimized for handling message streams. Clients can come and go, and brokers also provide durability. If there are too many messages, they are generally queued up instead of dropped. Once a message has been successfully delivered to a consumer, it is typically deleted from the queue.

When there are multiple consumers, two main patterns of messaging are used:

* Load balancing delivers each message to one consumer to share the work between them.
* Fan out delivers the message to all of the consumers.

### Log Based Message Brokers
In log based message brokers, each message is appended to the end of a log, and consumers read the end of the log sequentially, waiting for new messages to appear. The log can be partitioned into many different queues, with each partition belonging to a topic, which carries messages of the same type. Each partition can be replicated for fault tolerance and assigned to a group of nodes for load balancing. A monotonically increasing sequence number is assigned to every message to assist with ordering them.

### Change Data Capture
Change data capture is a method of treating a database as the leader of all other data systems that need to stay in sync. It does this by taking the changes to a database and putting them into a log based message broker which can be used to update all of the other derived data sources.

### Event Sourcing
Event sourcing is similar to change data capture, but it uses an append only log of events that details what the user is actually doing on the site instead of a database. This makes other schemas easier to maintain and debug, however it requires asynchronous writes.

### Streams and Time
When dealing with events in a given window, it can be difficult to decide whether to disregard a late event due to a network delay or to add it to the window after the fact. If the user clock is unreliable, it can be compared to the server clock at the time of message sending to get an offset between the two. This assumes that network delay is minimal, which is not always the case. 

When dealing with windows, if dealing with overlapping windows on fixed intervals (hopping windows), tumbling windows (non overlapping windows of fixed length) can be used and then aggregated together for the hopping window. Sliding windows with no fixed interval start and end points, but with a fixed duration, can be implemented by keeping a buffer of events sorted by time and then removing old events when they expire from the window.

### Stream Joins
Just like batch processing, streams need to be able to perform joins on other datasets.

#### Stream-Stream Join
When two streams are sending related events that need to be joined with one another, both streams must maintain state (usually for all events within a certain time window). An index can be used to do so on the join key, and each stream can check the index when events come in.

#### Stream-Table Join
Joining stream events with information from the database table requires a local copy of the table as querying the database every time is too slow. This table needs to be updated over time, which can be done by the stream processor subscribing to the database changes of the actual database and then updating its local copy.

#### Table-Table Join
Change data captures can be used to keep two tables up to date for each stream, and then the result of the join can be sent to its destination. Joins become nondeterministic, however, which can be addressed by using a unique ID for the thing being joined with, but this requires more storage.

### Fault Tolerance
In order to ensure that each message is processed exactly once, no less and no more, micro batching and checkpointing can be used to retain the state of the stream. Checkpointing keeps track of the offset of a consumer for each partition in the event of a crash, and then the stream can be restarted from the most recent checkpoint. Atomic transactions and idempotence can also be used to stop things external to the stream (such as sending an email) from occurring twice.
