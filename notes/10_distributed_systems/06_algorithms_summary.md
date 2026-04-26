## Algorithms and Data Structures for System Design

The following algorithms and data structures appear frequently in backend and distributed system design. They are useful because system design often involves trade-offs around scale, latency, storage, consistency, correctness, and fault tolerance.

These concepts help solve recurring problems: finding nearby locations, distributing data across servers, limiting traffic, searching prefixes, synchronizing replicas, estimating large counts, scheduling timeouts, and merging concurrent edits.

Each entry below explains what the structure is, how it works at a high level, why it matters, and where it is used in practice.

### 1. Geohash

A **Geohash** is a string encoding of a latitude and longitude into a hierarchical grid. It turns a two-dimensional location into a compact text prefix. Locations that share the same Geohash prefix are usually geographically close to each other.

Geohash works by repeatedly splitting the world into smaller latitude and longitude ranges. The algorithm interleaves bits from the latitude and longitude and then encodes the result using base-32. Shorter Geohashes cover larger areas, while longer Geohashes represent smaller, more precise regions.

Example coordinates:

```text
Latitude:  52.5200
Longitude: 13.4050
Location:  Berlin
```

Example Geohash-like output:

```text
u33dc
```

A longer Geohash gives more precision:

```text
u33dc1
u33dc1r
u33dc1rq
```

The prefix behavior is the key benefit. If multiple locations begin with `u33dc`, they are likely in the same general area.

Example lookup:

```json
{
  "query": "find drivers near Berlin",
  "geohashPrefix": "u33dc",
  "candidateDrivers": ["driver-17", "driver-22", "driver-91"]
}
```

Geohash is important because it allows location-based search to use string prefixes instead of expensive raw latitude/longitude comparisons. A system can index nearby users, restaurants, vehicles, or sensors by Geohash prefix and quickly narrow the search area.

Common use cases include ride-sharing dispatch, geofencing, nearby search, Redis `GEOADD`, Elasticsearch geo queries, food delivery apps, and location-based alerts.

### 2. Quadtree

A **Quadtree** is a tree structure that recursively partitions two-dimensional space into four quadrants. Each node represents a region of space, and each internal node splits its region into northwest, northeast, southwest, and southeast child regions.

Quadtrees are useful when spatial data is unevenly distributed. Dense areas can be subdivided many times, while sparse areas can remain large. This avoids wasting storage and computation on empty regions.

Example:

```text
+-----------------------+
|          |            |
|   NW     |     NE     |
|          |            |
|----------+------------|
|          |            |
|   SW     |     SE     |
|          |            |
+-----------------------+
```

If the northeast region contains too many points, it can be split again:

```text
+---------------------------+
|          |  NE-NW | NE-NE |
|   NW     |--------+-------+
|          |  NE-SW | NE-SE |
|----------+----------------|
|          |                |
|   SW     |     SE         |
|          |                |
+---------------------------+
```

Example stored points:

```json
{
  "region": "NE",
  "points": [
    { "id": "restaurant-1", "lat": 52.52, "lon": 13.40 },
    { "id": "restaurant-2", "lat": 52.53, "lon": 13.41 }
  ]
}
```

Quadtrees matter because they support efficient spatial queries such as “find all objects inside this rectangle” or “find nearby map features.” They are useful when the query area is a box, region, or map viewport.

In system design, Quadtrees may appear in map rendering, collision detection, geospatial indexing, game servers, and systems that need to partition spatial data across machines.

### 3. Consistent Hashing

**Consistent hashing** is a data distribution strategy that reduces key movement when servers are added or removed. It is commonly used in distributed caches, databases, and storage systems.

In ordinary modulo hashing, a key might be assigned like this:

```text
server = hash(key) % number_of_servers
```

The problem is that when the number of servers changes, most keys get remapped. This can cause massive cache misses or data movement.

Consistent hashing solves this by mapping both servers and keys onto a circular hash ring. A key belongs to the first server found while moving clockwise around the ring.

```text
            Consistent Hashing Ring

                Node A
               /      \
              /  keys   \
        Node D   ───►    Node B
              \         /
               \ keys  /
                Node C

        Adding Node E between A and B
        only moves keys in the arc before E.
```

Example key mapping:

