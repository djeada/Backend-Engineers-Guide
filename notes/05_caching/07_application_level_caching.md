## Application-Level Caching

Application-level caching stores computed results or frequently accessed objects directly inside the running process or in a dedicated in-process store. Because data never leaves the application's memory space, reads are limited only by CPU and memory bandwidth — no network hop, no serialisation, and no socket overhead. This makes application-level caches the fastest possible cache tier, complementing distributed caches like Redis or Memcached that serve data across multiple instances.

```
               Application-Level vs Distributed Cache

  Single Process                       Distributed Setup
  +--------------------------+         +----------------------------------+
  |  Application Instance    |         | App1   App2   App3   App4       |
  |                          |         | +---+  +---+  +---+  +---+      |
  |  +--------------------+  |         | |L1 |  |L1 |  |L1 |  |L1 |     |
  |  |  In-Process Cache  |  |         | +--++  +--++  +-+-+  +-+-+     |
  |  | (heap / off-heap)  |  |         |    |      |     |       |       |
  |  +--------+-----------+  |         |    +--+---+--+--+       |       |
  |           |              |         |       |         |       |       |
  |           v              |         |  +----+----+ +--+----+  |       |
  |  +--------------------+  |         |  | Redis / | | Redis / | |      |
  |  |  Database / Source |  |         |  |Memcached | |Memcached| |      |
  |  +--------------------+  |         |  +---------+ +---------+  |     |
  +--------------------------+         +----------------------------------+

  In-process cache = L1 (ultra-fast, node-local)
  Distributed cache = L2 (fast, cluster-wide)
  Database = source of truth
```

- An in-process cache is **faster** than any network-based store because it requires no serialisation or I/O to serve a cached entry.
- Application-level caches are **bounded** by the JVM heap or native memory limit of a single process, unlike distributed caches that scale across many nodes.
- When multiple application instances run behind a load balancer, each instance holds its own **independent** cache, meaning cache entries are not shared across nodes without a distributed layer.
- A local cache combined with a distributed cache forms a **two-tier** hierarchy that minimises latency for hot keys while still maintaining cluster-wide consistency.
- Cache population is **event-driven** in most frameworks, triggered automatically on a cache miss or explicitly pre-loaded at startup.

### Common In-Process Cache Libraries

#### Caffeine (Java)

Caffeine is a high-performance, near-optimal Java caching library based on the W-TinyLFU eviction algorithm.

```java
LoadingCache<String, Product> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(5))
    .refreshAfterWrite(Duration.ofMinutes(1))
    .recordStats()
    .build(key -> productRepository.findById(key));

Product p = cache.get("product:42");  // auto-loads on miss
```

- The W-TinyLFU policy is **optimal** for workloads with skewed access patterns because it evicts items with both low frequency and low recency.
- `expireAfterWrite` resets the TTL after each **write**, ensuring stale entries are eventually removed even if they remain popular.
- `refreshAfterWrite` triggers a **background** reload after the specified interval while still serving the old value until the refresh completes.
- `maximumSize` bounds heap usage, and the eviction algorithm automatically **selects** the lowest-value entries when the limit is reached.
- Caffeine's `recordStats()` method exposes **metrics** including hit rate, load time, and eviction count via a `CacheStats` object.

#### Guava Cache (Java)

Guava Cache is the predecessor to Caffeine and is still widely used in the Java ecosystem.

```java
LoadingCache<String, User> userCache = CacheBuilder.newBuilder()
    .maximumSize(5000)
    .expireAfterAccess(10, TimeUnit.MINUTES)
    .weakValues()
    .build(key -> userDao.load(key));
```

- `expireAfterAccess` removes entries that have not been **read** within the specified duration, which is useful for session-like data.
- `weakValues()` tells Guava to hold values via weak references, allowing the garbage collector to **reclaim** memory under pressure.
- Guava Cache is **thread-safe** by default and segments its internal structure to reduce contention under concurrent reads and writes.

#### Ehcache (Java)

Ehcache is a full-featured cache framework widely used in enterprise Java and Spring applications.

