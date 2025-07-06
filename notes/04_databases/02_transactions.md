## Database Transactions

Database transactions are a cornerstone of reliable data management. They let an application bundle **multiple low-level reads and writes into a single, all-or-nothing unit** so the database moves cleanly from one consistent state to another—even when dozens of users race to change the same rows or hardware glitches interrupt the process. Transactions offer the developer a simple success/ failure switch while the engine handles *locking, logging, versioning,* and *recovery* behind the scenes.

```
+-------------------------------------------------------------+
|            Application (Transaction Context)                |
|                                                             |
|   BEGIN TRANSACTION  ──►   Perform SQL/CRUD Operations      |
|                                                             |
|   COMMIT  ◄── Success? ────── Yes ───┐                      |
|                                      │                      |
|   ROLLBACK ◄── On error or cancel ───┘                      |
+-------------------------------------------------------------+
```

A typical flow starts with **`BEGIN`** (or an implicit start), runs several statements that may touch many tables, then finishes with **`COMMIT`** to make every change permanent—or **`ROLLBACK`** to annul them if any step fails.

### ACID: The Core Properties

* **Atomicity** – All operations inside the transaction succeed together; if one fails, the engine *undoes* every prior step using its log, leaving no half-finished updates behind.
* **Consistency** – Every commit must obey all schema constraints, triggers, and business rules, so the database never lands in an illegal state.
* **Isolation** – Concurrent transactions behave as though executed sequentially; the chosen *isolation level* dictates exactly how invisible their intermediate work is to one another (see earlier section).
* **Durability** – Once the engine acknowledges a commit, the redo/ WAL records are safely persisted—usually flushed to stable media or replicated—so the data survives crashes, power loss, or failover.

### Dealing with Single-Object Writes

```
   Single-Object Write Flow
   +-------------------------+
   |        BEGIN            |
   +-------------+-----------+
                 |
                 v
   +-------------------------+
   |  Lock / Version Check   |
   +-------------+-----------+
                 |
                 v
   +-------------------------+
   |     Apply the Write     |
   +-------------+-----------+
                 |
                 v
   +-------------------------+
   |   COMMIT or ROLLBACK    |
   +-------------------------+
```

* **Write-Ahead Log (WAL)** – The engine first records an *“intent”* entry to durable storage; only after the log is safe does it touch the actual data page, guaranteeing atomicity and crash recovery.
* **Lock-based concurrency** – A short-lived exclusive lock (row or page) blocks other writers, preserving isolation but possibly reducing concurrency.
* **MVCC (Multi-Version Concurrency Control)** – Instead of blocking, the engine keeps the *old* record version for readers while a new version is inserted for writers; this boosts read throughput at the cost of extra storage and version clean-up.
* Because only one object changes, the critical section is small, yet adopting the same ACID machinery keeps semantics uniform across *all* operations—large or tiny.

### Advanced Transaction Management

Complex workloads touch many independent resources—multiple tables, shards, or even distinct databases—so additional coordination layers are required.

#### Two-Phase Commit (2PC)

```
          Coordinator                         Participant(s)
   +-------------------------+      +------------------------------+
   |  1. PREPARE (ask to vote) ──►  |  PRE-COMMIT / VALIDATE       |
   |                             |  |  ─────────────────────────►  |
   |  ◄── 2. VOTES (YES / NO)   |  |            (Vote)            |
   +-------------------------+  |  +------------------------------+
               | All YES?        |
               v                 |
   +-------------------------+   |
   | 3. COMMIT else ROLLBACK |   |
   +-------------------------+   |
```

* *Phase 1* – The **coordinator** writes its own *prepare* record and instructs every **participant** to do the same; each votes *commit* only if it can guarantee durability locally.
* *Phase 2* – If **all** votes are *YES*, the coordinator logs **COMMIT** and tells participants to finalize; any *NO* triggers a **ROLLBACK** everywhere.
* Guarantees global atomicity across disparate systems but can **block** if the coordinator crashes after participants prepared yet before they learned the outcome. Production systems often add *timeouts,* *retry logs,* or even *three-phase commit* variants to reduce that window.

#### Deadlock Detection and Prevention

```
        Deadlock Example
   Transaction A          Transaction B
      |                        |
   lock X                  lock Y
      |                        |
   wait Y  ◄────────────── wait X
      |                        |
   (circular wait → deadlock)
```

* A deadlock is a cycle in the **wait-for graph**: each transaction owns a lock the next needs.
* **Detection** – Engines like PostgreSQL or SQL Server run periodic graph checks; upon finding a cycle they pick a *victim* to roll back automatically.
* **Prevention** – Acquire locks in a canonical order (e.g., by primary key), use *lock time-outs,* or favor MVCC reads to shrink the window.
* **Application best practice** – Keep transactions short and touch data in a predictable order to minimize deadlock probability.

### Concurrency Control Methods Comparison

| Method         | Underlying Mechanism                  | Pros                                                       | Cons                                                          | Typical Scenarios                                    |
| -------------- | ------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| **Locks**      | Pessimistic read/write locks          | Strong consistency; simple mental model                    | Blocking, deadlocks, lock-escalation overhead                 | OLTP systems where conflicts are frequent            |
| **MVCC**       | Append row versions + snapshot reads  | Readers never block writers; high read scalability         | Vacuuming/garbage collection; more I/O for version churn      | Mixed read-heavy workloads (PostgreSQL, InnoDB)      |
| **Timestamps** | Assign global time/order to Txns      | Easy to serialize logically; no blocking                   | High abort rate if contention; clock or logical-counter drift | In-memory or distributed DBs (Spanner, FoundationDB) |
| **Optimistic** | Validate at commit (compare‐and‐swap) | Near-zero overhead during read phase; suits low contention | Late failures waste work; write-write conflicts cause retries | Microservices or mobile apps with rare collisions    |
