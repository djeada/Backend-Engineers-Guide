## Isolation Levels

Isolation levels in relational database systems control how transactions perceive and interact with data changes made by other concurrent transactions. They define a spectrum of guarantees regarding data visibility, consistency, and concurrency. By selecting the right isolation level, one balances consistency requirements (making sure data correctness) with performance (allowing more parallelism). This document covers the primary SQL isolation levels, how they manifest in different database engines, and includes ASCII diagrams illustrating read phenomena and transaction overlap. Code snippets in SQL demonstrate how to set isolation levels and test their behavior.

### Introduction to Transaction Isolation  

A **transaction** in a database groups multiple reads or writes into a single logical unit, making sure atomicity (all-or-nothing) and consistency. Isolation makes sure each transaction’s intermediate states remain hidden from other concurrent transactions, or at least controlled by the chosen isolation level. Durability, the “D” in ACID, concerns making sure that once a transaction commits, changes survive system failures.

#### The "ACID" Properties  

- **Atomicity**: All operations in a transaction succeed or fail together.  
- **Consistency**: A transaction brings the database from one valid state to another.  
- **Isolation**: Operations within a transaction do not interfere improperly with operations in other concurrent transactions.  
- **Durability**: Once a transaction commits, changes persist even if the system crashes.

Isolation levels primarily address how “consistent” or “fresh” data is in the face of concurrent changes. The SQL standard defines four standard isolation levels:

I. **Read Uncommitted**  

II. **Read Committed**  

III. **Repeatable Read**  

IV. **Serializable**

However, actual implementations can differ across database systems.

### Concurrency Phenomena  

#### Dirty Reads  

A “dirty read” occurs when one transaction reads data written by another transaction that has not yet committed. If that other transaction rolls back, the first transaction has acted on invalid or temporary data.

#### Non-Repeatable Reads  

A “non-repeatable read” occurs if a transaction reads the same row twice and sees different data each time, because another transaction modified the row in between.

#### Phantom Reads  

A “phantom read” involves a transaction re-executing a query that retrieves a range of rows and seeing additional (or fewer) rows appear compared to the first read, even though the range condition is the same. Another transaction may have inserted or deleted rows in that range.

The following ASCII diagram provides a high-level view of how concurrency can introduce these anomalies:

```
                Transaction A                     Transaction B
     Time
       | -------------- Begin -------------       (Doesn't matter here)
       |
 (1)   |   SELECT COUNT(*) FROM employees
       |     -> sees 100 rows
       |
 (2)   |                                       INSERT INTO employees (name) VALUES ('New Hire')
       |                                               (commit changes)
       |
 (3)   |   SELECT COUNT(*) FROM employees
       |     -> sees 101 rows (Phantom read)
       |
       | ---------------- End -------------
       v
```

Transaction A sees different results for the same “range” query because Transaction B inserted a row in that time window. This is one example of a phantom read phenomenon.

### Isolation Level Definitions  

#### 1. Read Uncommitted  

**Allows**: Dirty reads, non-repeatable reads, phantom reads.  
**Usage**: Rare; some DBs treat it the same as Read Committed.  
**Behavior**: Transactions can see uncommitted data from other transactions, which may lead to incorrect or inconsistent results if those other transactions roll back.

In practice, many database engines do not provide a pure Read Uncommitted mode; instead, they use Read Committed but do not lock rows being read.

#### 2. Read Committed  

**Allows**: Non-repeatable reads, phantom reads.  
**Prevents**: Dirty reads.  
**Behavior**: Only committed data is visible to a transaction. Each statement sees the latest committed data at the time it runs, so subsequent statements might see updates committed after the transaction began.

##### Example: Non-Repeatable Read in Read Committed  

```
Transaction A:                Transaction B:
BEGIN;                         -- (some time later)
SELECT salary FROM employees
  WHERE emp_id = 10;  -- sees salary = 50000

                              BEGIN;
                              UPDATE employees
                                SET salary = 55000
                              WHERE emp_id = 10;
                              COMMIT;  -- now salary is 55000
                              
SELECT salary FROM employees
  WHERE emp_id = 10;  -- might see salary = 55000
COMMIT;
```

Transaction A sees different salary values in two separate queries within the same transaction because transaction B committed in between.

#### 3. Repeatable Read  

**Allows**: Phantom reads (depending on DB engine, but often mitigated).  
**Prevents**: Dirty reads, non-repeatable reads.  
**Behavior**: Makes sure that if a row is read multiple times within one transaction, the data in that row remains stable. The transaction sees a consistent snapshot of each row. Phantom rows, however, can still appear or disappear if new rows are inserted or deleted that meet the same search condition.

In some engines (like MySQL’s InnoDB in default Repeatable Read mode), phantom reads are also prevented by a combination of row-level locking and gap locks. In others, only full “Serializable” prevents phantoms.

#### 4. Serializable  

