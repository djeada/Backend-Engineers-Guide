## Replication

Replication is a method of maintaining copies of data across multiple nodes in distributed systems, making it useful for improving availability, reducing latency, and distributing load. Below are detailed notes, organized in bullet points, each containing one highlighted word in the middle to emphasize a key concept. Simple ASCII diagrams are included to illustrate how replication can be structured.

```
            +---------+
            |  Client |
            +----+----+
                 |
        Read/Write Requests
                 |
                 v
     +-----------+-----------+     
     |        Leader        |  (Single Leader Replication)
     +-----------+-----------+
                 |  Replication Log
     +-----------+-----------+
     |      Follower(s)     |
     +-----------------------+
```

- Replication is **helpful** for ensuring access to data even if one node fails or becomes unreachable.  
- Multiple replicas can be **useful** for distributing read queries, reducing latency for users in different locations.  
- Redundancy is **important** when a critical system must remain operational during hardware or software failures.  
- Different replication strategies can be **valuable** for balancing performance, consistency, and fault tolerance.  
- Monitoring replication lag is **essential** for applications that require up-to-date reads and strong consistency guarantees.  

### Single Leader Replication

Single leader replication designates one node as the leader, which receives all write operations. The followers continuously replicate changes from the leader, ensuring that each follower eventually converges to the same state.

```
+-----------+           +------------+
|   Leader  |  Log ---> |  Follower  |
+-----+-----+           +------------+
      |                      
      | Log               
      v                      
+-----------+                 
| Follower  |                 
+-----------+                 
```

- An **asynchronous** approach can increase throughput because the leader sends updates without waiting for followers to acknowledge them.  
- A **synchronous** method helps safeguard data by waiting for at least one follower to confirm updates before considering the write complete.  
- Initializing a follower is **efficient** if you use a full data snapshot, then replay subsequent log records to become up-to-date.  
- A replication log is **central** to both statement-based and log-based methods, capturing all changes to propagate them to followers.  
- Single leader replication is **beneficial** for applications that require a strict ordering of writes and simpler conflict resolution.  

### Managing Leader Failure

When the current leader fails or becomes unreachable, the system needs to conduct a failover procedure to select a new leader. This process should be carefully handled to avoid data loss and minimize downtime.

- A failover can be **triggered** manually by an operator or automatically by a system health check.  
- A **consensus** algorithm like Raft or Paxos is often used to allow followers to agree on the new leader.  
- Data loss is **possible** with asynchronous replication if the leader crashes before all writes are replicated.  
- Minimizing failover time is **advantageous** for maintaining higher availability and reducing service disruption.  
- Keeping track of each follower’s replication progress is **helpful** for promoting the most up-to-date follower to leader.  

### Implementing the Replication Log

Replication logs form the backbone of data propagation from the leader to followers. Two common strategies are statement-based replication (replicating SQL commands) and log-based replication (using a write-ahead log).

```
   +-------------+
   |  Leader DB  |
   +------+------+ 
          |  (Log Records) 
          v 
   +-------------+
   | Follower DB |
   +-------------+
```

- Statement-based replication is **straightforward** but can lead to nondeterministic behavior if stored procedures behave differently on each node.  
- Log-based replication captures **low-level** changes, ensuring that every byte-level modification is propagated accurately.  
- Write-ahead logs can be **useful** for both durability and replication, allowing a single place to track database modifications.  
- The choice between statement-based or log-based replication is **driven** by factors like performance, deterministic behavior, and schema complexity.  
- Implementations need to be **careful** with triggers, user-defined functions, and any nondeterministic operations.  

### Replication Lag and Eventual Consistency

In distributed systems, the delay between a write operation on the leader and its visibility on the followers is known as replication lag. This delay can affect how quickly data converges across nodes, leading to an eventually consistent state if delays are long.

- Applications may be **affected** by reading stale data if the system design does not address read-after-write consistency.  
- Monotonic reads are **desired** by some applications, where each subsequent read by a user sees the same or newer data.  
- A consistent prefix read is **important** when you want to ensure that reads reflect the chronological order of writes.  
- Eventual consistency is **common** in high-availability systems that accept temporary data divergence for better performance and uptime.  
- Monitoring replication lag is **critical** for diagnosing performance bottlenecks and adjusting system parameters.  

### Multi Leader Replication

In a multi-leader setup, each node can accept writes and replicate them to others, making it useful for geographically distributed deployments or cases where local write performance is prioritized. However, handling conflicting writes becomes more challenging.

```
          +-------+
          |Node A |
          +---+---+
              | ^ 
    (Writes)  | |   (Writes)
              v |
          +---+---+
          |Node B |
          +---+---+
              | ^
    (Writes)  | |   (Writes)
              v |
          +---+---+
          |Node C |
          +-------+
```

- Write conflicts are **likely** when multiple leaders accept writes concurrently, requiring conflict resolution strategies.  
- Conflict resolution can be **handled** by methods like last-write-wins, custom merge logic, or prompting user intervention.  
- Latency can be **reduced** for local operations since each region can write to its closest leader.  
- A multi-leader design is **beneficial** for collaboration software that allows multiple active editors in different regions.  
- Dealing with circular or cyclical replication is **crucial** for avoiding infinite update loops among nodes.  

### Leaderless Replication

Leaderless systems eliminate the concept of a single leader node, allowing any replica to accept writes. Such systems typically rely on a quorum approach to ensure most nodes agree on a given update or read, aiming to maintain consistency without centralized coordination.

```
        Leaderless Model
          +-----+
  Write -> |Node1| <-----
          +-----+       | 
                        |
          +-----+    +-----+
Read  <-  |Node2| <--|Node3|
          +-----+    +-----+
```

- A **quorum** read or write operation ensures that a majority of replicas confirm the operation, making data consistent if enough nodes respond.  
- Anti-entropy processes are **essential** for reconciling divergent replicas in the background.  
- Read-repair is **helpful** for fixing stale replicas whenever a read detects inconsistent data versions.  
- Leaderless designs are **common** in distributed key-value stores like Cassandra or Riak, which prioritize availability.  
- Eventual convergence is **achieved** when all nodes have consistent data after replicated writes.  
