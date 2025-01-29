## Database Transactions

Database transactions are a fundamental concept in data management, providing a reliable means to group one or more operations into a logical unit of work. This approach ensures that the database transitions from one valid state to another, even amidst concurrent user activity or potential system interruptions. Below is an expanded overview in notes form, presented with diagrams and lists for clarity.

```
+---------------------------------------------------+
|          Application (Transaction Context)        |
|                                                   |
|   Begin Transaction   --->   Perform Operations   |
|                                                   |
|   Commit or Rollback  <---   Confirmation         |
+---------------------------------------------------+
```

Transactions often start with a **begin** statement, then involve multiple data operations, and finally end with either **commit** (to make changes permanent) or **rollback** (to undo partial or failed changes).

### ACID: The Core Properties

- Each transaction enforces **Atomicity** by treating all operations as a single, indivisible unit that either fully applies or fully reverts.  
- The database maintains **Consistency** by ensuring that constraints or rules are not violated after a transaction completes.  
- Concurrent transactions aim for **Isolation**, which means they behave as though they are running one after the other.  
- Data achieves **Durability** by persisting commits on reliable storage, so completed transactions remain in effect even after a crash.  

### Dealing with Single Object Writes

```
    Single Object Write Flow
   +-------------------------+
   |         Begin          |
   +-----------+------------+
               |
               v
   +-------------------------+
   |   Lock or version check |
   +-----------+------------+
               |
               v
   +-------------------------+
   |       Write data       |
   +-----------+------------+
               |
               v
   +-------------------------+
   |      Commit / Rollback |
   +-------------------------+
```

- A log-based system can be **helpful** for ensuring atomicity by using a Write-Ahead Log (WAL) to record pending changes before they are applied.  
- A lock-based system can be **useful** for isolation by preventing other transactions from modifying the same object concurrently.  
- An MVCC approach can be **advantageous** because it allows multiple readers to access different object versions without waiting for locks.  
- A single object write often involves **minimal** overhead, but can still benefit from standardized transaction methods for consistency and durability.  

### Advanced Transaction Management

Transactions involving multiple objects or distributed environments call for more sophisticated techniques. They help coordinate complex tasks while preserving consistency across diverse systems or tables.

#### Two-Phase Commit (2PC)

```
          Coordinator                       Participant(s)
   +-----------------------+        +------------------------------+
   |  Prepare Transaction  |  -->   |    Pre-commit / Validate     |
   |  (Request Vote)       |        |  ------------------------->  |
   |                       |        |            (Vote)            |
   |  -------------------> |        +------------------------------+
   | (Votes)               |
   | <-------------------- |
   +-----------------------+
             |
             v
   +-----------------------+
   |       Commit /        |
   |       Rollback        |
   +-----------------------+
```

- The coordinator sends a **prepare** request to each participant, asking if it can commit.  
- Each participant responds with a **vote** (commit or abort) based on local checks.  
- If all participants vote commit, the coordinator issues a final **commit**; otherwise, it issues a **rollback**.  
- This protocol can be **helpful** in distributed databases to keep atomicity when multiple nodes are involved.  
- There can be **blocking** scenarios if the coordinator or participants fail at certain stages, so careful design is needed.  

#### Deadlock Detection and Prevention

```
   Deadlock Example

   Transaction A    Transaction B
        |                |
   lock Resource X  lock Resource Y
        |                |
      waits for Y     waits for X
        |                |
      (circular wait -> deadlock)
```

- Deadlock arises when transactions hold locks in a cycle, each waiting for a resource the other holds.  
- Detection algorithms can be **useful** for periodically scanning transactions to see if cycles have formed.  
- Prevention strategies can be **helpful** by forcing transactions to acquire locks in a predefined order or by rolling back one transaction when a cycle is probable.  
- Timeouts can be **practical** in resolving stuck transactions if the system cannot conclusively detect a deadlock.  

### Concurrency Control Methods Comparison

Below is a summary of different methods employed to handle concurrent transactions:

| Method         | Mechanism               | Pros                                                            | Cons                                                               | Common Use Cases                      |
|----------------|-------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------|---------------------------------------|
| Locks          | Lock data objects       | It can be **effective** for strict consistency.                 | It can lead to contention and potential deadlocks.                 | Traditional RDBMS with high integrity |
| MVCC           | Maintain multiple versions of data | It often allows **high** read concurrency.          | It can require additional storage for versions.                    | Databases that serve many read queries|
| Timestamp      | Use timestamps to order transactions | It can be **straightforward** to reason about order. | It can roll back transactions that conflict with newer timestamps. | Systems needing simpler concurrency   |
| Optimistic     | Validate changes at commit | It can be **appropriate** for low-conflict workloads. | It can cause commits to fail if conflicts are detected at end.     | Highly distributed or mostly-read apps|
  
