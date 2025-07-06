## Isolation Levels

Isolation levels in relational-database systems govern how simultaneously running transactions perceive one another’s changes. They sit on a spectrum that trades **consistency guarantees**—how “correct” every read is—against **concurrency**—how many transactions can safely overlap. Choosing the right level is therefore a tuning exercise: too little isolation risks logical errors; too much sacrifices throughput and invites blocking or rollbacks.

### Introduction to Transaction Isolation

A **transaction** bundles multiple SQL statements into a single, atomic unit of work: either every statement’s effect is made permanent, or none are. Isolation ensures that the *partially complete* state of one transaction never leaks in ways that would confuse another. Durability, the “D” of ACID, then locks in those committed changes so that even power failures or crashes cannot erase them.

#### The "ACID" Properties

* **Atomicity** – The transaction’s individual steps are inseparable; all succeed or all fail together.
* **Consistency** – Every commit must leave the database in a valid state that honors all constraints, cascades, and invariants.
* **Isolation** – Concurrent transactions cannot step on each other’s toes; each proceeds as if it were the sole user, within the chosen level.
* **Durability** – Once the commit command returns, data is irreversibly logged or flushed so that recovery will replay it.

Isolation levels chiefly shape the *visibility* dimension of consistency. The SQL standard formally names four:

I. **Read Uncommitted**  

II. **Read Committed** 

III. **Repeatable Read**  

IV. **Serializable**

Real-world engines often extend or tweak these definitions.

### Concurrency Phenomena

#### Dirty Reads

A transaction fetches data written by another that has not yet committed; if the writer later rolls back, the reader has relied on nonsense.

#### Non-Repeatable Reads

A transaction reads the *same* row twice but gets two different versions because some concurrent transaction committed an update in between.

#### Phantom Reads

A re-issued range query returns a *different set of rows*—new inserts or deletes qualify—even though the predicate is unchanged.

```
                Transaction A                          Transaction B
     Time
       | ------------ BEGIN ------------              (anytime)
  (1)  |   SELECT COUNT(*) FROM employees;
       |     → 100 rows
  (2)  |                                           INSERT INTO employees VALUES ('New Hire');
       |                                                 COMMIT;
  (3)  |   SELECT COUNT(*) FROM employees;
       |     → 101 rows  (phantom)
       | ------------- END -------------
       v
```

### Isolation Level Definitions

#### 1. Read Uncommitted

**Allows**: Dirty, non-repeatable, phantom reads.
**Behavior**: Statements can see data still in limbo; excellent throughput, terrible reliability. Many vendors quietly upgrade it to Read Committed by still hiding uncommitted writes in row-versioned engines.

#### 2. Read Committed

**Prevents**: Dirty reads.
**Allows**: Non-repeatable and phantom reads.
**Behavior**: Every statement gets the *latest committed value* at its start time, so successive statements may observe newer versions.

##### Example: Non-Repeatable Read

```
Tx A                                Tx B
BEGIN;                              ———
SELECT salary FROM emp WHERE id=10;   -- 50 000
                                    BEGIN;
                                    UPDATE emp SET salary=55 000 WHERE id=10;
                                    COMMIT;
SELECT salary FROM emp WHERE id=10;   -- 55 000
COMMIT;
```

#### 3. Repeatable Read

**Prevents**: Dirty reads, non-repeatable reads.
**Allows**: Phantoms (though some engines—MySQL InnoDB, SAP HANA—block them with gap or next-key locks).
**Behavior**: The *snapshot* of any row stays frozen for the whole transaction. Inserts into still-unlocked gaps may slip through unless extra range locks or MVCC tricks stop them.

#### 4. Serializable

**Prevents**: Dirty, non-repeatable, and phantom reads.
**Behavior**: Each transaction executes as if in a strictly serial schedule. Implementations choose between heavy locking (two-phase locking) and optimistic validation (snapshot isolation plus conflict checks). Either technique may force rollbacks when overlap would break serial order.

```
+--------------------------------+
| Isolation vs. Anomalies        |
+----------------+-----+-----+----+
| Level          |Dirty|NR  |Phan|
|----------------+-----+-----+----|
| Read Uncommitted| ✔  | ✔  | ✔ |
| Read Committed  | ✘  | ✔  | ✔ |
| Repeatable Read | ✘  | ✘  | ✔*|
| Serializable    | ✘  | ✘  | ✘ |
+----------------+-----+-----+----+
(*May be blocked in some engines)
```

### Isolation Levels in Popular Databases

#### PostgreSQL

* **Default**: Read Committed.
* **Higher**: Repeatable Read, Serializable (SSI algorithm).
* **Lower**: Read Uncommitted maps to Read Committed; MVCC hides uncommitted rows anyway.

