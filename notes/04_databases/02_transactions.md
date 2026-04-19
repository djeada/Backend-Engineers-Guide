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

#### Practical SQL Examples

```sql
-- Basic transaction: transfer $200 between accounts (PostgreSQL)
BEGIN;
  UPDATE accounts SET balance = balance - 200 WHERE id = 1;
  UPDATE accounts SET balance = balance + 200 WHERE id = 2;
COMMIT;

-- Explicit error handling with savepoints
BEGIN;
  INSERT INTO orders (customer_id, total) VALUES (42, 99.95);

  SAVEPOINT before_inventory;
  UPDATE inventory SET qty = qty - 1 WHERE product_id = 7;
  -- If the update fails (e.g., CHECK constraint: qty >= 0):
  ROLLBACK TO before_inventory;

  -- Retry with a different fulfilment path
  INSERT INTO backorders (product_id, customer_id) VALUES (7, 42);
COMMIT;

-- Setting an isolation level for a critical read
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
  SELECT balance FROM accounts WHERE id = 1;
  UPDATE accounts SET balance = balance - 50 WHERE id = 1;
COMMIT;
```

* The first block shows the classic **money-transfer** pattern—if either `UPDATE` fails the entire transaction rolls back and no money is lost.
* The second block demonstrates **savepoints** for partial rollback inside a larger transaction (covered in detail below).
* The third block locks the transaction to the **SERIALIZABLE** isolation level before performing a read-then-write sequence.

### ACID: The Core Properties

* **Atomicity** – All operations inside the transaction succeed together; if one fails, the engine *undoes* every prior step using its log, leaving no half-finished updates behind.
* **Consistency** – Every commit must obey all schema constraints, triggers, and business rules, so the database never lands in an illegal state.
* **Isolation** – Concurrent transactions behave as though executed sequentially; the chosen *isolation level* dictates exactly how invisible their intermediate work is to one another (see the Isolation Levels section below).
* **Durability** – Once the engine acknowledges a commit, the redo/ WAL records are safely persisted—usually flushed to stable media or replicated—so the data survives crashes, power loss, or failover.

### Isolation Levels

Isolation levels control **how much of one transaction's uncommitted work is visible to others**. Moving from the weakest to the strongest level trades concurrency for correctness.

```
Isolation Level Anomaly Spectrum

  READ            READ            REPEATABLE        SERIALIZABLE
  UNCOMMITTED     COMMITTED       READ
  ─────────────►──────────────►──────────────────►──────────────────►
  │               │               │                  │
  │ Dirty Reads   │               │                  │
  │ Non-Repeat.   │ Non-Repeat.   │                  │
  │ Phantoms      │ Phantoms      │ Phantoms         │ (no anomalies)
  │               │               │                  │
  ◄── Fastest ────────────────────────────── Slowest / Safest ──►
```

#### READ UNCOMMITTED

* A transaction can see **uncommitted (dirty) rows** written by others. Rarely used in practice because a rolled-back write may have already influenced another transaction's decisions.

#### READ COMMITTED

* Each statement sees only data **committed before that statement began**. This is the default in PostgreSQL and Oracle. Dirty reads are impossible, but two identical `SELECT`s in the same transaction can return different rows if another transaction commits between them (**non-repeatable read**).

#### REPEATABLE READ

* The transaction works from a **snapshot taken at its first read**. Re-reading a row always returns the same value. However, *new* rows inserted by other committed transactions may appear (**phantom reads**). MySQL/InnoDB uses this as its default level and largely eliminates phantoms via gap locks.

#### SERIALIZABLE

* The strongest guarantee: the outcome is equivalent to running transactions **one after another**. Engines enforce this through predicate locks, serializable snapshot isolation (SSI), or strict two-phase locking. Provides correctness at the cost of higher abort/retry rates.

#### Isolation Levels Comparison

| Level                  | Dirty Read | Non-Repeatable Read | Phantom Read | Typical Default In          |
| ---------------------- | ---------- | ------------------- | ------------ | --------------------------- |
| **READ UNCOMMITTED**   | Possible   | Possible            | Possible     | —                           |
| **READ COMMITTED**     | ✗          | Possible            | Possible     | PostgreSQL, Oracle, SQL Server |
| **REPEATABLE READ**    | ✗          | ✗                   | Possible     | MySQL / InnoDB              |
| **SERIALIZABLE**       | ✗          | ✗                   | ✗            | Selected explicitly         |

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


