## Caching

Caching is a technique used to speed up data retrieval by placing frequently accessed or computationally heavy information closer to the application or the end user. Below is an expanded set of notes on caching, presented with a simple ASCII diagram and bullet points that emphasize key considerations. Each bullet point is a complete sentence containing a single **bold** word in the middle.

```
  +-------------+           +-------------+
  |   Client    |           |   Server    |
  |             |           |             |
  |             |  Request  |             |
  |             +---------->+             |
  |             |           |             |
  |             |<----------+             |
  +------+------|           +------+------+
         |Cache |           |  Data  |
         |Miss  |           | Storage|
         |      |           |        |
         |      |           |        |
  +------v------+           +--------v-----+
  |   Cache     |           |              |
  |(Fast Access)|<----------+              |
  +-------------+  Cached   |              |
                            |              |
                            +--------------+
```

- A caching strategy can be **beneficial** for reducing round-trip times between clients and the primary data store.  
- Caching can be **vulnerable** to data staleness when updates in the main data store are not immediately reflected in the cache.  
- Cache hits can be **tracked** to measure how often requested items are served from the cache versus the underlying system.  
- Cache misses can be **costly** because they require fetching data from slower storage and populating the cache.  
- The overall memory footprint can be **optimized** by selecting cache eviction policies that remove unneeded or rarely used data.

### Types of Cache

Modern computing stacks use multiple caches at different layers, each addressing a specific scope and performance requirement.

- Hardware caches are **essential** at the CPU level (L1, L2, L3) or between main memory and disk, reducing memory access times.  
- An application server cache is **helpful** when frequently accessed items are kept in memory, decreasing database load.  
- A distributed cache can be **useful** for sharing cached data across multiple server instances in a cluster.  
- A Content Delivery Network (CDN) can be **advantageous** for caching static assets close to users, minimizing latency.  
- Edge caching can be **adopted** at the network boundary to deliver region-specific or frequently used data faster.

### Cache Write Policies

Different write policies determine how the cache interacts with the underlying data store during write operations.

- A write-through approach can be **reliable** because all writes are immediately persisted to both cache and storage, albeit with higher latency.  
- A write-around method is **practical** for workloads that do not require recently written items to appear in the cache right away.  
- A write-back (write-behind) policy is **faster** for writes because the cache is updated immediately and the main storage is updated asynchronously.  
- The choice of write policy can be **influential** in balancing consistency, throughput, and risk of data loss.  
- Monitoring asynchronous queues is **needed** in write-back systems to ensure updates eventually reach the primary storage.

### Cache Eviction Policies

When the cache is full, an eviction policy determines which items to discard so that new items can be stored.

- FIFO removes the oldest entries first and can be **straightforward** when items have similar usage patterns.  
- LIFO removes the newest entries first, which can be **uncommon** in modern caching but may be used in specialized scenarios.  
- LRU discards items that have not been accessed for the longest period and is **popular** due to its effectiveness in many real-world usage patterns.  
- LFU targets items with the fewest accesses and is **suitable** when certain objects exhibit much higher popularity than others.  
- Random replacement can be **unpredictable**, but it avoids overhead from tracking usage frequency or order.

### Cache Invalidation and Consistency

Ensuring that the cache reflects changes in the underlying data store can be one of the most **difficult** aspects of caching.

- Time-to-live (TTL) can be **assigned** to each cache entry so it expires automatically after a set duration.  
- Explicit invalidation calls can be **triggered** whenever an update is made to the primary data, removing or refreshing outdated cache entries.  
- Versioning or checksums are **helpful** for identifying outdated data in distributed caches.  
- Stale reads might be **tolerable** in some applications (eventually consistent scenarios) but unacceptable in strictly consistent systems.  
- Consistency requirements can be **varied**, ranging from strong consistency to eventual or read-your-own-write guarantees.

### Multi-Layer Caching

Some architectures employ multiple cache layers, each targeting different bottlenecks or data usage patterns.

```
Client
  |
  | (Browser Cache)
  |
  v
Reverse Proxy / CDN
  |
  | (Edge Cache)
  |
  v
Application Server
  |
  | (In-Memory Cache)
  |
  v
Database or Persistent Store
```

- A multi-layer approach can be **helpful** for capturing opportunities to cache at every step in the data retrieval process.  
- Browser caches can be **encouraged** by sending appropriate HTTP headers (e.g., Cache-Control, ETag).  
- In-memory caches on the server side can be **valuable** for storing session data, configurations, or frequently accessed queries.  
- CDNs and reverse proxies can be **effective** for reducing load on the origin server by delivering cached static and semi-static content.  
- Each layer introduces **complexity** in invalidation and monitoring, requiring careful coordination.

### Monitoring and Metrics

Effective caching strategies rely on continuous monitoring and tuning based on real-world usage patterns.

- A cache hit rate is **crucial** for estimating how effectively the cache serves incoming requests.  
- A cache miss penalty is **significant** for quantifying the extra time spent fetching data from slower storage.  
- Request latency distributions are **observed** to determine if caching is addressing performance hotspots.  
- Memory usage trends are **reviewed** to prevent over-allocation or under-utilization of the cache.  
- Profiling tools can be **utilized** to detect which data is most frequently accessed or frequently invalidated.
