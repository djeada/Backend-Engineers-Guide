# Transactions in Databases

Transactions are a powerful abstraction used by databases to manage writes and ensure data consistency. Transactions allow writes to be committed or rolled back based on the success or failure of the operation. While transactions can be challenging to implement in distributed systems, they are relatively simple to use in a single database.

## ACID Properties

Transactions in databases aim to provide the guarantees outlined by the ACID properties:

- **Atomicity**: All writes within a transaction are treated as a single, atomic operation. If a fault occurs during the transaction, any completed writes will be rolled back.

- **Consistency**: The database ensures that the data remains in a consistent state, even in the face of faults.

- **Isolation**: Concurrently executing transactions are isolated from one another, meaning each transaction can pretend that it is the only one running on the database. However, most databases do not implement strict isolation due to performance penalties and instead use weak isolation levels.

- **Durability**: Once a transaction is completed, the data will never be forgotten, even in the face of faults.

## Single Object Writes

In the case of single object writes, almost all database engines provide guarantees about atomicity and isolation to ensure that the data for an individual key does not become corrupted or mixed with previous values. Atomicity can be achieved by using a log for crash recovery and isolation can be implemented using a lock on each object.