```json
{
  "user:1001": "Node A",
  "user:1002": "Node C",
  "user:1003": "Node D"
}
```

When a new node is added, only a portion of keys move:

```json
{
  "newNode": "Node E",
  "movedKeys": ["user:1001"],
  "unchangedKeys": ["user:1002", "user:1003"]
}
```

Virtual nodes improve balance by placing each physical server at multiple positions on the ring. This avoids one server accidentally owning too much of the keyspace.

Consistent hashing is important because it makes distributed systems easier to scale. It is used in distributed caches, distributed hash tables, databases, CDNs, and storage systems such as Cassandra, Dynamo-style systems, Memcached clients, and Akamai-like routing designs.

### 4. Leaky Bucket

The **Leaky Bucket** algorithm is a rate-limiting and traffic-shaping algorithm. It smooths bursts by processing requests at a fixed rate.

The bucket acts like a queue. Requests enter the bucket. The bucket drains at a constant rate. If the bucket is full when a new request arrives, the request is dropped or rejected.

Example:

```text
Incoming requests:
R R R R R R R

Bucket capacity: 3
Drain rate: 1 request per second

If too many requests arrive at once,
extra requests are rejected.
```

Example output:

```json
{
  "requestId": "req-101",
  "bucketStatus": "full",
  "decision": "reject",
  "reason": "rate limit exceeded"
}
```

The Leaky Bucket algorithm is useful when the system needs a steady output rate. It prevents sudden bursts from overwhelming backend systems.

It is commonly used in API gateways, network traffic shaping, request throttling, Nginx `limit_req`, and systems that must protect downstream services from spikes.

The trade-off is that Leaky Bucket is strict. It smooths traffic well, but it may reject bursts even if the user has been idle for a long time.

### 5. Token Bucket

The **Token Bucket** algorithm is another rate-limiting algorithm, but it allows controlled bursts. Tokens are added to a bucket at a fixed rate. Each request consumes one token. If there are no tokens, the request is rejected or delayed.

Example:

```text
Token fill rate: 10 tokens per second
Bucket capacity: 50 tokens

A user can send a burst of 50 requests,
but over time the average rate is limited to 10 requests per second.
```

Example request decision:

```json
{
  "userId": "user-123",
  "tokensBefore": 4,
  "requestCost": 1,
  "tokensAfter": 3,
  "decision": "allow"
}
```

Example rejected request:

```json
{
  "userId": "user-123",
  "tokensBefore": 0,
  "requestCost": 1,
  "decision": "reject",
  "reason": "no tokens available"
}
```

Token Bucket is important because it supports burst tolerance while still enforcing a long-term average rate. This is useful for public APIs where short spikes are acceptable but sustained abuse is not.

It is commonly used in API gateways, cloud endpoints, payment APIs, network shaping, and fair-use throttling systems.

Compared with Leaky Bucket, Token Bucket is more flexible because it rewards idle time with accumulated burst capacity.

### 6. Trie

A **Trie**, also called a prefix tree, is a tree structure for storing strings. Each edge represents a character, and each node represents a prefix.

Tries are useful when many strings share prefixes. Instead of storing each full string separately, shared prefixes are stored once.

```text
               root
              / | \
             t  b  s
            /   |   \
           o    a    e
          / \   |    |
         p   w  l    a
                 \    \
                  l    r
                        \
                         c
                          \
                           h

      Words: top, tow, ball, search
```

Example autocomplete query:

```text
Prefix: "se"
```

Example output:

```json
{
  "prefix": "se",
  "suggestions": ["search"]
}
```

Lookup time is proportional to the length of the query string, not the number of stored words. Searching for a prefix of length `k` takes `O(k)` time.

Tries are important for autocomplete, spell checkers, dictionary lookup, routing tables, search suggestions, banned-word filters, and DNS-like prefix matching.

The trade-off is memory usage. A basic Trie can use a lot of memory if the character set is large or if the stored strings do not share many prefixes. Compressed tries, radix trees, and PATRICIA tries reduce this overhead.

### 7. Rsync

**Rsync** is a delta-transfer algorithm used to synchronize files efficiently. Instead of sending an entire file, it sends only the changed parts.

