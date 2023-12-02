## Linearizability

Linearizability is a consistency model used to make it seem like there's only one copy of the data. It ensures that:

- All reads reflect the latest written value.
- The system appears consistent and up-to-date.
- Availability and speed may be impacted.
  
```
Write Request       Read Request       Read Request
     |                  |                  |
     V                  V                  V
+----------+       +----------+       +----------+
|          |       |          |       |          |
| Database | ----> | Database | ----> | Database |
| (Latest  |       | (Latest  |       | (Latest  |
|  Value)  |       |  Value)  |       |  Value)  |
|          |       |          |       |          |
+----------+       +----------+       +----------+
```

## Ordering

To achieve linearizability, an order for data operations is required:

- Use Lamport timestamps to generate sequence numbers across multiple machines.
- Timestamps are tuples of the counter and the node ID.
- Nodes and clients track the maximum counter value and include it in every request.
- Lamport timestamps provide a total ordering but can't show concurrent operations.

## Total Order Broadcast

Total order broadcast is a protocol to exchange messages between nodes:

- Ensures no messages are lost.
- Delivers messages to every node in the same order.
- Helps solve problems like uniqueness constraints across different replicas.

## Distributed Transactions and Consensus

Distributed transactions can use the two-phase commit:

- Coordinator node sends writes and prepare requests to other nodes.
- Nodes either commit or abort based on the coordinator's decision.
- The coordinator maintains an internal log of decisions for crash recovery.

## Quorum and Consensus Algorithms

Consensus algorithms use a majority (quorum) of nodes to improve availability:

- New leaders are elected in subsequent epochs to prevent split-brain scenarios.
- Consensus algorithms define a recovery process for nodes to reach a consistent state.
- Coordination services like ZooKeeper provide replicated in-memory key-value stores for total order broadcast.
