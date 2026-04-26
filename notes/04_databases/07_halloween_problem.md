## Halloween Problem

The **Halloween Problem** is a database execution-plan issue where an `UPDATE` operation could theoretically update the same row more than once if the database scans rows through an access path that is changed by the update itself.

It was first observed by IBM System R researchers on October 31, 1976. The classic example is an update such as:

```sql
UPDATE employees
SET salary = salary * 1.10
WHERE salary < 50000;
```

If a naïve database engine scanned an index on `salary`, then increasing a row’s salary could move that row to a later position in the same index. The engine might then encounter the row again and apply the update a second time.

Example intended result:

```json
{
  "employee_id": 101,
  "old_salary": 45000,
  "new_salary": 49500,
  "updates_applied": 1
}
```

Example unsafe theoretical result:

```json
{
  "employee_id": 101,
  "old_salary": 45000,
  "new_salary": 54450,
  "updates_applied": 2
}
```

In modern relational databases, this is usually prevented by the query optimizer or execution engine. Databases such as PostgreSQL, SQL Server, Oracle, MySQL/InnoDB, and others have mechanisms that avoid repeatedly updating the same logical row during one statement.

So in normal application development, you usually do **not** need to manually protect every `UPDATE` statement from the Halloween Problem. It mainly matters when understanding execution plans, database internals, optimizer behavior, triggers, custom procedural loops, unusual update rules, or hand-written batching logic.

### Why It Happens Conceptually

The Halloween Problem happens when the database is both:

1. **Finding rows through an ordered access path**, such as an index.
2. **Changing a value that affects that same access path**, such as the indexed column.

Example table:

```sql
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  salary NUMERIC
);

CREATE INDEX idx_employees_salary ON employees(salary);
```

Risky-looking update:

```sql
UPDATE employees
SET salary = salary * 1.10
WHERE salary < 50000;
```

Conceptual unsafe scan:

```text
Salary index before update:

45000 -> employee 101
47000 -> employee 102
52000 -> employee 103
```

After employee `101` is updated:

```text
Salary index after first update:

47000 -> employee 102
49500 -> employee 101
52000 -> employee 103
```

If the engine were naïvely scanning forward through the same `salary` index, employee `101` could appear again at `49500`.

Modern engines avoid this by making sure each target row is identified and updated once.

### How Modern Databases Usually Prevent It

Modern databases typically insert protection automatically when an execution plan might be unsafe.

Common protections include:

#### 1. Spooling or Materialization

The database first stores the target row identifiers in an internal temporary structure, then updates those rows.

Conceptual plan:

```text
Find qualifying employee IDs
        |
        v
Store IDs in internal spool/worktable
        |
        v
Update employees by stable employee_id
```

Example internal target list:

```json
{
  "target_employee_ids": [101, 102]
}
```

Even if salary changes during the update, the database is no longer discovering new candidates from the changing salary index.

#### 2. Stable Row Identifiers

The database may scan one structure to find qualifying rows but update by a stable row identifier, such as a primary key, tuple ID, row ID, or internal physical locator.

Example:

```text
Scan finds:
employee_id = 101
employee_id = 102

Update phase uses those fixed identifiers.
```

This prevents the update from chasing rows as they move through an index.

#### 3. MVCC or Statement Snapshots

Many modern engines use MVCC, meaning readers see a stable snapshot while updates create new row versions.

Conceptually:

```text
Statement starts.
Scan sees snapshot S1.
Updates create new versions.
The scan does not rediscover its own new versions.
```

Example:

```json
{
  "read_snapshot": "statement_start",
  "updated_versions_visible_to_same_scan": false
}
```

This naturally separates the read view from the write effects of the same statement.

#### 4. Optimizer Plan Rewriting

The optimizer may choose a safer access path or rewrite the update plan to avoid scanning a changing index directly.

Example:

```json
{
  "detected_risk": "updated column participates in scan order",
  "optimizer_action": "use spool or safer access path"
}
```

This is why ordinary SQL updates are usually safe in mature database engines.

### When Developers Still Need to Care