```
Write-Ahead Logging (WAL) Flow

  Client                      WAL (on disk)              Data Pages (on disk)
    │                              │                              │
    │  1. BEGIN + UPDATE row 42    │                              │
    │─────────────────────────►    │                              │
    │                              │                              │
    │                     2. Append redo                          │
    │                        log entry ──►  [LSN 101: row 42     │
    │                                        old=A, new=B]       │
    │                              │                              │
    │  3. COMMIT                   │                              │
    │─────────────────────────►    │                              │
    │                     4. fsync commit                         │
    │                        record to disk                      │
    │  ◄── 5. ACK ────────────    │                              │
    │                              │                              │
    │                              │    6. Checkpoint             │
    │                              │    (lazy background write)   │
    │                              │──────────────────────►       │
    │                              │    Data page updated         │
```

* Steps 1–5 happen in the **hot path**: the client receives an acknowledgment as soon as the WAL commit record is durable. The actual data page is updated lazily during a **checkpoint** (step 6), keeping commit latency low.
* On crash recovery the engine replays WAL entries *after* the last checkpoint, restoring committed changes and discarding incomplete ones.
* **Lock-based concurrency** – A short-lived exclusive lock (row or page) blocks other writers, preserving isolation but possibly reducing concurrency.
* **MVCC (Multi-Version Concurrency Control)** – Instead of blocking, the engine keeps the *old* record version for readers while a new version is inserted for writers; this boosts read throughput at the cost of extra storage and version clean-up.
* Because only one object changes, the critical section is small, yet adopting the same ACID machinery keeps semantics uniform across *all* operations—large or tiny.

### Advanced Transaction Management

Complex workloads touch many independent resources—multiple tables, shards, or even distinct databases—so additional coordination layers are required.

#### Two-Phase Commit (2PC)

```
Coordinator                                   Participant(s)
┌───────────────────────────────┐        ┌────────────────────────────────┐
│ 1. PREPARE                    │        │ Receive PREPARE                │
│    (Ask participants to vote) │ ────►  │ Validate / Pre-commit          │
└───────────────────────────────┘        │                                │
            ▲                            │ Send VOTE (YES / NO)           │
            │                            └───────────────┬────────────────┘
            │                                            │
            └─────────────── 2. VOTES ◄──────────────────┘

                       Decision Phase
                           │
                           ▼

               ┌─────────────────────────┐
               │ 3. DECISION             │
               │                         │
               │ All YES  → COMMIT       │
               │ Any NO   → ROLLBACK     │
               └─────────────────────────┘
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


#### Savepoints

Savepoints let you **mark intermediate positions** inside a running transaction so you can roll back to that point without aborting the entire transaction.

```
Savepoints within a Transaction

  BEGIN
    │
    ├── INSERT INTO orders ...
    │
    ├── SAVEPOINT sp1 ◄──────────────── mark
    │     │
    │     ├── UPDATE inventory ...
    │     │
    │     └── (error) → ROLLBACK TO sp1   ◄── partial undo
    │
    ├── INSERT INTO backorders ...         ◄── continue normally
    │
    └── COMMIT                             ◄── everything except
                                                the rolled-back part
```

* **Nested recovery** – Savepoints are especially useful in stored procedures or ORM frameworks where an inner operation may fail but the outer transaction should survive.
* **Implementation** – Engines track enough transactional state to return to the savepoint boundary. Depending on the database, that may involve subtransactions, undo segments, or log records; `ROLLBACK TO` discards only the work performed after the savepoint.
* **Release** – `RELEASE SAVEPOINT sp1` discards the marker without rolling back, freeing engine resources.

### Concurrency Control Methods Comparison

| Method         | Underlying Mechanism                  | Pros                                                       | Cons                                                          | Typical Scenarios                                    |
| -------------- | ------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| **Locks**      | Pessimistic read/write locks          | Strong consistency; simple mental model                    | Blocking, deadlocks, lock-escalation overhead                 | OLTP systems where conflicts are frequent            |
| **MVCC**       | Append row versions + snapshot reads  | Readers never block writers; high read scalability         | Vacuuming/garbage collection; more I/O for version churn      | Mixed read-heavy workloads (PostgreSQL, InnoDB)      |
| **Timestamps** | Assign global time/order to Txns      | Easy to serialize logically; no blocking                   | High abort rate if contention; clock or logical-counter drift | In-memory or distributed DBs (Spanner, FoundationDB) |
| **Optimistic** | Validate at commit (compare‐and‐swap) | Near-zero overhead during read phase; suits low contention | Late failures waste work; write-write conflicts cause retries | Microservices or mobile apps with rare collisions    |
