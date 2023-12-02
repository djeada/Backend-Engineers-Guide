## Stream Processing

Stream processing is a technology designed for handling real-time data streams, enabling immediate computations on data as it flows through the system. This is particularly useful for applications needing rapid responses to continuously evolving data.

Here's a diagram to illustrate the concept:

```
+---------------+    +----------------------------+    +--------------+
|               |    |                            |    |              |
| Data Sources  +--->+ Stream Processing          +--->+ Final Output |
|               |    | (Real-time/Near-real-time) |    |              |
+---------------+    +----------------------------+    +--------------+
      |                             |                          |
      |                             |                          |
      |_____________________________|__________________________|
             Continuous Stream of Data
```

- **Data Stream**: Represents the live, real-time data being fed into the system. This could be from various sources like sensors, online transactions, social media feeds, etc.
- **Stream Processing System**: This is the core component that processes the incoming data streams. It consists of one or more processing stages (P1, P2, P3, etc.), each designed to perform specific computations or transformations on the data.
- **Processing Stages (P1, P2, P3, etc.)**: These represent individual steps within the stream processing system. They handle incoming data in a concurrent manner - processing it as soon as it arrives, rather than waiting for a complete batch. This allows for real-time or near-real-time data processing.
- **Processed Data**: This is the output after stream processing. The output is typically available almost instantaneously, or with minimal delay, after the data has been processed. It can be used for immediate decision-making, alerts, or further analytics.

### Message Brokers

Message brokers are key components in distributed systems, providing asynchronous communication capabilities between different systems or services. They act as intermediaries, managing the storage, routing, and transmission of messages:

- **Load Balancing**: Helps in distributing incoming messages across multiple consumers or services, thus ensuring an even workload distribution and optimizing overall system throughput.
- **Fan-out**: Enables broadcasting of messages to multiple consumers simultaneously. This is particularly useful in publish-subscribe scenarios, where each message should reach all subscribers.

### Log-Based Message Brokers

Log-based message brokers introduce a structured approach to handling messages by utilizing a log system:

- **Sequential Processing**: Consumers process messages in the order they were received, which is crucial for maintaining data consistency and order.
- **Partitioning and Scalability**: Topics, representing distinct message streams or categories, can be partitioned across multiple logs. This not only enhances scalability but also improves fault tolerance, as it allows for distributed data management.

### Change Data Capture (CDC)

CDC is a design pattern used to elegantly handle changes in databases:

- **Event Generation**: It captures the changes occurring in a database and converts them into a stream of events.
- **Data Synchronization**: These events can then be utilized by message brokers to synchronize changes across different systems, ensuring data consistency and continuity.

### Event Sourcing

Event Sourcing is an architectural pattern focused on capturing changes in application state:

- **Event Log**: Changes are stored as a series of events in an append-only log, which acts as a record of all state changes over time.
- **State Reconstruction**: By replaying these events, the current state of the application can be reconstructed. This method provides exceptional traceability and aids in auditing and debugging, as the entire history of changes is available for review.

### Streams and Time

In a distributed system, handling time is nontrivial due to factors like network latency and clock drift:

- **Hopping windows**: Non-overlapping, fixed-size time windows.
- **Sliding windows**: Overlapping time windows, capturing all events within a certain time range.
- **Tumbling windows**: Non-overlapping, fixed-size time windows, similar to hopping windows, but without overlap.

Example:

1. Hopping Windows

- Hopping windows can have gaps or overlaps, depending on the hop size relative to the window size.
- Each window covers a 6-minute period.
- The hop between the start of each window is 10 minutes, meaning each new window starts 10 minutes after the previous one.
- Window 1 spans from 0 to 6, followed by a 4-minute gap (since the hop is 10 minutes), then Window 2 spans from 10 to 16, and so on.
    
```
Time:     0----2----4----6----8----10---12---14---16---18---20---22---24---26---28---30
Window 1: [=====]
          0----2----4----6
Window 2:                          [=====]
                                   10---12---14---16
Window 3:                                                   [=====]
                                                            20---22---24---26
```

2. Sliding Windows