```xml
<!-- ehcache.xml -->
<cache name="products"
       maxEntriesLocalHeap="10000"
       timeToLiveSeconds="300"
       timeToIdleSeconds="120"
       overflowToDisk="true">
</cache>
```

- Ehcache supports both **heap** and off-heap storage, allowing very large caches without adding GC pressure.
- Off-heap storage serialises entries to native memory that is **not** managed by the JVM garbage collector.
- Ehcache integrates with **JCache** (JSR-107), enabling portable cache code that can be swapped between providers.
- Terracotta clustering adds a distributed **tier** to Ehcache for sharing entries across multiple nodes without a separate Redis deployment.

#### Python: functools.lru_cache and cachetools

```python
from functools import lru_cache
from cachetools import TTLCache, cached

@lru_cache(maxsize=512)
def get_config(key: str) -> str:
    return db.fetch(key)

_ttl_cache: TTLCache = TTLCache(maxsize=1000, ttl=300)

@cached(cache=_ttl_cache)
def get_user(user_id: int) -> dict:
    return user_service.fetch(user_id)
```

- `lru_cache` uses Python's **built-in** LRU eviction and is suitable for functions whose inputs have a small, bounded cardinality.
- `cachetools.TTLCache` adds time-based **expiry** on top of LRU eviction, removing entries that are older than the configured TTL.
- Neither cache is **thread-safe** by default under concurrent writes, so a lock wrapper is needed in multithreaded applications.

#### Node.js: node-cache and lru-cache

```javascript
import LRU from 'lru-cache';

const cache = new LRU({
  max: 500,
  ttl: 1000 * 60 * 5,  // 5 minutes
});

function getProduct(id) {
  const hit = cache.get(id);
  if (hit) return hit;
  const product = db.query(id);
  cache.set(id, product);
  return product;
}
```

- `lru-cache` is a widely-used **npm** package providing an LRU cache with optional TTL support.
- Because Node.js runs on a single event-loop thread, in-process caches require **no** locking for concurrent access within the same process.
- Multiple Node.js worker processes (via `cluster` or PM2) each have their own **isolated** cache, making a distributed layer necessary for cross-process consistency.

#### Go: sync.Map and groupcache

```go
var cache sync.Map

func GetUser(id string) *User {
    if val, ok := cache.Load(id); ok {
        return val.(*User)
    }
    user := db.FetchUser(id)
    cache.Store(id, user)
    return user
}
```

- `sync.Map` provides **concurrent** read and write access without explicit locking, optimised for the case where entries are written once and read many times.
- `groupcache` (from the Go team) fills the gap between a simple map and Redis by providing **consistent** hashing, request coalescing, and hot-key replication across a small cluster of app servers.
- Libraries like `ristretto` from Dgraph offer a more **sophisticated** eviction algorithm (TinyLFU) and metrics collection for production Go services.

### Cache Patterns at the Application Layer

#### Cache-Aside

```
  Application code manages loading:

  func Get(key) -> value:
    val = cache.get(key)
    if val == nil:
      val = db.fetch(key)
      cache.set(key, val, ttl)
    return val
```

- The calling code is **responsible** for populating the cache on a miss, giving it full control over what is stored and for how long.
- This pattern is **lazy**: data is only loaded into the cache when it is first requested, keeping memory usage proportional to actual demand.

#### Read-Through

- The cache itself is **responsible** for fetching from the backing store on a miss, using a loader function configured at setup time.
- Read-through simplifies **calling** code because it always reads from a single interface regardless of whether the data is cached.
- `Caffeine.build(loader)` and Spring's `@Cacheable` annotation both implement the **read-through** pattern transparently.

#### Write-Through

- Every write goes to both the cache and the **backing** store synchronously before the operation is acknowledged.
- Write-through keeps the cache **consistent** with the database at the cost of higher write latency.
- Spring's `@CachePut` annotation implements **write-through** by updating the cache entry alongside the database call.

#### Write-Behind (Write-Back)

- The application writes to the cache **immediately** and defers persistence to the backing store asynchronously.
- Write-behind improves **write** throughput by batching multiple updates into fewer database calls.
- The risk of data loss is **higher** because any crash between the cache write and the deferred flush can result in lost updates.

