## Replication

Replication is a critical aspect of distributed data systems, aimed at ensuring data availability, reducing latency, and load balancing.

1. Redundancy: Access to data even if a database node crashes.
2. Improved Performance: Faster read and write operations with closer nodes.
3. Reduced Load: Spreading data across databases lowers load on each one.

### Single Leader Replication

In single leader replication, one node acts as a leader, receiving all write requests. Followers, i.e., replicas, update themselves based on a replication log provided by the leader. 

- **Asynchronous Replication**: Here, the leader responds to write requests as soon as they are logged, regardless of whether the followers have updated. This approach boosts performance but risks data loss in case the leader crashes before the followers update.
- **Synchronous Replication**: In this mode, at least one follower needs to acknowledge receiving the updates before the leader responds to write requests. This ensures data safety at the cost of performance.
- **Initializing a Follower**: To setup a follower, it's common to create a snapshot of the leader's database state, copy it to the follower, then follow the replication log to get up-to-date.

### Managing Leader Failure

In the event of a leader failure, a process known as failover initiates to choose a new leader from the followers. This usually involves a consensus algorithm like Raft or Paxos. During failover, it's possible for some data to be lost if asynchronous replication is used, and care should be taken to minimize the duration of this state.

### Implementing the Replication Log

Replication logs can be implemented through statement-based replication (where SQL commands from the leader are copied) or log-based replication (using the write-ahead log which records all changes to the database). Each approach has its trade-offs and must be chosen based on the specific requirements of your system.

### Replication Lag and Eventual Consistency

Given the distributed nature of this setup, there can be a lag between a write operation and its visibility across all nodes (replicas). This latency can cause issues related to read-after-write consistency, monotonic reads, and consistent prefix reads.

### Multi Leader Replication

In a multi-leader setup, each node can accept write operations and act as a leader. This mode improves write performance across geographically distributed clusters but introduces complexities in managing data consistency due to potential write conflicts.

### Leaderless Replication

In leaderless systems, any node can accept writes, providing high write availability. Such systems often use a quorum approach, requiring a majority of nodes to agree on a write or read, and feature mechanisms like anti-entropy processes and read-repair to maintain consistency.
