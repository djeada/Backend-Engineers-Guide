## Concurrent Writes

Concurrent writes happen when two clients write to a database at the same time, unaware of each other's write. This can cause inconsistencies in the replicas.

```
[Write 1]   [Write 2]   [Write 3]
   \            |            /
    \           |           /
     \          |          /
      \         |         /
       \        |        /
       +------------------+
       |     Database     |
       +------------------+
```

## Detecting Concurrent Writes

- Both multi-leader and leaderless replication systems must detect and resolve concurrent writes.
- Events may arrive in different orders at different nodes; it's important for nodes to reach a consistent state eventually.

## Last Write Wins

- A common approach for concurrent writes is the "last write wins" strategy.
- Writes are given an arbitrary order, and the last write is chosen as the correct one.
- Easy to implement, but not durable; some writes are discarded.
- Timestamps for ordering writes can be problematic due to clock skew.

## Immutable Keys

- An alternative is to allow each key to be written only once, making it immutable.
- No writes are lost, but may not suit all use cases.

## Version Numbers

- Use version numbers to track a key's state.
- Clients pass the last version number they've seen to the server, which assigns a new version number and returns it.
- The server determines which data the client had access to at the time of writing.
- If the client writes without relying on existing data, the server can return both versions of the data on subsequent reads.
- The application can handle these two values, either merging them automatically or prompting the user to do so.

## Version Vectors

- Version vectors track the state of data for multiple replicas.
- A version vector includes a version number for each replica and key.
- Each replica keeps track of its own version number and those of other replicas to decide which values to use.
