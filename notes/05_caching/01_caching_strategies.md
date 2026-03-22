## Caching

Caching is a technique used to speed up data retrieval by placing frequently accessed or computationally heavy information closer to the application or the end user. Below is an expanded set of notes on caching, presented with ASCII diagrams and bullet points that emphasize key considerations. Each bullet point is a complete sentence containing a single **bold** word in the middle.

```
                 Request Flow (Cache Hit vs. Cache Miss)

  +-----------+                  +------------------+                +------------------+
  |           |  1. Request      |                  |                |                  |
  |  Client   +----------------->+      Cache       |                |   Data Store     |
  |           |                  |   (Fast Access)  |                |   (Disk / DB)    |
  |           |  2a. Cache Hit   |                  |                |                  |
  |           |<-----------------+  +-----------+   |  3. Fetch      |  +------------+  |
  |           |                  |  | Key: Val  |   |  on Miss       |  | Tables     |  |
  +-----------+                  |  | Key: Val  |   +--------------->+  | Rows       |  |
                                 |  +-----------+   |  4. Return     |  | Docs       |  |
                                 |                  |<---------------+  +------------+  |
                                 |  5. Store result |                |                  |
                                 +------------------+                +------------------+
```

- A caching strategy can be **beneficial** for reducing round-trip times between clients and the primary data store.
- Caching can be **vulnerable** to data staleness when updates in the main data store are not immediately reflected in the cache.
- Cache hits can be **tracked** to measure how often requested items are served from the cache versus the underlying system.
- Cache misses can be **costly** because they require fetching data from slower storage and then populating the cache.
- The overall memory footprint can be **optimized** by selecting cache eviction policies that remove unneeded or rarely used data.
- Latency improvements from caching are **measurable** by comparing response times for cache hits against the full retrieval path.

### Types of Cache

Modern computing stacks use multiple caches at different layers, each addressing a specific scope and performance requirement.

- Hardware caches are **essential** at the CPU level (L1, L2, L3) or between main memory and disk, reducing memory access times.
- An application server cache is **helpful** when frequently accessed items are kept in memory, decreasing database load.
- A distributed cache can be **useful** for sharing cached data across multiple server instances in a cluster.
- A Content Delivery Network (CDN) can be **advantageous** for caching static assets close to users, minimizing latency.
- Edge caching can be **adopted** at the network boundary to deliver region-specific or frequently used data faster.
- Local in-process caches are **lightweight** because they avoid network hops, though they cannot share state across multiple nodes.

### Cache-Aside (Lazy Loading) Pattern

The cache-aside pattern is one of the most widely used strategies, where the application code manages reads and writes to the cache explicitly.

```
  Cache-Aside Read Flow

  +-------------+        +--------------+        +----------------+
  |             | 1. Get |              |        |                |
  | Application +------->+    Cache     |        |   Data Store   |
  |   Code      |        |              |        |                |
  |             |  HIT?  |              |        |                |
  |             |<-------+              |        |                |
  |             |                       |        +-------+--------+
  |             | Yes: return value     |                ^  |
  |             |                       |                |  |
  |             | No:                   |                |  |
  |             +-- 2. Query DB ----------------------->+  |
  |             |<--- 3. Return result -----------------+  |
  |             +-- 4. Store in cache -->+              |   |
  +-------------+                       +--------------+   |
                                                           v
```

- The application first **checks** the cache and only queries the database when the requested item is not present.
- Stale data is **avoided** by setting a TTL on each entry or by explicitly invalidating keys when writes occur.
- Cache-aside is **flexible** because it gives the application full control over what gets cached and for how long.
- A downside of this pattern is **latency** on the first request for each key, since the cache starts empty and must be populated.
- Combining cache-aside with write-through can be **effective** for workloads that need both fast reads and consistent writes.

### Cache Write Policies

Different write policies determine how the cache interacts with the underlying data store during write operations.

```
   Write-Through              Write-Around               Write-Back (Write-Behind)

  App                        App                         App
   |                          |                           |
   | 1. Write                 | 1. Write                  | 1. Write
   v                          v                           v
  Cache ---- 2. Write ---> DB |                          Cache
   |         (synchronous)    +--- 2. Write ---> DB       |
   |                          |    (bypass cache)         | 2. Ack to app
   | 3. Ack                   | 3. Ack                    |    (immediate)
   v                          v                           |
  App                        App                          +--- 3. Async flush ---> DB
                                                          |    (batched / delayed)
   * Consistent               * Avoids cache pollution    |
   * Higher write latency     * Cache miss on next read   * Fastest writes
                                                          * Risk of data loss
```

