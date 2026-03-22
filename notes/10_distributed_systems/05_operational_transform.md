## Operational Transform (OT)

Operational Transform is a foundational technique in distributed systems that enables real-time collaborative editing of shared documents. Originally proposed by Ellis and Gibbs in 1989, OT allows multiple users to **concurrently** modify the same document while preserving consistency across all participants. The core idea is to transform incoming operations against previously executed operations so that every replica **converges** to the same final state regardless of the order in which edits arrive.

```
    [User A]              [User B]              [User C]
      |                     |                     |
      | op_a: Insert("X",3) | op_b: Delete(5)    | op_c: Insert("Z",1)
      |                     |                     |
      v                     v                     v
 +-----------+        +-----------+         +-----------+
 | OT Engine |<------>| OT Engine |<------->| OT Engine |
 | (Client)  |        | (Client)  |         | (Client)  |
 +-----------+        +-----------+         +-----------+
       \                    |                    /
        \                   |                   /
         \                  v                  /
          \        +-----------------+        /
           +------>|   OT Server     |<------+
                   | (Central Relay) |
                   +--------+--------+
                            |
                            v
                   +-------------------+
                   |  Shared Document  |
                   | "Hello, World!"   |
                   +-------------------+
```

## Collaborative Editing Challenges

Collaborative editing introduces several fundamental problems in distributed systems:

- Multiple users can **simultaneously** modify the same document region, creating conflicting edits.
- Network latency means each client operates on a **stale** snapshot of the document state.
- Naively applying remote operations in arrival order can **corrupt** the document or lose edits.
- Users expect their local edits to appear **instantly** without waiting for server confirmation.
- The system must guarantee that all replicas **converge** to an identical document state.

```
  User A (Local State)               User B (Local State)
  "ABCD"                             "ABCD"
    |                                   |
    | Insert('X', pos=2)                | Delete(pos=3)
    v                                   v
  "ABXCD"                            "ABD"
    |                                   |
    |--- op_a sent over network ------->|  (arrives late)
    |<------ op_b sent over network ----|  (arrives late)
    |                                   |
    | Naive apply Delete(pos=3)         | Naive apply Insert('X', pos=2)
    v                                   v
  "ABCD"  (WRONG! Lost 'X')          "ABXD"  (DIFFERENT! Inconsistent)
```

## How OT Works

OT resolves conflicts by **transforming** each incoming remote operation against local operations that have already been applied. This transformation adjusts positions and parameters so the intent of every edit is preserved.

The transformation process follows these steps:

- The OT engine **captures** each local operation and timestamps it with a logical clock or state vector.
- When a remote operation arrives, the engine **compares** its context against the local operation history.
- A transform function **adjusts** the remote operation to account for edits that have occurred since it was generated.
- The transformed operation is then **applied** to the local document, preserving the original intent.

```
  User A: Insert('X', pos=2)         User B: Delete(pos=3)
  on document "ABCD"                 on document "ABCD"

         Transform Function: T(op_a, op_b)
        +-------------------------------+
        | Input:                        |
        |   op_a = Insert('X', pos=2)   |
        |   op_b = Delete(pos=3)        |
        |                               |
        | Logic:                        |
        |   op_a.pos <= op_b.pos        |
        |   so shift op_b.pos by +1     |
        |                               |
        | Output:                       |
        |   op_a' = Insert('X', pos=2)  |
        |   op_b' = Delete(pos=4)       |
        +-------------------------------+

  User A applies op_b': Delete(pos=4)    User B applies op_a': Insert('X', pos=2)
  "ABXCD" -> "ABXD"                      "ABD" -> "ABXD"
              ^                                     ^
              Both converge to "ABXD"
```

## Transform Function Example

The transform function `T(op_a, op_b)` takes two concurrent operations and returns adjusted versions that can be safely applied in either order. Below is a simplified example for **insert-vs-insert** and **insert-vs-delete** cases:

- **Insert-Insert**: If both operations insert at different positions, the one with the higher position is shifted by the length of the earlier insert.
- **Insert-Delete**: If an insert occurs before a delete position, the delete index is **incremented** to account for the new character.
- **Delete-Insert**: If a delete occurs before an insert position, the insert index is **decremented** because a character was removed before it.
- **Delete-Delete**: If both delete the same position, one operation becomes a **no-op** since the character is already removed.

```
  T(Insert(pos_a), Insert(pos_b)):
  +-----------------------------------------+
  |  if pos_a < pos_b:                      |
  |      return Insert(pos_a), Insert(pos_b + 1) |
  |  else if pos_a > pos_b:                 |
  |      return Insert(pos_a + 1), Insert(pos_b) |
  |  else:  (tie-break by user ID)          |
  |      if user_a < user_b:                |
  |          return Insert(pos_a), Insert(pos_b + 1) |
  |      else:                              |
  |          return Insert(pos_a + 1), Insert(pos_b) |
  +-----------------------------------------+
```

## Types of Operations

OT systems define a set of primitive operations that cover all possible document mutations:

