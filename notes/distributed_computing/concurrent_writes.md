# Concurrent Writes in Replication

Concurrent writes are a common problem in both multileader and leaderless implementations of replication. These occur when two writes to a database from different clients are made at the same time and neither client knows about the other's write. This can lead to inconsistencies in the state of the replicas.

## Detecting Concurrent Writes
- Both multileader and leaderless replication systems must be able to detect and resolve concurrent writes.
- Events may arrive in a different order at different nodes, so it is important that every node eventually reaches a consistent state.

## Last Write Wins
- One common approach to dealing with concurrent writes is the "last write wins" strategy.
- In this approach, writes are given an arbitrary ordering and the last write is chosen as the correct one.
- This approach is easy to implement, but it is not durable as writes are discarded.
- Additionally, using timestamps to order writes can be problematic due to clock skew.

## Immutable Keys
- An alternative approach is to only allow each key to be written once, making it immutable.
- This approach ensures that no writes are lost, but it may not be suitable for all use cases.

## Version Numbers
- A more general approach is to use version numbers to track the state of a key.
- On each write to a key, the client passes the server the last version number of the key that it has seen, and the server assigns a new version number and returns it to the client.
- This allows the server to determine which data the client had access to at the time of writing.
- If the client is making a write independent of existing data, the server can return both versions of the data on subsequent reads.
- The application can then handle these two values and either merge them automatically or prompt the user to do so.

## Version Vectors
- When replicating data to many replicas, version vectors can be used to track the state of the data.
- A version vector is a version number for each replica, as well as for each key.
- Each replica keeps track of its own version number and the version numbers of other replicas in order to decide which values