- Sliding windows overlap, with the shift (or slide) being smaller than the window size.
- Each window covers a 6-minute period.
- Windows slide forward by 2 minutes each time, overlapping with the previous window.
- Window 1 starts at 0, Window 2 starts at 2, Window 3 starts at 4, and so on, each sliding forward by 2 minutes.
    
```
Time:     0----2----4----6----8----10---12---14---16---18---20
Window 1: [=====]
          0----2----4----6
Window 2:      [=====]
               2----4----6----8
Window 3:           [=====]
                    4----6----8----10
```

3. Tumbling Windows

- Tumbling windows are non-overlapping, fixed-size time windows that are contiguous.
- Each window spans 6 minutes.
- There are no gaps between windows; each starts immediately after the previous one ends.
- For example, Window 1 spans from 0 to 6, Window 2 from 6 to 12, Window 3 from 12 to 18, and so on.

```
Time:     0----2----4----6----8----10---12---14---16---18---20
Window 1: [=====]
          0----2----4----6
Window 2:                [=====]
                         6----7----9----12
Window 3:                               [=====]
                                        12---14---16--18
```

### Stream Joins

Joins correlate data from different streams or between streams and static data:

- **Stream-Stream Join**: Requires maintaining state in both streams and joining events as they arrive.
- **Stream-Table Join**: Involves joining a stream with a static table, requiring a local copy of the table.
- **Table-Table Join**: Involves joining two tables, often using CDC to keep the tables up to date.

Example:

1. Stream-Stream Join: Joining "Order" stream with "Payment" stream by order ID.

```
Stream 1 (Orders)                 Stream 2 (Payments)
(OrderID1, ProductA, $20)         (OrderID1, Paid $20)
(OrderID2, ProductB, $15)         (OrderID3, Paid $30)

   | Stream-Stream Join |
(OrderID1, ProductA, $20) from Stream 1
(OrderID1, Paid $20) from Stream 2
Joined Result: (OrderID1, ProductA, $20, Paid $20)

(OrderID2, ProductB, $15) from Stream 1
No corresponding payment event in Stream 2
Unjoined Result: (OrderID2, ProductB, $15, Unpaid)

```

Here, orders and payments are joined by OrderID as they arrive in their respective streams.

2. Stream-Table Join: Joining "User Activity" stream with a "User Profile" table.

```
Stream (User Activity)                  Table (User Profile)
(UserID1, LoggedIn, 10:00 AM)           (UserID1, Alice, 28)
(UserID2, ViewedProduct, 10:05 AM)      (UserID2, Bob, 35)

   | Stream-Table Join |
(UserID1, LoggedIn, 10:00 AM) from Stream
(UserID1, Alice, 28) from Table
Joined Result: (UserID1, LoggedIn, 10:00 AM, Alice, 28)

(UserID2, ViewedProduct, 10:05 AM) from Stream
(UserID2, Bob, 35) from Table
Joined Result: (UserID2, ViewedProduct, 10:05 AM, Bob, 35)
```

User activities are joined with user profile information by UserID.

3. Table-Table Join: Joining "Employee" table with "Department" table.

```
Table 1 (Employee)                     Table 2 (Department)
(EmpID1, Alice, DeptID1)               (DeptID1, Human Resources)
(EmpID2, Bob, DeptID2)                 (DeptID2, Information Technology)

   | Table-Table Join |
(EmpID1, Alice, DeptID1) from Table 1
(DeptID1, Human Resources) from Table 2
Joined Result: (EmpID1, Alice, DeptID1, Human Resources)

(EmpID2, Bob, DeptID2) from Table 1
(DeptID2, Information Technology) from Table 2
Joined Result: (EmpID2, Bob, DeptID2, Information Technology)
```

Here, employee information is joined with department information based on the DeptID.

### Fault Tolerance

Fault tolerance techniques ensure the system continues to operate correctly despite failures:

- **Micro batching**: Breaks the stream into small, manageable batches to process.
- **Checkpointing**: Records the progress at regular intervals to recover from a failure.
- **Atomic transactions and idempotence**: Ensure operations are completed exactly once, preventing duplication of side effects.
