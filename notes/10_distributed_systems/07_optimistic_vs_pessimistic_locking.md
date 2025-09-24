## Optimistic vs. Pessimistic Locking

Locking is about managing concurrent access to shared data. Engineers often make it sound harder than it is, but the core idea is simple: choose between optimistic or pessimistic approaches depending on how costly retries are.

* **Optimistic Lock → Application-level control**
* **Pessimistic Lock → Database-level control**

**Optimistic = “trust first, verify at the end.”**

Analogy: Editing a shared whiteboard snapshot. Imagine you take a picture of a whiteboard, add your ideas, and then return to update the board. If someone else has already changed it, you notice the mismatch and must reapply your changes.

**Pessimistic = “reserve first, then act.”**

Analogy: Using a single restroom stall. Once the door is locked, nobody else can enter until it’s unlocked. This prevents awkward collisions but can create a line.

**Rule of thumb**

* When do-overs are **quick and low-cost**, lean on **Optimistic Locking**.
* When do-overs are **slow, risky, or expensive**, rely on **Pessimistic Locking**.

✅ After reading this, you should be able to explain:

1. What optimistic and pessimistic locks are, and how they differ.
2. Why optimistic locks are app-level and pessimistic locks are DB-level.
3. The retry vs. blocking trade-off.
4. Which strategy fits different workloads (cheap retry vs. expensive retry).
5. How to avoid deadlocks when using pessimistic locking.

### Conceptual Diagram

We’re looking at how two users, A and B, interact with the same database record using two different locking strategies.

```
[Resource: Record X]

Optimistic Lock:
   |-- User A edits freely
   |-- User B edits freely
   |
   |-- Both try to save
   |-- Conflict check (timestamps / version numbers)
   |-- One succeeds, the other retries

Pessimistic Lock:
   |-- User A begins edit --> Database locks record
   |-- User B tries to edit --> Must wait
   |
   |-- Lock released after User A commits/rolls back
```

Optimistic locking lets multiple users edit the same record at the same time without restrictions. Each user works with their own copy, and only when they try to save does the system check for conflicts using a version number or timestamp. If no changes have happened since the user started editing, the save goes through; if another user has already updated the record, the save fails and the user must reload and try again. In contrast, pessimistic locking places an immediate lock on the record as soon as the first user begins editing. While the lock is active, no other user can make changes—anyone who tries has to wait until the first user commits or cancels their update. This guarantees consistency by blocking conflicts up front but also reduces concurrency.

### Understanding Optimistic Locking

Optimistic locking assumes **conflicts are rare**.
Instead of blocking others, each transaction works independently, and a conflict check happens **only at commit time**.

* Typically implemented using **version columns** or **timestamps**.
* If data has changed since you read it, your update fails, and you must retry.
* Works best in **read-heavy systems** where collisions are infrequent and retries are inexpensive.

**Example scenario:**
An e-commerce website where many users browse and occasionally update their shopping carts. Since collisions are rare, optimistic control avoids unnecessary blocking.

**Code sample (application-level check):**

```sql
-- Table has 'version' column
UPDATE Products
SET Stock = Stock - 1, version = version + 1
WHERE ProductID = 42 AND version = 7;
-- Update succeeds only if version hasn’t changed
```

### Exploring Pessimistic Locking

Pessimistic locking assumes **conflicts are likely**.
It prevents them by blocking others at the database level as soon as one transaction begins.

* Typically implemented with `SELECT … FOR UPDATE` or row/table locks.
* Guarantees no one else can read/write until the lock is released.
* Works best in **write-heavy or critical systems** where retries are too costly.

**Example scenario:**
A banking system transferring money. Losing or retrying a transfer is expensive, so the database enforces strict locks.

**Code sample (database-level lock):**

```sql
BEGIN TRANSACTION;
SELECT * FROM Accounts WHERE AccountID = 123 FOR UPDATE;
-- Row is locked until commit/rollback
UPDATE Accounts SET Balance = Balance - 100 WHERE AccountID = 123;
COMMIT;
```

### Interaction and Trade-offs

| Lock Type       | Where Enforced | Concurrency | Failure Handling             | Best Use Case                                             |
| --------------- | -------------- | ----------- | ---------------------------- | --------------------------------------------------------- |
| **Optimistic**  | Application    | High        | Retry if conflict detected   | Read-heavy, cheap retries (e.g., CRMs, shopping carts)    |
| **Pessimistic** | Database       | Lower       | Prevented by blocking others | Write-heavy, costly retries (e.g., banking, reservations) |

### Practical Examples

#### Optimistic Lock in Action