```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

#### MySQL (InnoDB)

* **Default**: Repeatable Read.
* **Others**: Read Committed, Read Uncommitted, Serializable.
* **Phantoms**: Blocked via next-key locks in most common cases.

```sql
SET SESSION transaction_isolation = 'READ COMMITTED';
```

#### SQL Server

* **Default**: Read Committed.
* **Extras**: Snapshot (MVCC-based) and Read Committed Snapshot.
* **Serializable**: Two-phase locking unless Snapshot is enabled, in which case it validates at commit.

```sql
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
```

#### Oracle

* **Default**: Read Committed (with MVCC).
* **Serializable**: Provides repeatable reads with predicate locking; Oracle treats Read Uncommitted as Read Committed.
* **Repeatable Read**: Not exposed separately.

### ANSI SQL Commands for Isolation Levels

```sql
SET TRANSACTION ISOLATION LEVEL 
    READ UNCOMMITTED | READ COMMITTED |
    REPEATABLE READ  | SERIALIZABLE;
```

Issue either inside an open transaction or immediately before `BEGIN`, per vendor rules.

### Illustrating Isolation Levels with an Example

#### Dirty Read (Read Uncommitted)

```
Tx A                                   Tx B
BEGIN;                                 BEGIN;
UPDATE acct SET bal = bal - 100 WHERE id=1;
-- uncommitted write                   SELECT bal FROM acct WHERE id=1;  -- dirty
ROLLBACK;                              — uses bogus balance —
```

#### Non-Repeatable Read (Read Committed)

```
Tx A                                   Tx B
BEGIN;                                 —
SELECT bal FROM acct WHERE id=1;  -- 1000
                                      UPDATE acct SET bal=1200 WHERE id=1; COMMIT;
SELECT bal FROM acct WHERE id=1;  -- 1200
COMMIT;
```

#### Phantom Rows (Repeatable Read)

```
Tx A                         Tx B
BEGIN;                       —
SELECT * FROM orders
 WHERE date BETWEEN '2025-01-01' AND '2025-01-31'; -- 10 rows
                              INSERT INTO orders VALUES ('2025-01-15', …); COMMIT;
SELECT * FROM orders
 WHERE date BETWEEN '2025-01-01' AND '2025-01-31'; -- 11 rows
COMMIT;
```

#### Serializable – No Phantoms

Under Serializable, Tx B would block or Tx A would abort to preserve a serial order.

### Performance and Locking Overheads

* **Row & Range Locks**: Higher isolation can pin more rows longer, increasing wait times and deadlock probability.
* **Snapshot Isolation**: MVCC engines (PostgreSQL, Oracle, SQL Server snapshot) favor *version reads* over blocking, but still validate write overlaps at commit.
* **Deadlocks**: More locks + longer lifetimes → greater risk; engines automatically pick a victim to roll back.

### Choosing the Right Isolation Level

I. **Read Uncommitted** – Diagnostics or ETL where stale or transient data is acceptable. Rarely used.

II. **Read Committed** – Safe default that eliminates dirty reads yet scales well.

III. **Repeatable Read** – Critical when multiple selects must agree on row values; good for financial summaries.

IV. **Serializable** – Regulatory or business rules require absolute correctness; expect more contention and occasional retry logic.

**Rule of Thumb**: Start with the vendor’s default, profile real workloads, then escalate only where tests prove anomalies would harm correctness.

### Practical Examples

PostgreSQL – Demonstrating Non-Repeatable vs. Repeatable Read:

```sql
-- Session A
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT bal FROM test_balance WHERE id = 1;  -- 1000

-- Session B
BEGIN;
UPDATE test_balance SET bal = 1100 WHERE id = 1;
COMMIT;

-- Session A again
SELECT bal FROM test_balance WHERE id = 1;  -- still 1000
COMMIT;
```

SQL Server – Checking Isolation:

```sql
SELECT transaction_isolation_level
FROM sys.dm_exec_sessions
WHERE session_id = @@SPID;  -- returns 0–5 per MSDN table
```

MySQL – Viewing / Changing Isolation:

```sql
SHOW VARIABLES LIKE 'transaction_isolation';
SET SESSION transaction_isolation = 'SERIALIZABLE';
```

### Common Pitfalls and Tips

I. **Long Transactions** – Hold locks or versions longer; keep business logic outside the transaction where possible.

II. **Phantom Handling** – Verify whether your engine blocks phantoms at Repeatable Read; assumptions differ.

III. **Lock Escalation** – Some systems upgrade many row locks to a table lock; monitor and tune thresholds.

IV. **Snapshot vs. Repeatable Read** – Do not conflate them: snapshot may allow write-skew anomalies absent in true Repeatable Read.

V. **Read-Only Transactions** – Declare `SET TRANSACTION READ ONLY` to let the optimizer skip superfluous locks or validation.

VI. **Serializable Rollbacks** – Code retry loops around `SerializationFailure` errors; this is normal, not a bug.
