## Halloween Problem

The Halloween Problem is a notorious pitfall in relational‐database execution plans. First observed by IBM System R researchers on **October 31, 1976**—hence the spooky nickname—the phenomenon occurs when an `UPDATE` statement unwittingly revisits and modifies the same row more than once. Each extra pass can inflate numeric columns, duplicate work, or otherwise corrupt results, so modern optimizers build in explicit defenses. Nevertheless, the problem remains a classic illustration of how row ordering and side effects can interact inside a seemingly simple set operation.

### Nature of the Halloween Problem

The crux of the issue is **state-dependent scanning**: if the executor reads rows through an index whose **key contains the column being updated**, the mutation can reposition that row inside the index, making it visible again later in the scan. Without extra safeguards, the engine has no memory that the tuple was already processed.

A textbook example is granting a 10 % raise to employees earning under \$50 000:

```sql
UPDATE employees
   SET salary = salary * 1.10
 WHERE salary < 50000;
```

An employee starting at \$45 000 climbs to \$49 500 after the first pass—still under the threshold—so the cursor notices the row again and applies yet another 10 % bump. In a naïve plan, the loop continues until the row finally exits the qualifying range (or, in degenerate cases, forever).

### Intermediate Table Method

This classic remedy freezes the qualifying set in an auxiliary structure, turning the original scan into a **read-only** operation:

1. **Extract phase** – Copy every row that meets the `WHERE` predicate into a worktable (e.g., a spool, temporary table, or materialized CTE).
2. **Transform phase** – Apply the `UPDATE` solely to that worktable, guaranteeing each row changes exactly once.
3. **Merge phase** – Write the modified rows back to the base table in one, atomic operation, usually inside the same transaction for consistency.

```
Original Table                    Worktable                     Original Table
+-------------+                  +-------------+                +-------------+
| Row 1       |  1) Extract ---> | Row 1       |                | Row 1*      |
| Row 2       |                  | Row 3       |  2) Update --> | Row 2       |
| Row 3       |                  | Row 5       |                | Row 3*      |
| Row 4       |                  +-------------+                | Row 4       |
| Row 5       |                                                 | Row 5*      |
+-------------+                                                 +-------------+
       ^                                                               |
       |___________________ 3) Merge / Insert _________________________|
```

The extra I/O can be significant, so many engines insert this spool only when the optimizer detects the risk automatically.

### Indexing Strategies

Selecting an access path **orthogonal to the updated column** breaks the feedback loop:

1. A **non-clustered index** that stores a pointer (RID) to the heap remains logically ordered even after the row’s payload columns change.
2. When the optimizer drives the scan through that index, each RID is visited once and cannot reappear.
3. By contrast, a **clustered index** or any index whose key includes the updated column will physically relocate the record, allowing a naïve scan to see it twice.

```
Base Table (heap)                 Non-Clustered Index
+----------------------+          +------------------+
| RID 101 Data A       | <----+   | Key A -> RID 101 |
| RID 102 Data B       |      |   | Key B -> RID 102 |
| RID 103 Data C       |  Update   | Key C -> RID 103 |
| RID 104 Data D       | -------+  | Key D -> RID 104 |
| RID 105 Data E       |          | Key E -> RID 105 |
+----------------------+          +------------------+
      ^     ^                             ^
      |     |_____________________________|
      |              Lookup
      |  (Each RID visited exactly once)
```

Extra non-clustered indexes speed reads but slow writes, so DBAs must balance mitigation against maintenance cost.

### Isolation Levels

ANSI isolation levels can also shield a statement from revisiting modified rows:

1. **Serializable** guarantees the transaction behaves as though it ran alone, blocking or versioning away rows that could alter the result set mid-scan.
2. **Repeatable Read** prevents other sessions from changing rows you have touched, but it does not stop your own update from making a row newly qualify, so some Halloween cases persist.
3. Implementations enforce these rules via locks or row-versioning; the stronger the level, the greater the contention or version-store growth.

```
 Transaction 1 (Serializable)      Transaction 2
+-----------------------------+   +-------------------------+
| 1. Read Row 1               |   | 1. Blocked on Row 1     |
| 2. Update Row 1             |   |                         |
| 3. Commit                   |   | 2. Read Row 1           |
+-----------------------------+   | 3. Update Row 1         |
                                   | 4. Commit               |
                                   +-------------------------+
          ^                                      ^
          |_____________ strict snapshot ________|
```

High isolation removes the glitch but can throttle throughput on busy, write-heavy tables.

### Database Engine Optimization

Modern DBMSs implement several **automatic** defenses:

1. **MVCC / Row versioning** writes new row images rather than updating in place, so the scan sees only the snapshot taken at statement start.
2. **Snapshot isolation** freezes the candidate set on first read.
3. **Plan rewriting** can inject an implicit spool, switch to a safer index, or add a hash filter of processed keys.
4. **Adaptive locking** escalates from row to page only when needed, minimizing the concurrency penalty.

Because each vendor differs, always test critical updates under production-like loads.

### Order by Primary Key

Running the update in a **stable key order** eliminates back-tracking:

1. Adding `ORDER BY <primary_key>` forces the executor to process rows in ascending (or descending) primary-key sequence, which by definition never changes within the statement.
2. Once a row is past the cursor, even large attribute changes cannot cause it to reappear.

```
+----------------------------+
| Table: employees           |
+----------------------------+
| PK 1  salary 45000         |
| PK 2  salary 47000         |  --+
| PK 3  salary 48000         |    | Cursor direction
| PK 4  salary 49000         |    |  (ascending PK)
| PK 5  salary 49500         |    |
+----------------------------+    v
             |                    +----------------------------------+
             |  UPDATE ...        | After pass:                      |
             |  ORDER BY PK       +----------------------------------+
             |                    | 1  49500 (was 45000)             |
             |                    | 2  51700 (was 47000)             |
             v                    | 3  52800 (was 48000)             |
+----------------------------+    | 4  53900 (was 49000)             |
| Executor scans once only   |    | 5  54450 (was 49500)             |
+----------------------------+    +----------------------------------+
```

A supporting index on the key avoids a full-table scan and external sort, keeping the remedy performant.

### Locking Mechanisms

Finally, explicit **pessimistic locks** guarantee a row is updated exactly once in a transaction:

1. `SELECT ... FOR UPDATE` (or equivalent) takes an exclusive latch on each qualifying row.
2. Because even the same transaction cannot reacquire a lock it already owns, a self-inflicted Halloween loop is impossible.
3. Deadlocks loom if concurrent writers lock rows in different orders, so pair locking with a deterministic scan strategy.

```
+--------------------------+         +----------------------+
| Txn A (holds Lock)       |         | Txn B (waiting)      |
+--------------------------+         +----------------------+
| 1. SELECT ... FOR UPDATE |   -->   | 1. Blocks on same row|
| 2. UPDATE Row            |         |                      |
| 3. COMMIT (release)      |         | 2. Gains lock        |
+--------------------------+         | 3. UPDATE Row        |
                                     | 4. COMMIT            |
                                     +----------------------+
```

Locks are easy to reason about but can throttle high-throughput workloads, so use them judiciously alongside the other, less intrusive techniques.
