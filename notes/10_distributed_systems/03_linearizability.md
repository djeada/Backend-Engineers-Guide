## Linearizability

Linearizability is a consistency model that makes a distributed system appear as if there is only a single copy of the data, and every operation takes effect atomically at some point between its invocation and its response. Even when data is replicated across multiple nodes, a linearizable system guarantees that clients always see the most recent write.

- **Recency**: Every read returns the value of the most recent completed write, regardless of which replica handles the request.
- **Atomicity**: Each operation appears to execute instantaneously at a single point in time, with no intermediate states visible to other clients.
- **Ordering**: If operation A completes before operation B begins, then B must see the effects of A.
- **Trade-off**: Providing these guarantees often comes at the cost of higher latency and reduced availability during network partitions.

```
   Client A (Write x=1)        Client B (Read x)        Client C (Read x)
        |                            |                         |
   t0   |------- write(x,1) ------->|                         |
        |                           |                         |
   t1   |                     [write completes]               |
        |                           |                         |
   t2   |                           |------- read(x) ------->|
        |                           |                         |
   t3   |                           |    returns x=1          |
        |                           |                         |
   t4   |                           |          |--- read(x) ->|
        |                           |          |              |
   t5   |                           |          | returns x=1  |
        |                           |          |              |
        v                           v          v              v

   +------------+            +------------+           +------------+
   |  Replica 1 |  --------> |  Replica 2 |  -------> |  Replica 3 |
   |   x = 1    |  replicate |   x = 1    | replicate |   x = 1    |
   +------------+            +------------+           +------------+
        All replicas converge so every read reflects the latest write
```

## Linearizability vs Serializability

These two terms sound similar but describe **different** guarantees. Serializability is a property of transactions in a database, while linearizability is a property of individual read and write operations on a register or object.

- **Serializability**: Guarantees that the outcome of executing transactions concurrently is equivalent to some serial (one-at-a-time) execution order, but that order does not have to match real-time ordering.
- **Linearizability**: Guarantees that individual operations appear to take effect in real-time order, meaning if operation A finishes before operation B starts, A must precede B.
- **Scope**: Serializability applies to multi-operation transactions, while linearizability applies to single-object, single-operation guarantees.
- **Combination**: Strict serializability (also called one-copy serializability) combines both properties, providing the strongest consistency guarantee available.

```
   Serializability (Transaction-level)        Linearizability (Operation-level)
   +-----------------------------------+      +-----------------------------------+
   |  Tx1: Read A, Write B             |      |  Op1: Write(x, 5)   at t=0       |
   |  Tx2: Read B, Write A             |      |  Op2: Read(x) => 5  at t=1       |
   |                                   |      |  Op3: Write(x, 8)   at t=2       |
   |  Result equivalent to Tx1->Tx2    |      |  Op4: Read(x) => 8  at t=3       |
   |  OR Tx2->Tx1 (any serial order)   |      |  (must respect real-time order)   |
   +-----------------------------------+      +-----------------------------------+
```

## Real-World Examples

Linearizability matters in many practical scenarios where stale data can cause correctness problems.

- **Leader Election**: When a distributed system uses a lock to elect a leader, every node must agree on who holds the lock; a stale read could result in two nodes both believing they are the leader (split-brain).
- **Uniqueness Constraints**: If two users try to register the same username concurrently, a linearizable check ensures only one succeeds and the other receives an error.
- **Bank Transfers**: When moving money between accounts, the system must ensure that a balance check reflects all prior debits and credits to avoid overdrafts.
- **Distributed Locking**: Services like Apache ZooKeeper and etcd provide linearizable operations so that distributed locks and leases behave correctly across nodes.
- **Configuration Management**: Updating a feature flag or routing rule must propagate atomically so that all nodes act on the same configuration at any given time.

## Ordering

To achieve linearizability, an ordering mechanism for data operations is required. Without a shared global clock, distributed systems must use logical clocks or consensus protocols to agree on operation order.

