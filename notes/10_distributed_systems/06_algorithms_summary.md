## Algorithms and Data Structures for System Design

The following algorithms and data structures appear frequently in backend and distributed system design. Each entry explains what the structure is, how it works at a high level, why it matters, and where it is used in practice.

---

### 1. Geohash

**What it is:** A string encoding of latitude/longitude into a hierarchical grid.
**How it works:** The algorithm interleaves bits of the latitude and longitude, then base-32 encodes the result. Longer strings give **finer** precision, and locations that share a prefix are spatially close.
**Why it's important:** Enables very fast proximity searches (e.g. "find all users within 1 km") by turning 2D spatial queries into simple prefix lookups. Interviewers often probe how you'd build location-based services (ride-share, geofencing), and Geohash shows you understand spatial indexing.
**Where it's used:** Redis `GEOADD`, Elasticsearch geo queries, ride-sharing dispatch, geofencing services.

---

### 2. Quadtree

**What it is:** A tree that recursively partitions 2D space into four quadrants.
**How it works:** Each internal node has exactly four children representing NW, NE, SW, SE quadrants. Subdivisions continue until a region contains fewer than a **threshold** number of points or reaches a maximum depth.
**Why it's important:** Supports efficient window/region queries and dynamic spatial indexing. In system design, you might use Quadtrees to shard geospatial data across servers or accelerate map-tile rendering—knowing it demonstrates spatial-data handling at scale.
**Where it's used:** Map-tile rendering, collision detection in games, spatial database indexes, Uber's H3 (conceptually similar).

---

### 3. Consistent Hashing

```
            Consistent Hashing Ring

                Node A
               /      \
              /   keys  \
        Node D    ───►   Node B
              \         /
               \ keys  /
                Node C

        Adding Node E between A and B
        only moves keys in arc A→E
        (all other keys stay put)
```

**What it is:** A hashing scheme that minimizes remapping when nodes join/leave the cluster.
**How it works:** Nodes and keys are both mapped onto a circular hash space. Each key is **assigned** to the next node clockwise on the ring. Virtual nodes (multiple positions per physical node) improve balance.
**Why it's important:** The go-to for distributing cache entries or data partitions (e.g. in a distributed cache or DHT) so that only ~1/N keys move on topology changes. Interviewers will expect you to know how to scale caches (e.g. Memcached) without a massive cache-miss storm on resizing.
**Where it's used:** Amazon DynamoDB, Apache Cassandra, Memcached, Akamai CDN.

---

### 4. Leaky-Bucket

**What it is:** A rate-limiting algorithm that smooths bursts by processing tokens at a fixed rate.
**How it works:** Incoming requests enter a bucket (queue) of fixed size. The bucket **drains** at a constant rate. If the bucket is full when a new request arrives, that request is dropped.
**Why it's important:** Illustrates how to enforce steady request throughput (e.g. API gateways). In interviews, designing a throttling layer often comes up, and Leaky-Bucket shows you can bound QPS and prevent overload.
**Where it's used:** Network traffic shaping (ATM, ISP policing), API gateways, Nginx `limit_req`.

---

### 5. Token-Bucket

**What it is:** A rate-limiter that allows bursts up to a bucket size but enforces a long-term rate.
**How it works:** Tokens are added to a bucket at a fixed rate up to a maximum capacity. Each request **consumes** one token. If the bucket is empty the request is rejected or queued.
**Why it's important:** More flexible than Leaky-Bucket—lets you absorb short spikes while still capping average rate. Interviewers like to discuss fair-use policies and burst-tolerant rate limits; Token-Bucket is fundamental.
**Where it's used:** AWS API Gateway, Google Cloud Endpoints, Stripe API, Linux `tc` traffic control.

---

### 6. Trie

```
               (root)
              / | \
             t  b  s
            /   |   \
           o    a    e
          / \   |    |
         p   w  l    a
                 \    \
                  l    r
                   \    \
                    ─    c
                          \
                           h

      Words: top, tow, ball, search
      Shared prefixes reduce storage
```

**What it is:** A prefix tree for storing strings.
**How it works:** Each edge represents a character and each node a prefix. Lookups walk the tree character by character, giving O(k) time where k is the key **length**, independent of the number of stored keys.
**Why it's important:** Powers lightning-fast autocomplete, IP routing tables, dictionary lookups. When you design a search-as-you-type feature or need compact prefix storage (e.g. banned words filter), Tries show you can optimize both space and lookup latency.
**Where it's used:** Autocomplete engines, DNS resolvers, IP routing (PATRICIA trie), spell checkers.