This is useful when two machines already have similar copies of a large file. The receiver calculates checksums for blocks of its file and sends those checksums to the sender. The sender scans its version using a rolling checksum and sends only the blocks that differ.

Example:

```text
Old file on receiver:
AAAA BBBB CCCC DDDD

New file on sender:
AAAA BBBB XXXX DDDD

Only block CCCC changed to XXXX.
Rsync sends only the changed block.
```

Example sync result:

```json
{
  "file": "backup.tar",
  "fileSizeMb": 5000,
  "changedDataMb": 20,
  "transferredMb": 20
}
```

Rsync matters because bandwidth is often more expensive or slower than local CPU work. Delta synchronization can dramatically reduce network transfer.

It is used in backup systems, file synchronization tools, database backup transfer, CDN origin updates, deployment systems, and block-level file sync tools.

The trade-off is CPU overhead. Rsync must compute checksums and scan data, which may be expensive for very large files or many small files.

### 8. Raft and Paxos

**Raft** and **Paxos** are consensus protocols. They allow a distributed cluster to agree on a single sequence of operations even when some nodes fail.

Consensus is needed when systems require strong consistency. For example, a cluster may need to agree on who the leader is, what the latest configuration is, or which writes have been committed.

Raft is often easier to understand than Paxos. In Raft, one node becomes the leader. The leader receives client commands, appends them to its log, and replicates them to followers. A command is committed only after a majority of nodes acknowledge it.

Example Raft cluster:

```text
          Client Write
              |
              v
           Leader
          /   |   \
         v    v    v
     Follower Follower Follower

Write commits after majority acknowledgement.
```

Example commit result:

```json
{
  "command": "set x=10",
  "replicas": 5,
  "acknowledgedBy": 3,
  "committed": true
}
```

Consensus protocols are important because they allow distributed systems to behave like one reliable system. They are used for replicated logs, metadata stores, leader election, distributed databases, and configuration systems.

Examples include etcd using Raft, CockroachDB using Raft, ZooKeeper using ZAB, and Google Spanner using Paxos-based ideas.

The trade-off is availability and latency. Strong consensus usually requires communication with a quorum, so writes may fail or slow down during network partitions.

### 9. Bloom Filter

A **Bloom Filter** is a probabilistic data structure used to test whether an item might be in a set. It is very space-efficient, but it can return false positives.

A Bloom Filter can say:

```text
Definitely not present
Possibly present
```

It cannot say with complete certainty that something is present.

A Bloom Filter uses a bit array and multiple hash functions. To insert an item, each hash function sets one bit. To check an item, the same hash functions are used. If any required bit is zero, the item is definitely absent. If all required bits are one, the item is probably present.

```text
Insert "apple":  h1=2, h2=5, h3=7

Bit array:
Index:  0   1   2   3   4   5   6   7   8   9
       [0] [0] [1] [0] [0] [1] [0] [1] [0] [0]

Query "banana": h1=1, h2=5, h3=8
Bit 1 = 0 → definitely NOT in set

Query "grape": h1=2, h2=5, h3=7
All bits = 1 → possibly in set
```

Example lookup:

```json
{
  "key": "user:999",
  "bloomFilterResult": "definitely_not_present",
  "databaseLookupNeeded": false
}
```

Bloom Filters are important because they can avoid expensive lookups. For example, a database engine can check a Bloom Filter before reading disk. If the key is definitely absent, it avoids unnecessary I/O.

They are used in Bigtable, Cassandra SSTables, safe browsing systems, deduplication pipelines, crawlers, cache filtering, and large-scale membership checks.

The trade-off is false positives. The system may occasionally perform an unnecessary lookup, but it will not incorrectly reject an item that is actually present.

### 10. Merkle Tree

A **Merkle Tree** is a tree of hashes. Leaf nodes hash individual data blocks. Parent nodes hash their children’s hashes. The root hash summarizes the entire dataset.

```text
                  Root Hash
                 /         \
            Hash(AB)      Hash(CD)
            /     \       /     \
        Hash(A) Hash(B) Hash(C) Hash(D)
           |       |       |       |
        Block A Block B Block C Block D
```

If one block changes, only the hashes along its path to the root change.

```text
Changing Block C invalidates:
Hash(C) → Hash(CD) → Root Hash
```