- **Lamport Timestamps**: Generate sequence numbers across multiple machines by combining a logical counter with a node ID, producing a tuple like `(counter, nodeId)`.
- **Tracking**: Every node and client tracks the maximum counter value it has seen and includes it in every request, incrementing it with each new operation.
- **Total Ordering**: Lamport timestamps impose a total ordering on all operations, but they cannot distinguish between concurrent and causally related operations.
- **Vector Clocks**: An alternative that maintains a counter per node, allowing the system to detect concurrent operations, at the cost of larger metadata per message.
- **Limitation**: Knowing the total order after the fact is not always sufficient; sometimes you need to know the order in real time to make decisions, which requires consensus.

```
   Node A                     Node B                     Node C
   counter=0                  counter=0                  counter=0
      |                          |                          |
      |-- send(counter=1) ----->|                          |
      |                         |-- recv, set counter=2 -->|
      |                         |                          |-- counter=3
      |                         |                          |
      |<-- send(counter=4) ------------------------------ |
      |                         |                          |
   counter=5                    |                          |
      |                         |                          |
      v                         v                          v

   Lamport Timestamp = (counter, nodeId)
   Example ordering:  (1,A) < (2,B) < (3,C) < (4,C) < (5,A)
```

## Total Order Broadcast

Total order broadcast is a protocol for exchanging messages between nodes that guarantees two key properties: reliable delivery and total ordering. It serves as the foundation for implementing linearizable systems and state machine replication.

- **Reliable Delivery**: If a message is delivered to one node, it is guaranteed to be delivered to all non-faulty nodes, ensuring no messages are silently lost.
- **Total Order**: Every node receives all messages in exactly the same order, so all replicas process state transitions identically.
- **Uniqueness Constraints**: By funneling concurrent requests through total order broadcast, you can enforce constraints like unique usernames across all replicas without conflicts.
- **State Machine Replication**: If every replica starts from the same initial state and applies the same sequence of messages, they all converge to the same final state.
- **Equivalence**: Total order broadcast is formally equivalent to consensus, meaning any system that solves one can solve the other.

```
   Client Request              Total Order Broadcast Layer
       |
       v
   +--------+       +-------------------------------------------+
   | Submit  | ----> |  Assign global sequence number            |
   | Message |       |  Broadcast to all nodes in order          |
   +--------+       +-------------------------------------------+
                          |              |              |
                          v              v              v
                     +---------+    +---------+    +---------+
                     | Node A  |    | Node B  |    | Node C  |
                     | msg #1  |    | msg #1  |    | msg #1  |
                     | msg #2  |    | msg #2  |    | msg #2  |
                     | msg #3  |    | msg #3  |    | msg #3  |
                     +---------+    +---------+    +---------+
                     All nodes deliver messages in the same order
```

## CAP Theorem Implications

The CAP theorem states that a distributed system can provide at most two of three guarantees simultaneously: Consistency (linearizability), Availability, and Partition tolerance. Since network partitions are unavoidable in practice, the real choice is between consistency and availability during a partition.

- **CP Systems**: Choose consistency over availability; during a network partition, some requests may be rejected or delayed until the partition heals (e.g., etcd, ZooKeeper, HBase).
- **AP Systems**: Choose availability over consistency; every request receives a response, but reads may return stale data during a partition (e.g., Cassandra, DynamoDB with eventual consistency).
- **Partition Tolerance**: Network partitions (lost or delayed messages between nodes) are a fact of life in distributed systems and cannot be avoided.
- **Nuance**: In practice, CAP is more of a spectrum than a binary choice; systems often allow tunable consistency levels per operation rather than a single global setting.

```
                           Consistency (C)
                              /      \
                             /        \
                            /    CP    \
                           /   systems  \
                          /              \
                         /________________\
                        /                  \
          Availability (A) ----------- Partition Tolerance (P)
                         \    AP systems   /
                          \               /
                           \_____________/

   Network partitions are inevitable, so the practical trade-off
   is between Consistency and Availability during a partition.
```

## Cost of Linearizability

Linearizability is a strong guarantee, but it comes with measurable performance and availability costs that engineers must consider when designing a system.

