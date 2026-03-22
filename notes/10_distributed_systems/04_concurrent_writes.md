## Concurrent Writes

Concurrent writes happen when two or more clients write to the same key in a database at the same time, each **unaware** of the other's write. In replicated systems, these writes may arrive at different replicas in different orders, causing the replicas to **diverge** and hold conflicting values. Without a strategy to detect and resolve these conflicts, the system risks permanent **inconsistency** across its nodes.

```
  Client A writes X=1              Client B writes X=2
  at time T                        at time T
        |                                |
        v                                v
  +------------+                   +------------+
  |  Replica 1 |                   |  Replica 2 |
  |   X = 1    |                   |   X = 2    |
  +------+-----+                   +------+-----+
         |                                |
         |      (replication lag)         |
         v                                v
  +------------+                   +------------+
  |  Replica 1 |                   |  Replica 2 |
  |  X = 1? 2? |                   |  X = 2? 1? |
  +------------+                   +------------+

  Both replicas received both writes but in
  different orders — which value is correct?
```

- The core **problem** is that there is no single source of truth when multiple writers operate independently.
- Replicated databases face this challenge because network **latency** means writes propagate to other nodes at different speeds.
- Without conflict resolution, two replicas can settle on **different** final values for the same key, violating eventual consistency guarantees.

## Detecting Concurrent Writes

- Both multi-leader and leaderless replication systems must **detect** concurrent writes before they can resolve them.
- Events may arrive in different **orders** at different nodes, so the system cannot rely on arrival sequence to determine which write came first.
- Two writes are considered **concurrent** if neither causally depends on the other — that is, neither writer knew about the other's write when it was issued.
- A write A **happens-before** write B if B was made with knowledge of A's result; in that case the writes are sequential and B simply overwrites A.
- Determining causality requires the system to track **metadata** about which prior state each write was based on.

```
  Timeline at Node 1                Timeline at Node 2

  t1: Receive Write A               t1: Receive Write B
      (X = "apple")                     (X = "banana")
        |                                 |
  t2: Receive Write B               t2: Receive Write A
      (X = "banana")                     (X = "apple")
        |                                 |
        v                                 v
  Final state: X = "banana"         Final state: X = "apple"
                 ↑                                  ↑
                 |                                  |
              INCONSISTENT — replicas disagree!
```

- If nodes simply apply writes in the **order** they arrive, two nodes can end up with permanently different final values.
- The system must use a deterministic **strategy** to ensure all replicas converge to the same value regardless of arrival order.

## Last Write Wins

- The simplest conflict resolution approach is the **LWW** (last write wins) strategy, where each write is assigned a timestamp and the write with the highest timestamp is kept.
- All conflicting writes are given an **arbitrary** ordering based on their timestamps, and only the "latest" write survives.
- LWW is easy to **implement** because every node can independently pick the same winner by comparing timestamps.
- The major downside is **durability** — writes that arrived "earlier" according to the timestamp are silently discarded, even if they contained important data.
- Timestamps across distributed nodes are subject to **clock-skew**, meaning a write that actually happened first could receive a later timestamp and incorrectly win.
- Cassandra and DynamoDB use LWW as their **default** conflict resolution strategy because it trades correctness for simplicity and availability.
- LWW is safe only when keys are written **once** and never updated, or when losing some writes is acceptable for the application.

```
  Client A: SET X = "apple"  (timestamp: 100)
  Client B: SET X = "banana" (timestamp: 105)

  +---------------------+          +---------------------+
  |     Replica 1       |          |     Replica 2       |
  |                     |          |                     |
  |  Receives:          |          |  Receives:          |
  |   A (ts=100) first  |          |   B (ts=105) first  |
  |   B (ts=105) second |          |   A (ts=100) second |
  |                     |          |                     |
  |  Keeps: B (ts=105)  |          |  Keeps: B (ts=105)  |
  |  X = "banana"  ✔    |          |  X = "banana"  ✔    |
  +---------------------+          +---------------------+

  Both replicas converge on the same value,
  but Client A's write is lost forever.
```

## Immutable Keys

- An alternative approach is to make each key **immutable** — once a value is written, it can never be overwritten.
- Every write creates a new **unique** key (for example by appending a UUID), so concurrent writes never conflict because they target different keys.
- This strategy guarantees that no data is **lost**, since every write is preserved under its own identifier.
- Immutable keys work well for **append-only** workloads such as event logs, audit trails, and time-series data.
- The trade-off is that applications must handle **multiple** versions of conceptually related data, often requiring a separate read-time merge step.
- This approach may not suit use cases that require **mutable** state, such as a user profile that needs to be updated in place.

## Version Numbers