Example verification:

```json
{
  "block": "Block C",
  "proofIncludes": ["Hash(D)", "Hash(AB)"],
  "verificationCost": "O(log N)"
}
```

Merkle Trees matter because they make large datasets tamper-evident. A system can compare root hashes to detect whether two replicas are identical. If roots differ, it can compare subtrees to find exactly where data diverged.

They are used in Git, blockchains, Dynamo-style anti-entropy repair, IPFS, certificate transparency logs, and distributed storage systems.

The trade-off is maintaining hash trees during writes. Updates require recalculating hashes along the changed path.

### 11. HyperLogLog

**HyperLogLog** is a probabilistic algorithm for estimating the number of distinct items in a large dataset. This is called cardinality estimation.

It is useful when exact distinct counting would require too much memory. For example, counting unique users from billions of events may be expensive if every user ID must be stored.

HyperLogLog hashes each item and observes patterns in the hash output, especially the number of leading zeros. Seeing many leading zeros suggests that the dataset is large. It combines estimates across multiple registers to produce an approximate count.

Example stream:

```text
user-1
user-2
user-1
user-3
user-2
user-4
```

Exact distinct count:

```json
{
  "uniqueUsers": 4
}
```

HyperLogLog approximate result:

```json
{
  "estimatedUniqueUsers": 4,
  "errorRate": "small"
}
```

At very large scale:

```json
{
  "estimatedUniqueUsers": 103482991,
  "memoryUsed": "small fixed amount"
}
```

HyperLogLog is important for analytics systems that need approximate unique counts with tiny memory usage.

It is used in Redis `PFADD` and `PFCOUNT`, BigQuery `APPROX_COUNT_DISTINCT`, Presto, Druid, analytics dashboards, ad systems, and event pipelines.

The trade-off is accuracy. HyperLogLog gives an estimate, not an exact count.

### 12. Count-Min Sketch

A **Count-Min Sketch** is a probabilistic data structure for estimating how often items appear in a stream. It uses a fixed-size two-dimensional array and multiple hash functions.

Each incoming item is hashed into one column per row, and each corresponding counter is incremented. To estimate an item’s frequency, the algorithm checks all relevant counters and returns the minimum value.

Example stream:

```text
apple, banana, apple, orange, apple, banana
```

Exact counts:

```json
{
  "apple": 3,
  "banana": 2,
  "orange": 1
}
```

Count-Min Sketch approximate output:

```json
{
  "apple": 3,
  "banana": 2,
  "orange": 1
}
```

In larger streams, collisions can cause overestimation:

```json
{
  "item": "apple",
  "estimatedCount": 1032,
  "actualCountMayBeLessOrEqual": true
}
```

Count-Min Sketch is important because it tracks frequencies without storing every unique item. This is useful for high-volume streams where there may be millions or billions of unique keys.

It is used for heavy hitter detection, trending topics, network traffic analysis, fraud detection, ad-click monitoring, log analytics, and approximate top-k systems.

The trade-off is that counts may be overestimated due to hash collisions, but the error can be bounded by choosing appropriate table dimensions.

### 13. Hierarchical Timing Wheels

A **Hierarchical Timing Wheel** is a data structure for managing large numbers of timers efficiently. It is used when a system needs to schedule millions of timeouts, retries, expirations, or delayed tasks.

A timing wheel is like a circular array of time slots. Each slot contains timers that expire during that time interval. A pointer advances on every tick. When the pointer reaches a slot, timers in that slot are executed.

```text
      Second wheel (60 slots)          Minute wheel (60 slots)
      ┌──┬──┬──┬──┬──┬──┐             ┌──┬──┬──┬──┬──┬──┐
      │ 0│ 1│ 2│..│58│59│  overflow   │ 0│ 1│ 2│..│58│59│
      └──┴──┴──┴──┴──┴──┘  ───────►   └──┴──┴──┴──┴──┴──┘
            ▲ tick                          ▲ cascade
            │ pointer                       │ pointer

      Timers < 60 s   → second wheel
      Timers < 60 min → minute wheel
```

Example scheduled timers:

```json
[
  { "task": "retry-payment", "delaySeconds": 5 },
  { "task": "expire-session", "delaySeconds": 1800 },
  { "task": "close-websocket", "delaySeconds": 60 }
]
```