- **Latency**: Every write must be acknowledged by enough replicas before it is considered committed, adding round-trip delays proportional to network distance.
- **Availability**: During a network partition, a linearizable system must reject requests to the minority partition to preserve correctness, reducing overall availability.
- **Throughput**: Coordination overhead (consensus rounds, synchronous replication) limits the number of operations the system can process per second compared to eventually consistent systems.
- **Geographic Replication**: Multi-datacenter deployments suffer the most, since cross-datacenter round trips can add tens or hundreds of milliseconds per operation.
- **Workaround**: Many systems offer per-request consistency levels, allowing critical operations (like payments) to use linearizability while less critical operations (like analytics reads) use eventual consistency.

## Consistency Models Comparison

| Model                     | Guarantee                                                        | Latency     | Example Systems                  |
| ------------------------- | ---------------------------------------------------------------- | ----------- | -------------------------------- |
| **Linearizability**       | Reads always return the latest write; real-time ordering         | Highest     | etcd, ZooKeeper, Spanner         |
| **Sequential Consistency**| All nodes see operations in the same order, but not necessarily real-time | High        | ZooKeeper (for some operations)  |
| **Causal Consistency**    | Operations that are causally related are seen in order; concurrent operations may differ | Medium      | MongoDB (causal sessions)        |
| **Eventual Consistency**  | All replicas converge eventually, but reads may return stale data temporarily | Lowest      | Cassandra, DynamoDB, Riak        |
| **Strict Serializability**| Combines serializability and linearizability for the strongest guarantee | Highest     | CockroachDB, Spanner             |

## Distributed Transactions and Consensus

Distributed transactions coordinate writes across multiple nodes. The most common protocol is two-phase commit (2PC), which ensures all participants either commit or abort a transaction together.

- **Phase One (Prepare)**: The coordinator sends a prepare request to every participant node; each participant checks whether it can commit and replies with a vote (yes or no).
- **Phase Two (Commit/Abort)**: If all participants voted yes, the coordinator sends a commit command; if any participant voted no, it sends an abort command to all.
- **Coordinator Log**: The coordinator writes its decision to a durable log before sending the final commit or abort, ensuring it can recover and complete the protocol after a crash.
- **Blocking Problem**: If the coordinator crashes after sending prepare but before sending commit/abort, participants are stuck holding locks and waiting indefinitely, which is a major drawback of 2PC.
- **Three-Phase Commit**: An extension of 2PC that adds a pre-commit phase to reduce blocking, though it is rarely used in practice due to added complexity.

```
   Coordinator                  Participant A             Participant B
       |                             |                          |
       |--- prepare --------------->|                          |
       |--- prepare ----------------------------------------->|
       |                             |                          |
       |<-- vote yes ---------------|                          |
       |<-- vote yes ------------------------------------------|
       |                             |                          |
       | (write decision to log)     |                          |
       |                             |                          |
       |--- commit ---------------->|                          |
       |--- commit ------------------------------------------>|
       |                             |                          |
       |<-- ack --------------------|                          |
       |<-- ack ------------------------------------------------|
       |                             |                          |
```

## Quorum and Consensus Algorithms

Consensus algorithms use a majority (quorum) of nodes to make decisions, avoiding the single-point-of-failure problem that plagues two-phase commit. They form the backbone of modern fault-tolerant distributed systems.

- **Quorum**: A majority of nodes (e.g., 3 out of 5) must agree on a value for it to be considered committed, ensuring that any two quorums overlap by at least one node.
- **Leader Election**: In each epoch (term), a new leader is elected through a vote; a node can only be elected if it has the most up-to-date log, preventing stale data from being promoted.
- **Split-Brain Prevention**: Because a quorum requires a strict majority, at most one leader can be elected per epoch, eliminating the risk of conflicting decisions.
- **Recovery**: When a failed node rejoins, it synchronizes its log with the current leader and replays any missing entries to reach a consistent state.
- **Raft and Paxos**: Raft is the most widely adopted consensus algorithm due to its understandability; Paxos is theoretically equivalent but harder to implement correctly.
- **Coordination Services**: Systems like ZooKeeper, etcd, and Consul implement consensus internally and expose linearizable key-value operations, leader election, and distributed locking as building blocks for other applications.