---

### 7. Rsync

**What it is:** A delta-transfer algorithm that synchronizes files by sending only changed blocks.
**How it works:** The receiver splits its copy into fixed-size blocks and sends rolling checksums. The sender scans its copy for **matching** blocks and transmits only the non-matching bytes plus block-reuse instructions.
**Why it's important:** Critical for efficient backups, CDN origin-pull, or database replication. Interviewers may ask how to sync large datasets over the network with minimal bandwidth; Rsync's rolling-checksum trick is the classic answer.
**Where it's used:** Linux `rsync` utility, Dropbox block-level sync, CDN origin-pull, database backup tools.

---

### 8. Raft / Paxos

**What it is:** Consensus protocols to agree on a single sequence of operations in a distributed cluster.
**How it works:** A leader is elected and **replicates** a log of commands to followers. A command is committed only after a majority (quorum) acknowledges it. If the leader fails, a new election begins.
**Why it's important:** Core to building strongly consistent distributed systems (e.g. leader election, replicated logs in databases like etcd, Spanner). In any fault-tolerance discussion, you'll need to contrast CP vs. AP (CAP theorem) and show you understand how systems stay in sync despite node failures.
**Where it's used:** etcd (Raft), ZooKeeper (ZAB, Paxos-derived), Google Spanner (Paxos), CockroachDB (Raft).

---

### 9. Bloom Filter

```
      Insert "apple":  h1=2, h2=5, h3=7

      Bit array (m = 10):
      Index:  0   1   2   3   4   5   6   7   8   9
             [0] [0] [1] [0] [0] [1] [0] [1] [0] [0]

      Query "banana": h1=1, h2=5, h3=8
      Bit 1 = 0  →  definitely NOT in set

      Query "grape":  h1=2, h2=5, h3=7
      All bits = 1  →  POSSIBLY in set (false positive)
```

**What it is:** A space-efficient probabilistic data structure for set membership with false positives.
**How it works:** k hash functions each map an element to a position in a bit array of size m. To test membership, check whether **all** k positions are set; if any is zero the element is absent, otherwise it is probably present.
**Why it's important:** Used to avoid expensive lookups (e.g. "is this key in the cache?" or "have we seen this URL before?"). In interview scenarios around caching or big-data pipelines, Bloom filters demonstrate you can trade a tiny error rate for huge memory savings.
**Where it's used:** Google Bigtable, Apache Cassandra (SSTable lookups), Chrome safe-browsing, Medium (dedup recommendations).

---

### 10. Merkle Tree

```
                  Root Hash
                 /         \
            Hash(AB)      Hash(CD)
            /     \       /     \
        Hash(A) Hash(B) Hash(C) Hash(D)
           |       |       |       |
        Block A Block B Block C Block D

      Changing Block C only invalidates
      Hash(C) → Hash(CD) → Root Hash
      (logarithmic verification path)
```

**What it is:** A hash tree where each parent summarizes its children's hashes.
**How it works:** Leaf nodes hash individual data blocks. Each parent node hashes the **concatenation** of its children's hashes. To verify a single block, only the sibling hashes along the path to the root are needed—O(log N) proof size.
**Why it's important:** Enables efficient, tamper-evident verification of large datasets (e.g. git, blockchain, database replicas). When designing systems that need to detect or reconcile divergent data (e.g. anti-entropy in Dynamo), Merkle trees are your tool.
**Where it's used:** Git (object store), Bitcoin/Ethereum, Amazon DynamoDB (anti-entropy), IPFS, certificate transparency logs.

---

### 11. HyperLogLog

**What it is:** A streaming algorithm for cardinality estimation (count distinct) using tiny memory.
**How it works:** Elements are hashed and the algorithm tracks the maximum number of **leading** zeros seen across many sub-streams (registers). The harmonic mean of estimates across registers gives an overall cardinality estimate with ~0.8% standard error using only 12 KB.
**Why it's important:** Real-time analytics often need "unique user" or "distinct search terms" counts on massive streams. In scale-out designs, HyperLogLog shows you can give approximate metrics with sub-kilobyte state.
**Where it's used:** Redis `PFADD`/`PFCOUNT`, Google BigQuery `APPROX_COUNT_DISTINCT`, Presto, Druid.