Example timer firing:

```json
{
  "currentSlot": 5,
  "expiredTasks": ["retry-payment"]
}
```

Timing wheels are important because naive timer systems may scan all timers repeatedly, which becomes expensive at scale. Timing wheels can make timer insertion and expiration very efficient.

They are used in operating systems, TCP retransmission timers, Netty `HashedWheelTimer`, Kafka delayed operations, Erlang VM internals, job schedulers, and cache TTL systems.

The trade-off is timer precision. Slot granularity affects how accurately timers fire.

### 14. Operational Transformation

**Operational Transformation**, or OT, is an algorithm used for real-time collaborative editing. It allows multiple users to edit the same document concurrently while keeping all copies consistent.

The core problem is that concurrent edits may refer to positions that change as other edits are applied.

Example:

```text
Original document:
hello

User A inserts "X" at position 0:
Xhello

User B inserts "Y" at position 5:
helloY
```

If both edits happen at the same time, the system must transform positions so both users converge to the same final document.

Example converged output:

```text
XhelloY
```

OT works by transforming operations against each other. If one user inserts text before another user’s edit position, the second operation’s index may need to shift.

Example operation transformation:

```json
{
  "operationA": "insert X at position 0",
  "operationBOriginal": "insert Y at position 5",
  "operationBTransformed": "insert Y at position 6"
}
```

OT is important because collaborative editors need low-latency local editing while still converging to a shared document state.

It is used in Google Docs-style editors, Microsoft Office Online, collaborative code editors, Firepad, and older systems such as Apache Wave.

The trade-off is implementation complexity. OT requires careful handling of operation order, history, transformation rules, and edge cases. CRDTs are another approach to similar collaboration problems.

### Summary Comparison

| Algorithm / Structure          | Category                    |         Typical Time Complexity |                       Space | Key Trade-Off                                |
| ------------------------------ | --------------------------- | ------------------------------: | --------------------------: | -------------------------------------------- |
| **Geohash**                    | Spatial indexing            |            `O(k)` prefix lookup |                      `O(N)` | Precision vs prefix length                   |
| **Quadtree**                   | Spatial indexing            |              `O(log N)` average |                      `O(N)` | Balance depends on point distribution        |
| **Consistent Hashing**         | Partitioning                |               `O(log N)` lookup |                  `O(N + V)` | Balance vs virtual-node count                |
| **Leaky Bucket**               | Rate limiting               |                          `O(1)` |        `O(1)` or queue size | Smoothness vs burst rejection                |
| **Token Bucket**               | Rate limiting               |                          `O(1)` |                      `O(1)` | Burst tolerance vs long-term cap             |
| **Trie**                       | String indexing             |                   `O(k)` lookup | Can be high for sparse keys | Fast prefix lookup vs memory                 |
| **Rsync**                      | Synchronization             |                     `O(N)` scan |            `O(N)` checksums | Bandwidth savings vs CPU cost                |
| **Raft / Paxos**               | Consensus                   | Quorum communication per commit |              Replicated log | Consistency vs availability under partitions |
| **Bloom Filter**               | Membership test             |                          `O(k)` |                 `O(m)` bits | Memory efficiency vs false positives         |
| **Merkle Tree**                | Integrity / synchronization |         `O(log N)` verification |               `O(N)` hashes | Fast verification vs tree maintenance        |
| **HyperLogLog**                | Cardinality estimation      |                `O(1)` add/query |             Fixed registers | Tiny memory vs approximate counts            |
| **Count-Min Sketch**           | Frequency estimation        |                `O(d)` add/query |                  `O(d × w)` | Fixed memory vs overestimation               |
| **Timing Wheels**              | Scheduling                  |        Near `O(1)` start/expire |         `O(slots + timers)` | Timer granularity vs wheel complexity        |
| **Operational Transformation** | Collaboration               | Can grow with operation history |                `O(history)` | Convergence vs implementation complexity     |

These algorithms are valuable in system design because they represent common patterns for scaling systems. They help answer questions like how to distribute keys, rate-limit users, search by prefix, count unique visitors, synchronize replicas, schedule millions of timeouts, or coordinate writes across unreliable machines.