- A write-through approach can be **reliable** because all writes are immediately persisted to both cache and storage, albeit with higher latency.
- A write-around method is **practical** for workloads that do not require recently written items to appear in the cache right away.
- A write-back (write-behind) policy is **faster** for writes because the cache is updated immediately and the main storage is updated asynchronously.
- The choice of write policy can be **influential** in balancing consistency, throughput, and risk of data loss.
- Monitoring asynchronous queues is **needed** in write-back systems to ensure updates eventually reach the primary storage.
- Write-through paired with cache-aside reads is **common** in production systems that prioritize strong consistency without sacrificing read speed.

| Policy | Write Latency | Read After Write | Consistency | Data Loss Risk |
|---|---|---|---|---|
| Write-Through | Higher (two writes) | Always a cache hit | Strong | Very low |
| Write-Around | Lower (one write) | Cache miss until next read | Eventual | Very low |
| Write-Back | Lowest (cache only) | Always a cache hit | Eventual | Higher if cache crashes |

### Cache Eviction Policies

When the cache is full, an eviction policy determines which items to discard so that new items can be stored.

```
  Eviction Policy Comparison

  FIFO (First In, First Out)           LRU (Least Recently Used)
  +---+---+---+---+---+               +---+---+---+---+---+
  | A | B | C | D | E |  <- Full      | A | B | C | D | E |  <- Full
  +---+---+---+---+---+               +---+---+---+---+---+
    ^                                    ^
    |  Evict A (oldest arrival)          |  Evict A (longest since
    |  regardless of access              |  last access)
    +-- Insert F here                    +-- Insert F here

  LFU (Least Frequently Used)          Random Replacement
  +---+---+---+---+---+               +---+---+---+---+---+
  | A | B | C | D | E |  <- Full      | A | B | C | D | E |  <- Full
  +---+---+---+---+---+               +---+---+---+---+---+
        ^                                       ^
        |  Evict B (fewest total                |  Evict C (chosen
        |  accesses over lifetime)              |  at random)
        +-- Insert F here                       +-- Insert F here
```

- FIFO removes the oldest entries first and can be **straightforward** when items have similar usage patterns.
- LIFO removes the newest entries first, which can be **uncommon** in modern caching but may be used in specialized scenarios.
- LRU discards items that have not been accessed for the longest period and is **popular** due to its effectiveness in many real-world usage patterns.
- LFU targets items with the fewest accesses and is **suitable** when certain objects exhibit much higher popularity than others.
- Random replacement can be **unpredictable**, but it avoids overhead from tracking usage frequency or order.
- Adaptive policies like ARC (Adaptive Replacement Cache) are **sophisticated** because they dynamically balance recency and frequency.

| Policy | Tracking Overhead | Best For | Weakness |
|---|---|---|---|
| FIFO | Minimal (insertion order) | Uniform access patterns | Ignores access frequency |
| LRU | Moderate (last access time) | Temporally clustered reads | Scan pollution from one-time reads |
| LFU | Higher (access counters) | Skewed popularity distributions | Stale popular items linger |
| Random | None | Simple implementations | No adaptation to workload |

### Cache Stampede and Thundering Herd

A cache stampede occurs when a frequently accessed cache entry expires and many concurrent requests simultaneously attempt to regenerate it, overwhelming the data store.

```
  Cache Stampede Scenario                     Mitigation: Locking / Lease

                  TTL expires
  Request 1 --+       |                      Req 1 --> MISS --> Acquire lock --> Query DB
  Request 2 --+       v                                                          |
  Request 3 --+  +---------+  +----------+  Req 2 --> MISS --> Lock held, wait   |
  Request 4 --+->|  Cache  +->|Data Store|  Req 3 --> MISS --> Lock held, wait   |
  ...            |  MISS!  +->|          |                                       v
  Request N --+  +---------+->|Overloaded|  Cache now populated <----------------+
                              +----------+  Req 2 --> HIT (served from cache)
                                            Req 3 --> HIT (served from cache)
```

