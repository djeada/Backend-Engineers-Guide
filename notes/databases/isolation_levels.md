## Isolation Levels

Isolation levels are a way of allowing concurrent access to a database while still ensuring data integrity and consistency. In situations where concurrent writes need to be completely sequential, it can take up a large amount of resources and slow down a database. To prevent this, some databases use weaker isolation levels. 

### Read Committed Isolation

With this level of isolation, when reading from the database, the user will only be able to see committed data. This ensures that the user does not see any data that is in a partially updated state that may be rolled back soon. To implement this, row level locks are not used, rather the old committed value is stored before the new value is committed and returned instead. When writing to the database, the user will only overwrite committed data and any later writes will be delayed until earlier writes are either committed or aborted. However, this does not prevent two processes from reading an old value and then both updating it, resulting in the first update to be completely thrown out.

### Snapshot Isolation and Repeatable Read

Read Committed Isolation prevents many problems, but still some concurrency bugs can occur. One such bug is read skew, which occurs when a client makes multiple consecutive reads, but in the middle of them, the database changes and the client views an inconsistent state. To prevent this, snapshot isolation is used, where each transaction reads from a consistent snapshot of the database. Writers and readers do not block each other, and the database stores multiple committed versions of an object. Every transaction is given a monotonically increasing transaction ID and when a read is made, the value with the highest transaction ID less than or equal to the reader's transaction ID is returned.

### Dealing with Lost Updates

Lost updates can occur when an application reads one piece of data, modifies it, and then writes it back. If two of these cycles happen concurrently, it is possible that the update from one of them will be lost. Atomic write operations like incrementing or compare and set can be used to prevent this, by implementing row level locks. Some databases can also detect lost updates automatically using snapshot isolation, thus eliminating the need for locks and aborting transactions that cause the lost update. This is more effective as it reduces the risk of making bugs when dealing with locks.

### Write Skew and Phantoms

Write skew occurs when concurrent writes to different parts of the database allow some invariant about the data to be broken. To prevent this, locks can be used to lock the rows that can break the invariant when updating one row. However, if two transactions are creating a row in the database, not modifying it, and if both of these rows are created it will violate an invariant (phantom). To prevent this, a pre-populated blank row in the database should be used as something to lock in order to avoid write skew.