#### Refresh-Ahead

- The cache **pre-emptively** refreshes an entry in the background before it expires, ensuring reads never block on a slow loader.
- Caffeine's `refreshAfterWrite` implements this pattern by triggering a **background** reload when a read occurs after the refresh threshold has passed.
- Refresh-ahead is most **beneficial** for entries with predictable, high-frequency access where expiry-induced latency spikes are unacceptable.

### Invalidation Strategies

```
  Invalidation Approaches

  Time-based (TTL)         Event-based              Version-based
  +---------------+        +---------------+         +--------------+
  | Entry expires |        | DB update     |         | Key includes |
  | after N secs  |        | triggers a    |         | version or   |
  | automatically |        | cache.delete  |         | hash suffix  |
  +---------------+        +---------------+         +--------------+
  Simple, no coupling    Precise, event-driven     No invalidation needed;
  Risk: stale data       Complexity: messaging     old keys expire naturally
```

- Time-to-live invalidation is **simple** to implement but may serve stale data for the entire TTL interval after an update.
- Event-driven invalidation reacts to **domain** events (e.g., "product updated") and removes or refreshes the affected key immediately.
- Version-based keys embed a **hash** of the data version into the cache key so a data change produces a new key and the old entry is naturally displaced.
- Spring's `@CacheEvict` annotation removes **specific** cache entries by key or clears the entire cache when a method modifies underlying data.

### Two-Tier (L1 + L2) Caching

Many production architectures combine a local in-process cache (L1) with a distributed cache (L2) for maximum efficiency.

```
  Two-Tier Cache Read Flow

  App Instance
  +--------------------------------------------+
  |  1. Check L1 (Caffeine / lru-cache)         |
  |         |                                   |
  |    HIT  +  MISS                             |
  |     |         |                             |
  |     v         v                             |
  |  Return    2. Check L2 (Redis / Memcached)  |
  |  value          |                           |
  |            HIT  +  MISS                     |
  |             |         |                     |
  |             v         v                     |
  |     Populate L1   3. Fetch from DB          |
  |     Return val        |                     |
  |                  Populate L2 + L1           |
  |                  Return value               |
  +--------------------------------------------+
```

- L1 serves the **hottest** keys with zero network latency; L2 catches misses that fall through from L1.
- L1 invalidation across nodes is **challenging** because a write on one instance does not automatically update the in-process caches of other instances.
- Pub/Sub invalidation broadcasts a **delete** message over Redis or a message queue so all instances evict their local copy when the source data changes.
- Short L1 TTLs (a few seconds) combined with longer L2 TTLs achieve a **balance** between staleness risk and latency reduction.
- Near-cache patterns keep a **replica** of a remote distributed cache entry locally, refreshed on demand, and are used by frameworks like Hazelcast and Apache Ignite.

### Sizing and Capacity Planning

- The target hit rate for an in-process cache is typically **95%** or higher; lower rates suggest the cache is undersized or the key space is too large.
- Access frequency histograms should **guide** sizing: if the top 1 % of keys account for 80 % of requests, a small cache serving those keys provides most of the benefit.
- Heap impact can be **estimated** by multiplying the average serialised entry size by the maximum number of entries.
- Off-heap caches in Ehcache or Chronicle Map allow **large** caches (tens of GB) without triggering long GC pauses.
- Monitoring eviction rate trends over time is **important** to detect a growing working set that is outpacing the configured cache size.

### Observability

- Hit rate, miss rate, load time, and eviction count are the **core** metrics every application cache should expose.
- Caffeine's `CacheStats` object provides all **four** standard metrics and integrates with Micrometer for Prometheus or Datadog export.
- Tracing cache operations with OpenTelemetry spans makes it **visible** how much time each request spends in cache lookup versus database I/O.
- Setting up alerts on a sudden drop in hit rate is **valuable** for catching cache misconfigurations or deployment-induced invalidation storms.
- Logging slow cache loads (loader duration > threshold) helps **identify** backing queries that need their own optimisation independent of the cache.