---

### 12. Count-Min Sketch

**What it is:** A probabilistic frequency-counting structure with fixed size.
**How it works:** A 2D array of d rows × w columns is maintained. Each of d hash functions maps an element to one column per row, and the **minimum** across all d cells is used as the frequency estimate, bounding overcount.
**Why it's important:** Lets you track "top-k" heavy hitters (e.g. popular products, trending hashtags) in streaming data. Interviewers frequently ask how to monitor high-volume logs or metrics without storing every event; Count-Min Sketch is a key answer.
**Where it's used:** Network traffic monitoring, trending topics on Twitter/X, ad-click fraud detection, Apache Spark.

---

### 13. Hierarchical Timing Wheels

```
      Second wheel (60 slots)          Minute wheel (60 slots)
      ┌──┬──┬──┬──┬──┬──┐             ┌──┬──┬──┬──┬──┬──┐
      │ 0│ 1│ 2│..│58│59│  overflow   │ 0│ 1│ 2│..│58│59│
      └──┴──┴──┴──┴──┴──┘  ───────►  └──┴──┴──┴──┴──┴──┘
            ▲ tick                          ▲ cascade
            │ pointer                       │ pointer

      Timers < 60 s  → second wheel
      Timers < 60 min → minute wheel
      Each tick advances the pointer by one slot
```

**What it is:** A timer-wheel structure to manage millions of timeouts efficiently.
**How it works:** Slots in a circular array correspond to time intervals. Timers are placed in the slot matching their **expiry**. A tick pointer advances each interval; expired timers in the current slot fire. Longer timers cascade into coarser-grained wheels.
**Why it's important:** Critical for schedulers (e.g. TCP retransmission timers, cache-entry TTLs) at high scale. In system design, you'll be asked how to handle huge numbers of delayed jobs or network timeouts without O(N) per-tick overhead.
**Where it's used:** Linux kernel timer subsystem, Netty `HashedWheelTimer`, Kafka delayed operations, Erlang VM.

---

### 14. Operational Transformation

**What it is:** An algorithm for real-time collaborative editing that merges concurrent operations.
**How it works:** When two users make concurrent edits, the server transforms one operation against the other so that applying both in either order **converges** to the same document state. Indices are adjusted to account for prior insertions or deletions.
**Why it's important:** Powers Google Docs-style collaborative applications. When discussing collaborative systems or CRDTs (Conflict-Free Replicated Data Types), knowing OT shows you can handle concurrent state updates with consistency guarantees.
**Where it's used:** Google Docs, Microsoft Office Online, Apache Wave, Firepad.

---

### Summary Comparison

| Algorithm | Category | Time Complexity | Space | Key Trade-off |
|---|---|---|---|---|
| **Geohash** | Spatial indexing | O(k) lookup | O(N) | Precision vs prefix length |
| **Quadtree** | Spatial indexing | O(log N) average | O(N) | Balance vs point distribution |
| **Consistent Hashing** | Partitioning | O(log N) lookup | O(N + V) | Balance vs virtual-node count |
| **Leaky-Bucket** | Rate limiting | O(1) | O(1) | Smoothness vs burst rejection |
| **Token-Bucket** | Rate limiting | O(1) | O(1) | Burst tolerance vs long-term cap |
| **Trie** | String indexing | O(k) lookup | O(Σ × k) | Speed vs memory for sparse keys |
| **Rsync** | Synchronization | O(N) scan | O(N) checksums | Bandwidth savings vs CPU cost |
| **Raft / Paxos** | Consensus | O(N) per commit | O(log) | Consistency vs availability (CAP) |
| **Bloom Filter** | Membership test | O(k) | O(m) bits | Space vs false-positive rate |
| **Merkle Tree** | Integrity / sync | O(log N) verify | O(N) hashes | Verification speed vs tree build |
| **HyperLogLog** | Cardinality | O(1) add/query | O(m) registers | Accuracy vs memory (~12 KB) |
| **Count-Min Sketch** | Frequency | O(d) add/query | O(d × w) | Accuracy vs table dimensions |
| **Timing Wheels** | Scheduling | O(1) start/cancel | O(slots) | Granularity vs wheel levels |
| **OT** | Collaboration | O(ops²) worst case | O(history) | Correctness vs implementation complexity |