* User A and User B both edit a customer profile.
* User A saves first.
* User B tries to save, but version check fails.
* User B reloads the latest record and retries.

```
[Resource: Record X]

--- Optimistic Lock (App-Level) ---
   |
   |-- User A edits locally (no lock)
   |-- User B edits locally (no lock)
   |
   |-- Both try to save
   |     -> DB checks version/timestamp
   |     -> One succeeds, the other retries
   |
   [High concurrency, occasional retry]
```

Here’s a simple example showing how optimistic locking might work in practice. This version uses a **version column** in the database to detect conflicts:

```python
# Example: Optimistic Lock in Action (Python + SQLAlchemy style)

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import StaleDataError

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    version = Column(Integer, nullable=False, default=1)

# Simulating User A and User B editing the same record
def update_customer(session: Session, customer_id: int, new_email: str, expected_version: int):
    try:
        customer = session.query(Customer).filter(
            Customer.id == customer_id,
            Customer.version == expected_version  # check version matches
        ).one()

        customer.email = new_email
        customer.version += 1  # increment version on successful update
        session.commit()
        print("Update successful")

    except Exception:
        session.rollback()
        print("Conflict detected, reload latest record and retry")

# Example flow
# User A reads record (version=1)
# User B reads record (version=1)

# User A saves first → succeeds (version now 2)
update_customer(sessionA, customer_id=1, new_email="userA@email.com", expected_version=1)

# User B tries to save with old version=1 → fails
update_customer(sessionB, customer_id=1, new_email="userB@email.com", expected_version=1)

# User B reloads record (now version=2) and retries → succeeds
update_customer(sessionB, customer_id=1, new_email="userB@email.com", expected_version=2)
```

This pattern enforces that only the **first save** on the expected version succeeds. Any later saves with an outdated version will fail, prompting the user to **reload the latest data** and try again.

#### Pessimistic Lock in Action

* User A starts editing a hotel booking.
* Database locks the row.
* User B tries to edit the same booking → blocked until User A finishes.
* Ensures no double-bookings.

```
[Resource: Record X]

--- Pessimistic Lock (DB-Level) ---
   |
   |-- User A starts edit --> DB places lock
   |-- User B tries to edit --> Blocked until A finishes
   |
   [Lower concurrency, no retry, but possible waiting]
```

Here’s a practical example of **pessimistic locking** in action, where the database itself prevents concurrent edits by holding a lock on the row until the first transaction finishes:

```python
# Example: Pessimistic Lock in Action (Python + SQLAlchemy style)

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    room_number = Column(Integer)
    guest_name = Column(String)

# User A: starts editing a booking
def user_a_edit(session: Session, booking_id: int):
    # SELECT ... FOR UPDATE acquires a row-level lock
    booking = session.query(Booking).filter_by(id=booking_id).with_for_update().one()
    print("User A locked the booking record")

    # simulate edit
    booking.guest_name = "Alice"
    session.commit()  # lock released after commit
    print("User A finished editing, lock released")

# User B: tries to edit at the same time
def user_b_edit(session: Session, booking_id: int):
    try:
        booking = session.query(Booking).filter_by(id=booking_id).with_for_update().one()
        print("User B acquired the lock after A finished")

        # simulate edit
        booking.guest_name = "Bob"
        session.commit()
    except Exception as e:
        session.rollback()
        print("User B failed:", e)

# Flow:
# 1. User A calls user_a_edit → acquires lock on row.
# 2. User B calls user_b_edit → blocked until A commits.
# 3. Once A finishes, B can proceed safely.
```

* The database uses `SELECT ... FOR UPDATE` to lock the row.
* While the lock is active, any other transaction trying to edit the same row must **wait**.
* This ensures **no double-bookings** or conflicting changes, at the cost of reduced concurrency.

### Best Practices for Locking Strategy

* Prefer **optimistic** if retries are acceptable and collisions are rare.
* Use **pessimistic** if conflicts are common or retries are too costly.
* Keep transactions **short** to minimize lock contention.
* Avoid mixing application-level and database-level locks unless absolutely necessary.
* Monitor retries, deadlocks, and wait times to tune strategy.

### Deadlocks in Pessimistic Locking

Because pessimistic locks block, they can lead to deadlocks if two transactions wait on each other’s locks.

```
Transaction 1:
   LOCK Row A
   WAIT Row B

Transaction 2:
   LOCK Row B
   WAIT Row A
```

**Strategies to handle:**

* Enforce **consistent lock ordering**.
* Use **timeouts** on lock acquisition.
* Keep transactions **as short as possible**.
