
### 1. Geohash

**What it is:** A string encoding of latitude/longitude into a hierarchical grid.
**Why it’s important:** Enables very fast proximity searches (e.g. “find all users within 1 km”) by turning 2D spatial queries into simple prefix lookups. Interviewers often probe how you’d build location-based services (ride-share, geofencing), and Geohash shows you understand spatial indexing.

---

### 2. Quadtree

**What it is:** A tree that recursively partitions 2D space into four quadrants.
**Why it’s important:** Supports efficient window/region queries and dynamic spatial indexing. In system design, you might use Quadtrees to shard geospatial data across servers or accelerate map-tile rendering—knowing it demonstrates spatial-data handling at scale.

---

### 3. Consistent Hashing

**What it is:** A hashing scheme that minimizes remapping when nodes join/leave the cluster.
**Why it’s important:** The go-to for distributing cache entries or data partitions (e.g. in a distributed cache or DHT) so that only \~1/N keys move on topology changes. Interviewers will expect you to know how to scale caches (e.g. Memcached) without a massive cache-miss storm on resizing.

---

### 4. Leaky-Bucket

**What it is:** A rate-limiting algorithm that smooths bursts by processing tokens at a fixed rate.
**Why it’s important:** Illustrates how to enforce steady request throughput (e.g. API gateways). In interviews, designing a throttling layer often comes up, and Leaky-Bucket shows you can bound QPS and prevent overload.

---

### 5. Token-Bucket

**What it is:** A rate-limiter that allows bursts up to a bucket size but enforces a long-term rate.
**Why it’s important:** More flexible than Leaky-Bucket—lets you absorb short spikes while still capping average rate. Interviewers like to discuss fair-use policies and burst-tolerant rate limits; Token-Bucket is fundamental.

---

### 6. Trie

**What it is:** A prefix tree for storing strings.
**Why it’s important:** Powers lightning-fast autocomplete, IP routing tables, dictionary lookups. When you design a search-as-you-type feature or need compact prefix storage (e.g. banned words filter), Tries show you can optimize both space and lookup latency.

---

### 7. Rsync

**What it is:** A delta-transfer algorithm that synchronizes files by sending only changed blocks.
**Why it’s important:** Critical for efficient backups, CDN origin-pull, or database replication. Interviewers may ask how to sync large datasets over the network with minimal bandwidth; Rsync’s rolling-checksum trick is the classic answer.

---

### 8. Raft / Paxos

**What it is:** Consensus protocols to agree on a single sequence of operations in a distributed cluster.
**Why it’s important:** Core to building strongly consistent distributed systems (e.g. leader election, replicated logs in databases like etcd, Spanner). In any fault-tolerance discussion, you’ll need to contrast CP vs. AP (CAP theorem) and show you understand how systems stay in sync despite node failures.

---

### 9. Bloom Filter

**What it is:** A space-efficient probabilistic data structure for set membership with false positives.
**Why it’s important:** Used to avoid expensive lookups (e.g. “is this key in the cache?” or “have we seen this URL before?”). In interview scenarios around caching or big-data pipelines, Bloom filters demonstrate you can trade a tiny error rate for huge memory savings.

---

### 10. Merkle Tree

**What it is:** A hash tree where each parent summarizes its children’s hashes.
**Why it’s important:** Enables efficient, tamper-evident verification of large datasets (e.g. git, blockchain, database replicas). When designing systems that need to detect or reconcile divergent data (e.g. anti-entropy in Dynamo), Merkle trees are your tool.

---

### 11. HyperLogLog

**What it is:** A streaming algorithm for cardinality estimation (count distinct) using tiny memory.
**Why it’s important:** Real-time analytics often need “unique user” or “distinct search terms” counts on massive streams. In scale-out designs, HyperLogLog shows you can give approximate metrics with sub-kilobyte state.

---

### 12. Count-Min Sketch

**What it is:** A probabilistic frequency-counting structure with fixed size.
**Why it’s important:** Lets you track “top-k” heavy hitters (e.g. popular products, trending hashtags) in streaming data. Interviewers frequently ask how to monitor high-volume logs or metrics without storing every event; Count-Min Sketch is a key answer.

---

### 13. Hierarchical Timing Wheels

**What it is:** A timer-wheel structure to manage millions of timeouts efficiently.
**Why it’s important:** Critical for schedulers (e.g. TCP retransmission timers, cache-entry TTLs) at high scale. In system design, you’ll be asked how to handle huge numbers of delayed jobs or network timeouts without O(N) per-tick overhead.

---

### 14. Operational Transformation

**What it is:** An algorithm for real-time collaborative editing that merges concurrent operations.
**Why it’s important:** Powers Google Docs-style collaborative applications. When discussing collaborative systems or CRDTs (Conflict-Free Replicated Data Types), knowing OT shows you can handle concurrent state updates with consistency guarantees.