**Allows**: Typically none of the above anomalies (dirty reads, non-repeatable reads, phantoms).  
**Behavior**: Transactions run as though they are serially executed, one after another. The DB might use extra locks or validation to make sure no conflicts occur that break the illusion of a serial schedule. This can significantly reduce concurrency if many concurrent transactions update overlapping data ranges.

```
+--------------------------------+
|  Isolation Level vs. Phenomena |
+--------------------+-----------+
| Level             | Dirty  Reads?  Non-Repeatable  Reads?  Phantom  Reads?  |
|-------------------|----------------|------------------------|----------------|
| Read Uncommitted  | Allowed        | Allowed                | Allowed        |
| Read Committed    | Prevented      | Allowed                | Allowed        |
| Repeatable Read   | Prevented      | Prevented             | Allowed*       |
| Serializable      | Prevented      | Prevented             | Prevented      |
+-------------------+----------------+------------------------+----------------+
```

(*In some DBs, Repeatable Read also prevents phantoms, e.g., MySQL InnoDB.)

### Isolation Levels in Popular Databases  

#### PostgreSQL  

- **Default**: Read Committed.  
- **Other**: Repeatable Read, Serializable.  
- **Read Uncommitted** is treated the same as Read Committed.  

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- Or
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

```

#### MySQL (InnoDB)  

- **Default**: REPEATABLE READ.  
- **Other**: READ COMMITTED, READ UNCOMMITTED, SERIALIZABLE.  
- **Phantoms**: InnoDB’s repeatable read usually includes next-key locks that prevent phantoms for typical statements.  

```sql
SET GLOBAL tx_isolation = 'REPEATABLE-READ';
SET SESSION tx_isolation = 'READ-COMMITTED';
```

#### SQL Server  

- **Default**: READ COMMITTED.  
- **Other**: READ UNCOMMITTED, REPEATABLE READ, SNAPSHOT, SERIALIZABLE.  
- **Snapshot** is not part of the original SQL standard but is similar to REPEATABLE READ (with some extra concurrency benefits).  

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

#### Oracle  
- **Default**: READ COMMITTED.  
- **Other**: SERIALIZABLE.  
- **Repeatable Read** is absent in Oracle; `SERIALIZABLE` in Oracle is somewhat akin to Repeatable Read with potential phantom protection.  
- **Read Uncommitted** is effectively the same as Read Committed in Oracle.

### ANSI SQL Commands for Isolation Levels  

```

SET TRANSACTION ISOLATION LEVEL 
    { READ UNCOMMITTED | READ COMMITTED 
    | REPEATABLE READ | SERIALIZABLE };

```

A transaction must be in progress or started right after this statement, depending on the DB engine’s specifics.  

**Example**:
```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Perform queries/updates here...
COMMIT;
```

Or sometimes one can do:
```sql
START TRANSACTION ISOLATION LEVEL READ COMMITTED;

```
Implementation details vary by vendor.


### Illustrating Isolation Levels with an Example  

Consider two transactions operating on a bank’s `accounts` table. The table has `acct_id`, `balance`, and so forth. We illustrate how each isolation level handles concurrent updates:

#### Dirty Read Scenario (Read Uncommitted)  
```

Transaction A                       Transaction B
--------------------------------    --------------------------------
BEGIN;                              BEGIN;
UPDATE accounts
  SET balance = balance - 100
  WHERE acct_id = 1;        -- uncommitted

-- T-A not committed yet
                                  SELECT balance
                                  FROM accounts
                                  WHERE acct_id = 1;  -- sees reduced balance (dirty read)

ROLLBACK;  -- T-A rollback, so no real change
                                  -- T-B has used invalid data in its logic

```

Transaction B read a value that was never committed by A.

#### Non-Repeatable Read in Read Committed  

```

Transaction A                       Transaction B
--------------------------------    --------------------------------
BEGIN;
SELECT balance FROM accounts
  WHERE acct_id = 1;  -- sees 1000

                                 BEGIN;
                                 UPDATE accounts
                                   SET balance = 1200
                                 WHERE acct_id = 1;
                                 COMMIT; -- new balance is 1200

SELECT balance FROM accounts
 WHERE acct_id = 1;  -- now sees 1200
COMMIT;
```

Transaction A’s second read sees a different value. Non-repeatable read is possible in Read Committed.

#### Phantom Rows in Repeatable Read  

```

Transaction A                      Transaction B
--------------------------------   --------------------------------
BEGIN;
SELECT * FROM orders
  WHERE order_date >= '2025-01-01' 
  AND order_date < '2025-02-01';  
-- Suppose 10 rows returned

                               BEGIN;
                               INSERT INTO orders(...)
                               WHERE order_date='2025-01-15';
                               COMMIT;

SELECT * FROM orders
  WHERE order_date >= '2025-01-01'
  AND order_date < '2025-02-01';
