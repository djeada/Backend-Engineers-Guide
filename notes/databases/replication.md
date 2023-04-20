## Replication

Replication means storing multiple copies of data on different computers. It helps with:

1. Redundancy: Access to data even if a database node crashes.
2. Improved Performance: Faster read and write operations with closer nodes.
3. Reduced Load: Spreading data across databases lowers load on each one.

## Single Leader Replication

One node becomes the leader; all writes go to it. Other replicas, called followers, get data from the leader through a replication log. Replication can be synchronous or asynchronous.

- **Asynchronous Replication**: Client gets write confirmation once it reaches the leader. Changes propagate to replicas in the background (eventual consistency).
- **Synchronous Replication**: All followers need up-to-date data. Usually, only one follower is synchronous; others are asynchronous.
- **Setting Up Followers**: Take a snapshot of the leader database, copy it to the follower, then connect to the leader. Use the replication log to catch up from the snapshot.

## Leader Failure

Failover happens when the leader fails. Determine leader failure with a timeout, then pick a new leader through consensus. Clients must send write requests to the new leader, and the old leader becomes a follower.

Failover risks discarding some writes from the old leader, causing inconsistencies. Too small a timeout can cause unnecessary failovers.

## Replication Log Implementation

Replication log methods:

- Copying SQL statements from the leader. Some SQL commands can be nondeterministic.
- Using a write-ahead log. The same log is used for indexing and contains all writes to the database. Allows rolling upgrades and easier recovery from crashing followers.

## Replication Lag & Eventual Consistency Issues

Replication lag and eventual consistency can cause problems:

1. Reading Your Own Writes: Old data may still be visible after writing and refreshing.
2. Monotonic Reads: Reading from different replicas may seem like moving back in time.
3. Consistent Prefix Reads: If two entries have a causal relationship but are out of order, it may seem like the latter write comes before the preceding one.

## Multi Leader Replication

Each leader is also a follower for all other leaders. Conflicting writes between different leaders need to be resolved. Useful for geographically different data centers.

Various topologies for propagating writes: circular, star, and all-to-all. Replication log must mark which nodes writes pass through to avoid duplicates.

## Leaderless Replication

Any replica can accept writes from any client. Reads and writes need a threshold of successful nodes for the operation to succeed. When an unavailable node comes back online, clients can use read repair to update its value. Anti-entropy is a background process that checks for data differences in replicas and copies the correct data over. Quorums help ensure the most up-to-date copy of data is always read.
