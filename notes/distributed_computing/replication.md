
# Replication
Replication is the process of storing multiple copies of data on multiple different computers. It is used for the following purposes:

1. Redundancy: Data remains accessible even if one of the database nodes crashes.
2. Improved Performance: Reading and writing operations are speed up when performed by a geographically closer node.
3. Reduced Load: Replicating data to many databases allows the reduction of load on each one.

## Single Leader Replication
In single leader replication, one of the nodes is designated to be the leader and all writes are sent to this leader. The other replicas are known as followers and receive data from the leader via a replication log. This process can be performed either synchronously or asynchronously.

- **Asynchronous Replication**: The client receives a message confirming the write the moment it reaches the leader. All changes to the replicas are propagated in the background, using eventual consistency.
- **Synchronous Replication**: All followers must have up to date data. This is impractical since a crash or slow performance on one of the followers can break the whole system. Typically, only one follower is synchronous while the rest are asynchronous.
- **Setting Up Followers**: Involves taking a consistent snapshot of the leader database, copying it to the follower node and then connecting to the leader. The replication log is used to catch up from the snapshot.

## Leader Failure
In the event of a leader failure, the system must perform a failover. This involves determining if the leader has actually failed using a timeout and then using a consensus mechanism to determine a new leader. Clients must be configured to send their write requests to the new leader, and the old leader must be aware that it is now a follower.

Failover can be dangerous since some writes from the old leader may be discarded, leading to inconsistencies with other systems. Additionally, if the timeout for determining failover is too small, unnecessary failovers may be performed.

## Replication Log Implementation
The replication log can be implemented in two ways: 
- Copying over the SQL statements used by the leader. This is problematic since some SQL commands are nondeterministic.
- Using a write ahead log. This is the same log used for indexing, which contains a sequence of bytes with all writes to the database. This allows rolling upgrades and makes recovery from crashing followers easier.

## Problems with Replication Lag and Eventual Consistency
Replication lag and eventual consistency can lead to various issues:

1. Reading Your Own Writes: After writing data and refreshing, the old data may still be seen since changes have yet to be propagated.
2. Monotonic Reads: Reads on different replicas can lead to moving back in time.
3. Consistent Prefix Reads: When two entries have a causal relationship, but the one that precedes the other has a greater replication lag, it may seem like the latter write comes before the preceding one.

## Multi Leader Replication
Multi leader replication adds significant complexity to single leader replication. Each leader is also a follower for all of the other leaders, leading to the need to resolve conflicting writes between different leaders. This works well in cases with multiple data centers in geographically different regions.

Various topologies can be used for propagating writes from one leader to another, including circular, star and all-to-all topologies. To avoid duplicate operations, the replication log must mark which nodes writes are passed through.

## Leaderless Replication
In leaderless replication, any replica can accept writes from any client. Reads and writes must meet a threshold of successful nodes for the operation to be successful. When an unavailable node comes back online, a client may use read repair to update its value. Anti-entropy is a background process that looks for data differences in replicas and copies the correct data over. Quorums can be used to ensure that a most up-to-date copy of the data is always read.