- A cache stampede can be **devastating** for backend systems because hundreds of threads may simultaneously query the database for the same key.
- Distributed locks or leases are **employed** so that only one request regenerates the cache entry while others wait for the result.
- Probabilistic early expiration is **useful** because it randomly refreshes entries slightly before TTL, spreading regeneration load over time.
- Serving slightly stale data during regeneration is **acceptable** in many applications and prevents cascading failures under heavy load.
- Request coalescing can be **implemented** at the cache layer to merge duplicate in-flight requests into a single backend query.

### Cache Warming

Cache warming is the practice of pre-populating the cache before it begins serving live traffic, preventing a flood of cold misses on startup.

- Loading frequently accessed keys at startup is **important** for applications that cannot tolerate high latency during the initial ramp-up period.
- Historical access logs can be **analyzed** to determine which keys should be preloaded into the cache based on past traffic patterns.
- Warming scripts are **scheduled** to run during deployment windows so the cache is fully populated before traffic is routed to the new instance.
- Gradual traffic shifting can be **combined** with cache warming, routing a small percentage of requests to a new node until its cache is hot.

### Distributed Cache Considerations

When caches span multiple nodes, additional challenges arise around partitioning, replication, and network overhead.

- Consistent hashing is **preferred** for distributing keys across cache nodes because adding or removing a node only remaps a small fraction of keys.
- Replication across cache nodes can be **configured** to improve availability, though it increases memory usage and write amplification.
- Network partitions can be **problematic** in distributed caches, leading to split-brain scenarios where different nodes hold conflicting data.
- Serialization format choices are **relevant** because compact binary formats reduce the bandwidth consumed by cache reads and writes across the network.
- Cluster topology changes are **managed** through health checks and automatic rebalancing to keep the key space evenly distributed.

### Cache Invalidation and Consistency

Ensuring that the cache reflects changes in the underlying data store can be one of the most **difficult** aspects of caching.

- Time-to-live (TTL) can be **assigned** to each cache entry so it expires automatically after a set duration.
- Explicit invalidation calls can be **triggered** whenever an update is made to the primary data, removing or refreshing outdated cache entries.
- Versioning or checksums are **helpful** for identifying outdated data in distributed caches.
- Stale reads might be **tolerable** in some applications (eventually consistent scenarios) but unacceptable in strictly consistent systems.
- Consistency requirements can be **varied**, ranging from strong consistency to eventual or read-your-own-write guarantees.
- Event-driven invalidation through message queues is **scalable** because cache nodes subscribe to change events and invalidate affected keys.

### Multi-Layer Caching

Some architectures employ multiple cache layers, each targeting different bottlenecks or data usage patterns.

```
  +-------------------+
  |      Client       |
  |  (Browser Cache)  |
  +--------+----------+
           |
           v
  +-------------------+          Serves static assets
  |  Reverse Proxy /  +-------->  from edge locations
  |       CDN         |
  +--------+----------+
           |
           v
  +-------------------+          Local in-process cache
  | Application Server+-------->  (HashMap, Guava, etc.)
  +--------+----------+
           |
           v
  +-------------------+          Redis / Memcached
  | Distributed Cache +-------->  shared cluster
  +--------+----------+
           |
           v
  +-------------------+
  |  Database or      |
  |  Persistent Store |
  +-------------------+
```

- A multi-layer approach can be **helpful** for capturing opportunities to cache at every step in the data retrieval process.
- Browser caches can be **encouraged** by sending appropriate HTTP headers (e.g., Cache-Control, ETag).
- In-memory caches on the server side can be **valuable** for storing session data, configurations, or frequently accessed queries.
- CDNs and reverse proxies can be **effective** for reducing load on the origin server by delivering cached static and semi-static content.
- Each layer introduces **complexity** in invalidation and monitoring, requiring careful coordination.
- Layered TTLs should be **staggered** so that inner caches expire before outer caches, preventing simultaneous expiration storms across all tiers.

### Monitoring and Metrics

Effective caching strategies rely on continuous monitoring and tuning based on real-world usage patterns.

- A cache hit rate is **crucial** for estimating how effectively the cache serves incoming requests.
- A cache miss penalty is **significant** for quantifying the extra time spent fetching data from slower storage.
- Request latency distributions are **observed** to determine if caching is addressing performance hotspots.
- Memory usage trends are **reviewed** to prevent over-allocation or under-utilization of the cache.
- Profiling tools can be **utilized** to detect which data is most frequently accessed or frequently invalidated.
- Eviction rate spikes can be **indicative** of an undersized cache or a sudden shift in access patterns that warrants capacity adjustment.