- **Insert**: Adds new content at a specified position, shifting subsequent characters to the right.
- **Delete**: Removes content at a specified position, shifting subsequent characters to the left.
- **Retain**: Skips over a number of characters without modification, used to **compose** operations efficiently.
- **Move**: Relocates content from one position to another, often decomposed into a delete followed by an insert.
- **Format**: Changes styling attributes such as bold or italic on a **range** of characters without altering the text itself.

## Convergence Properties

For an OT system to guarantee correctness, the transform function must satisfy key **mathematical** properties:

- **TP1** (Transformation Property 1): For any two concurrent operations `a` and `b`, applying `a` then `T(b, a)` must yield the same state as applying `b` then `T(a, b)`. This ensures **pairwise** convergence.
- **TP2** (Transformation Property 2): When three or more operations are concurrent, transforming in any order must still produce the same result. This ensures **global** convergence in peer-to-peer settings.
- **Causality**: Operations that are causally related must be applied in **causal** order, while only truly concurrent operations undergo transformation.
- **Intention**: The transformed operation must preserve the **intent** of the original edit, not just produce a mechanically valid adjustment.

```
  TP1 Convergence Guarantee:
  +---------------------------------------------------+
  |                                                   |
  |  State S                                          |
  |    |            \                                 |
  |    | apply(a)    \ apply(b)                       |
  |    v              v                               |
  |  State S_a      State S_b                         |
  |    |                \                             |
  |    | apply(T(b,a))   \ apply(T(a,b))              |
  |    v                  v                           |
  |  State S_ab  ===  State S_ba   (must be equal)    |
  |                                                   |
  +---------------------------------------------------+
```

## Server-Based vs Peer-to-Peer OT

OT architectures fall into two main categories depending on how operations are **coordinated** across participants:

**Server-based OT** uses a central server as the single source of truth:

- A central server **serializes** all operations into a single total order, simplifying the transformation logic.
- Clients only need to satisfy **TP1** because the server resolves all ordering ambiguities.
- This approach scales well for typical **web** applications where a reliable server is available.
- Google Docs and similar products use this **architecture** to handle millions of concurrent sessions.

**Peer-to-peer OT** has no central authority:

- Each peer communicates **directly** with other peers, requiring no single point of failure.
- The transform function must satisfy both TP1 and **TP2**, which is significantly harder to implement correctly.
- State vectors or logical clocks are needed to track **causality** between distributed operations.
- This model is better suited for **decentralized** applications but has proven difficult to get right in practice.

## OT vs CRDT Comparison

Conflict-free Replicated Data Types (CRDTs) offer an alternative approach to **collaborative** editing. While OT transforms operations, CRDTs design data structures that merge automatically without conflicts.

| Aspect                | OT                                      | CRDT                                     |
|-----------------------|-----------------------------------------|------------------------------------------|
| Conflict Resolution   | Transforms operations at runtime        | Conflicts are impossible by design       |
| Server Requirement    | Often relies on a central server        | Works fully peer-to-peer                 |
| Complexity            | Complex transform functions             | Complex data structures                  |
| Memory Overhead       | Low (stores operations)                 | Higher (stores metadata per character)   |
| Proven at Scale       | Google Docs, Apache Wave                | Yjs, Automerge, Apple Notes              |
| Correctness           | Must satisfy TP1/TP2 (error-prone)      | Mathematically guaranteed                |
| Undo Support          | Straightforward with inverse operations | More difficult to implement              |
| Network Requirement   | Typically needs ordered delivery        | Works with any delivery order            |

Key considerations when choosing between them:

- OT is a **mature** technology with decades of production use in centralized systems like Google Docs.
- CRDTs provide stronger **guarantees** for correctness but can consume more memory due to tombstone metadata.
- OT is generally easier to **optimize** for specific document types because transforms are tailored to the operation set.
- CRDTs are the preferred choice for **offline-first** applications where peers may be disconnected for extended periods.

## Implementing OT

Building an OT system requires careful attention to several engineering challenges:

- The document must be represented with a **model** that supports efficient positional operations, such as a rope or piece table.
- Transform functions must handle every **combination** of operation types, which grows quadratically with the number of primitives.
- A history buffer must store recent operations so that **late-arriving** remote edits can be transformed against the correct context.
- Client-side prediction applies local edits **immediately** for responsiveness, then reconciles with the server-acknowledged state.
- Undo and redo require maintaining an **inverse** operation for each applied edit, transformed against subsequent operations.

Popular OT implementations include:

- **Google Docs**: A web-based collaborative platform using server-based OT to synchronize edits across millions of users in real time.
- **ShareJS**: An open-source OT library built on Node.js that provides a **foundation** for adding real-time collaboration to custom applications.
- **Apache Wave**: The open-source successor to Google Wave, which **pioneered** many OT concepts for rich-text and structured document collaboration.
- **Firepad**: A collaborative text editor built on Firebase that uses OT to **synchronize** changes through a real-time database backend.
