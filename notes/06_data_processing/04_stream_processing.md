## Stream Processing

Stream processing enables real-time computations on data moving through the system, ideal for applications that require prompt responses to constantly changing data.

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

- Data Stream represents real-time data feeding into the system.
- Stream Processing is the system or application that processes these data streams.
- P1, P2, and P3 represent individual processing stages within the stream processing system. They process incoming data simultaneously or as it arrives, without waiting for the entire batch to be ready.
- Processed Data represents the output data after the stream processing. It's generally available almost instantly after the data has been processed.

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

Example:

1. Hopping Windows

- In this example, each window is 6 minutes long.
- The hop (shift) of 4 minutes means that the start of each new window is 4 minutes after the start of the previous window.

```
Time:     0----2----4----6----8----10---12---14---16---18---20
Window 1: [=====]
          0----2----4----6
Window 2:           [=====]
                     4----6----8----10
Window 3:                   [=====]
                             8----10---12---14
```

2. Sliding Windows

Each window is 5 minutes long and slides by 1 minute. Window1 covers time 0 to 5, Window2 covers time 1 to 6, and so on.

```
Time:     0----1----2----3----4----5----6----7----8----9----10
Window1:  [=====]
          0----1----2----3----4
               Window2:       [=====]
                               1----2----3----4----5
                                    Window3:              [=====]
                                                          2----3----4----5----6
```

3. Tumbling Windows

```
Time:     0----5----10----15----20
Window1:  [=====]
          0----1----2----3----4
               Window2:       [=====]
                               5----6----7----8----9
                                    Window3:              [=====]
                                                          10---11---
```

### Stream Joins

Joins correlate data from different streams or between streams and static data:

- **Stream-Stream Join**: Requires maintaining state in both streams and joining events as they arrive.
- **Stream-Table Join**: Involves joining a stream with a static table, requiring a local copy of the table.
- **Table-Table Join**: Involves joining two tables, often using CDC to keep the tables up to date.

Example:

1. Stream-Stream Join: Joining "Order" stream with "Payment" stream by order ID.

```
Stream 1 (Orders)    Stream 2 (Payments)
(OrderID1, Product)  (OrderID1, Paid)
(OrderID2, Product)  (OrderID3, Paid)

   | Stream-Stream Join |
(OrderID1, Product) from Stream 1
(OrderID1, Paid) from Stream 2
Joined: (OrderID1, Product, Paid)

(OrderID2, Product) from Stream 1
No corresponding event in Stream 2
```

Here, orders and payments are joined by OrderID as they arrive in their respective streams.

2. Stream-Table Join: Joining "User Activity" stream with a "User Profile" table.

```
Stream (User Activity)    Table (User Profile)
(UserID1, Activity)       (UserID1, Name, Age)
(UserID2, Activity)       (UserID2, Name, Age)

   | Stream-Table Join |
(UserID1, Activity) from Stream
(UserID1, Name, Age) from Table
Joined: (UserID1, Activity, Name, Age)

(UserID2, Activity) from Stream
(UserID2, Name, Age) from Table
Joined: (UserID2, Activity, Name, Age)
```

User activities are joined with user profile information by UserID.

3. Table-Table Join: Joining "Employee" table with "Department" table.

```
Table 1 (Employee)        Table 2 (Department)
(EmpID, Name, DeptID)     (DeptID, DepartmentName)

   | Table-Table Join |
(EmpID1, Alice, DeptID1) from Table 1
(DeptID1, HR) from Table 2
Joined: (EmpID1, Alice, DeptID1, HR)

(EmpID2, Bob, DeptID2) from Table 1
(DeptID2, IT) from Table 2
Joined: (EmpID2, Bob, DeptID2, IT)
```

Here, employee information is joined with department information based on the DeptID.

### Fault Tolerance

Fault tolerance techniques ensure the system continues to operate correctly despite failures:

- **Micro batching**: Breaks the stream into small, manageable batches to process.
- **Checkpointing**: Records the progress at regular intervals to recover from a failure.
- **Atomic transactions and idempotence**: Ensure operations are completed exactly once, preventing duplication of side effects.