-- Now 11 rows if the engine doesn't block phantoms
COMMIT;
```

Transaction A sees a new row that meets the same condition. This is a phantom read.

#### Serializable - Avoiding Phantoms  

With **Serializable**, the engine (through locking or multi-version concurrency control) makes sure the second SELECT sees the same set of rows or else one transaction is forced to rollback due to conflict. Thus, no additional row can sneak in between consistent reads.

### Performance and Locking Overheads  

#### Row-Level and Range Locks  
To enforce higher isolation, databases may lock rows (or even entire ranges) to prevent concurrent inserts or updates that would cause anomalies. At higher isolation levels, you might see more lock waits and potential deadlocks, especially if transactions are long-running.

#### Snapshot Isolation  
Some DBs (like PostgreSQL, Oracle, SQL Server with snapshot, MySQL with MVCC) rely heavily on versioned data rather than extensive locks. A transaction sees a consistent snapshot from the time it starts (or statement start). This reduces blocking, but can still lead to concurrency errors if two transactions modify overlapping data sets under serializable conditions.

#### Deadlocks  
As isolation rises, so does the risk of deadlocks—two or more transactions waiting on each other’s locks. Databases typically detect and resolve deadlocks by aborting one transaction.


### Choosing the Right Isolation Level  

I. **Read Uncommitted**: Rarely recommended. Possibly used for certain analytics or specialized workloads where “dirty data” is acceptable.  
II. **Read Committed** (Default in many systems): Good compromise, preventing dirty reads but allowing non-repeatable reads and phantoms.  
III. **Repeatable Read**: Makes sure consistent row reads within a transaction. Good for consistent aggregations or when you must rely on stable row data. In some systems (like MySQL InnoDB), it also prevents phantoms effectively.  
IV. **Serializable**: The safest but can drastically limit concurrency, leading to more contention and potential rollbacks. Typically used if absolute correctness is important (financial transactions with complicated constraints, for example).

**Rule of Thumb**: Start with the default (often Read Committed or Repeatable Read) and only move to higher isolation if you truly need the extra consistency guarantees.

### Practical Examples  

#### PostgreSQL Example: Testing Non-Repeatable Read vs. Repeatable Read

```sql
-- Setup
CREATE TABLE test_balance (
  id   SERIAL PRIMARY KEY,
  bal  INT
);
INSERT INTO test_balance (bal) VALUES (1000);

-- Session A (terminal A)
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT bal FROM test_balance WHERE id=1;   -- sees 1000
-- do not commit yet...

-- Session B (terminal B)
BEGIN;
UPDATE test_balance SET bal=1100 WHERE id=1;
COMMIT;  -- changes from 1000 -> 1100

-- Back to Session A
SELECT bal FROM test_balance WHERE id=1;   -- sees 1100 now, non-repeatable read
COMMIT;
```

If we had set `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;` for Session A, the second SELECT might still read 1000 in a pure snapshot-based system (unless the database specifically prevents phantoms but not non-repeatable reads under Repeatable Read).  

#### SQL Server: Checking Transaction Isolation

```sql
-- Check current isolation
SELECT CASE transaction_isolation_level
  WHEN 0 THEN 'Unspecified'
  WHEN 1 THEN 'Read Uncommitted'
  WHEN 2 THEN 'Read Committed'
  WHEN 3 THEN 'Repeatable Read'
  WHEN 4 THEN 'Serializable'
  WHEN 5 THEN 'Snapshot'
  END AS IsolationLevel
FROM sys.dm_exec_sessions
WHERE session_id = @@SPID;

-- Change isolation
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRAN;
-- do queries
COMMIT;

```

#### MySQL: Show and Change Global/Session Settings

```sql
-- Check current isolation level
SHOW VARIABLES LIKE 'tx_isolation';
-- or for newer versions: 'transaction_isolation'

-- Change globally (needs privileges, affects new connections only)
SET GLOBAL transaction_isolation = 'READ-COMMITTED';

-- Change session
SET SESSION transaction_isolation = 'READ-COMMITTED';
```

### Common Pitfalls and Tips  

I. **Long Transactions**: Higher isolation plus lengthy transactions can hold locks for an extended period, blocking other updates or leading to deadlocks. Keep transactions as short as possible.  

II. **Phantom Handling**: Some systems auto-block phantoms at Repeatable Read, others do not. Test your specific engine’s documentation and behavior.  

III. **Row vs. Table Locking**: Some older systems or specific workloads might escalate to table-level locks under high concurrency, harming performance.  

IV. **Snapshot vs. Repeatable Read**: Snapshot isolation in SQL Server or Oracle may not exactly match the ANSI definition of Repeatable Read. Validate your DB’s actual concurrency model.  

V. **Read-Only Transactions**: Some engines optimize read-only transactions by skipping certain lock overhead if they never modify data.  

VI. **SERIALIZABLE Rollbacks**: If the DB detects a conflict that would break the illusion of serial execution, it may force one transaction to rollback with an error. Client code must handle these retry scenarios gracefully.