- Version numbers provide a way to **track** the causal history of a key's value, enabling the system to detect concurrent writes precisely.
- The server maintains a **counter** for each key that is incremented every time the key is written.
- When a client reads a key, the server returns the current value along with its **version** number.
- When a client writes, it sends the version number it last **observed** — this tells the server which state the client's write was based on.
- If the client's version matches the server's current version, the write is a simple **sequential** update and the server increments the version.
- If the client sends a version that is **older** than the current version, the server knows a concurrent write has occurred.
- When a concurrent write is detected, the server keeps **both** values (called siblings) and returns them on the next read, letting the application decide how to merge.
- If the client writes without any prior version (version **null**), the server treats the write as concurrent with all existing values.
- The application is responsible for **merging** sibling values — it can do so automatically (for example, taking the union of items in a shopping cart) or by prompting the user to choose.

```
  Server (key: "cart")                Client A                  Client B
  ========================            ========                  ========

  v1: cart = {milk}
        |
        +--- read ----------------------> gets v1, {milk}
        |
        +--- read ----------------------------------------------------> gets v1, {milk}
        |
        +<-- write(v1, {milk, eggs}) ---- Client A adds eggs
        |
  v2: cart = {milk, eggs}
        |
        +<-- write(v1, {milk, bread}) --------------------------------- Client B adds bread
        |                                                                (based on stale v1!)
  v3: cart = [{milk, eggs},
              {milk, bread}]          <-- server keeps BOTH as siblings
        |
        +--- read ----------------------> gets v3, [{milk, eggs}, {milk, bread}]
        |
        +<-- write(v3, {milk, eggs, bread})  Client A merges siblings
        |
  v4: cart = {milk, eggs, bread}      <-- conflict resolved, no data lost
```

- This approach ensures **no** writes are silently discarded, unlike last-write-wins.
- The cost is additional **complexity** in the application layer, which must implement merge logic for sibling values.

## Version Vectors

- When data is replicated across **multiple** nodes, a single version number is not enough — each replica may accept writes independently.
- A version vector extends the version number concept by maintaining a **separate** counter for every replica.
- The version vector for a key is a collection of `(replica, version)` **pairs** — for example `{A:3, B:2, C:5}` means replica A has seen 3 writes, B has seen 2, and C has seen 5.
- When a client reads from a replica, it receives the key's current version **vector** along with the value.
- When a client writes, it sends back the version vector it observed, allowing the receiving replica to **compare** vectors and detect concurrency.
- Vector A **dominates** vector B if every component in A is greater than or equal to the corresponding component in B — this means A causally follows B.
- If neither vector dominates the other, the writes are **concurrent** and the system must keep both values as siblings.
- Riak used version vectors (which it called **dotted** version vectors) to track causality across its distributed vnodes.

```
  Replica A                    Replica B                    Replica C
  =========                    =========                    =========

  Write X = 1
  VA = {A:1}
       |
       +--- replicate -------> VB = {A:1}
       |                            |
       |                       Write X = 2
       |                       VB = {A:1, B:1}
       |                            |
       |                            +--- replicate -------> VC = {A:1, B:1}
       |                                                         |
  Write X = 3                                               Write X = 4
  VA = {A:2}                                                VC = {A:1, B:1, C:1}
       |                                                         |
       +--- compare with C's vector --------------------------->|
       |                                                         |
  {A:2} vs {A:1, B:1, C:1}                                      |
  Neither dominates the other → writes are CONCURRENT            |
  System keeps both values as siblings                           |
```

- Version vectors allow the system to precisely **distinguish** between sequential writes (which can be safely overwritten) and concurrent writes (which must be preserved as siblings).
- The size of the vector grows with the number of **replicas**, not the number of writes, so it remains compact in typical deployments.

## Conflict Resolution Strategies Compared

| Aspect                    | Last Write Wins          | Immutable Keys            | Version Numbers            | Version Vectors            |
| ------------------------- | ------------------------ | ------------------------- | -------------------------- | -------------------------- |
| **Data loss**             | Yes — silent overwrites  | None                      | None (siblings kept)       | None (siblings kept)       |
| **Complexity**            | Very low                 | Low                       | Moderate                   | High                       |
| **Clock dependency**      | Yes — needs timestamps   | No                        | No                         | No                         |
| **Multi-replica support** | Yes                      | Yes                       | Single replica only        | Yes — designed for it      |
| **Merge responsibility**  | System (automatic)       | Application (at read)     | Application (at read)      | Application (at read)      |
| **Best suited for**       | Write-once data, caches  | Event logs, audit trails  | Single-leader with conflicts | Multi-leader / leaderless |
| **Real-world usage**      | Cassandra, DynamoDB      | Event sourcing systems    | Single-node key stores     | Riak, Dynamo-style DBs    |

- Choosing the right strategy depends on whether the application can **tolerate** lost writes and how much complexity it can absorb in the merge layer.
- Systems that prioritize **availability** (AP in the CAP theorem) often use LWW for simplicity, while systems that require strong consistency use version vectors.
- Many production systems **combine** strategies — for example, using LWW for non-critical metadata and version vectors for business-critical data.