Although modern databases usually handle the classic Halloween Problem, developers can still create similar issues through **custom logic**.

You should be careful when writing code that manually scans and updates rows in loops, especially when the update changes the same condition used to select the next batch.

#### Example: Custom Batch Loop Risk

Suppose a script repeatedly updates rows in batches:

```sql
UPDATE employees
SET salary = salary * 1.10
WHERE salary < 50000
ORDER BY salary
LIMIT 100;
```

Then the script runs this statement again and again until no rows match.

The database may protect each individual statement, but the **application loop** can still update the same row across multiple statements if the row still matches the condition after the first update.

Example:

```json
{
  "employee_id": 101,
  "salary_after_batch_1": 49500,
  "still_matches_condition": true,
  "salary_after_batch_2": 54450
}
```

This is not the classic engine-level Halloween Problem inside one statement. It is a similar application-level batching bug.

Safer pattern:

```sql
CREATE TEMP TABLE raise_targets AS
SELECT employee_id
FROM employees
WHERE salary < 50000;

UPDATE employees
SET salary = salary * 1.10
WHERE employee_id IN (
  SELECT employee_id FROM raise_targets
);
```

This fixes the candidate set before running the update.

#### Example: Triggers or Rules

Custom database triggers can also create repeated or unexpected updates if they modify rows that are part of the same logical operation.

Example risky trigger idea:

```sql
CREATE TRIGGER adjust_salary_again
AFTER UPDATE ON employees
FOR EACH ROW
WHEN (NEW.salary < 50000)
EXECUTE FUNCTION apply_extra_raise();
```

If the trigger updates the same table again, it can create recursive or repeated modifications unless carefully controlled.

Example protection:

```json
{
  "trigger_recursion_guard": true,
  "max_trigger_depth": 1,
  "updates_allowed_once": true
}
```

Triggers should be designed with clear recursion limits and conditions.

#### Example: Queue Processing

Queue tables can have Halloween-like bugs if workers repeatedly select “next available” rows while also changing the fields used to select those rows.

Risky pattern:

```sql
SELECT job_id
FROM jobs
WHERE status = 'pending'
ORDER BY priority
LIMIT 1;
```

Then:

```sql
UPDATE jobs
SET priority = priority + 1
WHERE job_id = ?;
```

If the job remains `pending`, it may be selected again later.

Safer pattern:

```sql
UPDATE jobs
SET status = 'processing'
WHERE job_id = ?
RETURNING job_id;
```

Or select and claim atomically:

```sql
UPDATE jobs
SET status = 'processing'
WHERE job_id = (
  SELECT job_id
  FROM jobs
  WHERE status = 'pending'
  ORDER BY priority
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
RETURNING job_id;
```

Example output:

```json
{
  "job_id": 42,
  "old_status": "pending",
  "new_status": "processing",
  "can_be_selected_again_as_pending": false
}
```

### Practical Rule of Thumb

For normal single-statement SQL updates in modern relational databases, the Halloween Problem is mostly handled by the engine.

The practical risk today is usually in:

```text
Custom batching loops
Triggers and recursive rules
Queue-processing logic
Manual cursor-based updates
Stored procedures that repeatedly scan and mutate the same condition
Unusual execution plans in custom engines or embedded systems
```

A safe design principle is:

```text
If you are repeatedly scanning rows and updating the same fields that decide which rows are scanned next,
freeze the target row IDs first.
```

### Safe Pattern: Freeze the Candidate Set

The most practical developer-level defense is to first capture stable primary keys, then update by those keys.

```sql
CREATE TEMP TABLE target_employees AS
SELECT employee_id
FROM employees
WHERE salary < 50000;
```

Then:

```sql
UPDATE employees
SET salary = salary * 1.10
WHERE employee_id IN (
  SELECT employee_id
  FROM target_employees
);
```

Example:

```json
{
  "target_set_fixed_before_update": true,
  "updated_by_stable_primary_key": true,
  "same_row_updated_multiple_times": false
}
```

This pattern is useful for migrations, backfills, batch jobs, stored procedures, and scripts where repeated scans could otherwise change their own future input.
