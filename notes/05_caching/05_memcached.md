## Memcached

Memcached is a high-performance, distributed, in-memory key-value cache originally created at LiveJournal in 2003 and now used by many of the world's largest web services. Its design philosophy prioritises **simplicity**: one data type (byte strings up to 1 MB), a minimal command set, and a multi-threaded architecture that saturates all available CPU cores. This makes Memcached an excellent choice for straightforward caching workloads where raw throughput and low latency matter more than rich data structures or durability.

```
              Memcached Cluster Overview

  +----------+   +----------+   +----------+
  | Client 1 |   | Client 2 |   | Client 3 |
  +----+-----+   +----+-----+   +----+-----+
       |               |               |
       |  Consistent-hash routing      |
       v               v               v
  +---------+    +---------+    +---------+
  | Node A  |    | Node B  |    | Node C  |
  | (Slab)  |    | (Slab)  |    | (Slab)  |
  +---------+    +---------+    +---------+
    Keys 0-X       Keys X-Y      Keys Y-Z
```

- Memcached is **designed** for horizontal scalability, allowing operators to add nodes without restarting existing ones.
- The client library is **responsible** for partitioning keys across nodes, which means the server requires no inter-node communication.
- An absence of replication at the server level means Memcached is **suited** for use cases that can tolerate cache loss without data corruption.
- All stored values are **volatile**: a server restart empties the cache completely and the data must be repopulated from the primary store.
- Memcached's multi-threaded model is **efficient** at utilising multiple CPU cores, giving it an edge over single-threaded architectures for raw throughput.

### Architecture

- The Memcached process listens on a single TCP or UDP port and handles **concurrent** connections via a thread pool backed by libevent.
- Each worker thread maintains its own event loop and processes commands **independently**, avoiding global locks on the hot path.
- Memory is pre-allocated at startup and organised into **slabs** — groups of fixed-size chunks — so malloc/free overhead is eliminated during runtime.
- The slab allocator assigns items to the slab class whose chunk size best **fits** the item, wasting a small amount of space in exchange for constant-time allocation.
- A background maintenance thread handles **LRU** crawling, expired-item reclamation, and statistics gathering without blocking worker threads.

```
  Slab Allocator Memory Layout

  +-------------------------------------------+
  |       Memcached Process Memory Pool        |
  +---------------+--------------+-------------+
  | Slab Class 1  | Slab Class 2 | Slab Class 3|
  | chunk=96 B    | chunk=120 B  | chunk=152 B |
  +---+---+---+---+---+---+---+--+---+---+-----+
  |[  ][ ]|[  ][  ]|[  ][  ]|   |[  ][  ]|     |
  | page 1       | page 2      | page 3         |
  +-------------------------------------------+
```

- Slab classes grow by a configurable **factor** (default 1.25×), balancing the number of size classes against internal fragmentation.
- Items that exceed the largest slab class chunk size are **rejected** with a "value too large" error, capping object size at 1 MB by default.
- The `stats slabs` command exposes **granular** per-class utilisation data, helping operators identify fragmentation or mismatched chunk sizes.

### Core Commands

Memcached exposes a compact ASCII (or binary) protocol with a small set of verbs.

| Command | Description | Example |
|---------|-------------|---------|
| `set` | Store a value unconditionally | `set key 0 300 5\r\nhello` |
| `add` | Store only if key does not exist | `add key 0 60 3\r\nfoo` |
| `replace` | Store only if key already exists | `replace key 0 60 3\r\nbar` |
| `get` | Retrieve one or more values | `get key1 key2` |
| `gets` | Retrieve value with CAS token | `gets key` |
| `cas` | Store only if CAS token matches | `cas key 0 60 3 <token>\r\nnew` |
| `delete` | Remove a key | `delete key` |
| `incr`/`decr` | Increment or decrement a counter | `incr counter 1` |
| `flush_all` | Invalidate all items | `flush_all` |
| `stats` | Return server statistics | `stats` |

- The `set` command accepts a **flags** field (a 16-bit integer) that clients use to store metadata such as serialisation format hints.
- The expiration parameter is **interpreted** as seconds from now if less than 30 days (2,592,000 s), or as a Unix timestamp otherwise.
- The `cas` (check-and-set) command provides **optimistic** concurrency, preventing lost updates when two clients race to modify the same key.
- `incr`/`decr` operate atomically on **numeric** string values, making them useful for counters and rate limiters without external locking.

### Client-Side Partitioning

Because Memcached nodes do not communicate with each other, the client library is **entirely** responsible for mapping keys to nodes.

```
  Client-Side Key Routing

  Key = "user:42:profile"
  Hash = CRC32("user:42:profile") = 0x7A3F...
  Node = hash % num_nodes  OR  consistent-hash ring lookup

       +------+     hash("user:42")       +---------+
       |Client+-------------------------->| Node B  |
       +------+                           +---------+

       +------+     hash("post:99")       +---------+
       |Client+-------------------------->| Node C  |
       +------+                           +---------+
```

- Modulo hashing is **simple** but causes mass key redistribution whenever a node is added or removed from the pool.
- Consistent hashing places nodes on a **ring** so that only a small fraction of keys must be remapped when topology changes.
- Virtual nodes (vnodes) improve **balance** by giving each physical node multiple positions on the consistent-hash ring.
- Client libraries like libmemcached, spymemcached, and pylibmc implement consistent hashing and connection pooling **automatically**.
- Ketama is the most **widely** adopted consistent-hash algorithm for Memcached, originally developed by Last.fm.

### Expiration and Eviction

- Every item is stored with a **TTL** expressed in seconds; when the TTL elapses the item becomes logically expired.
- Memcached uses **lazy** expiration: expired items are not removed proactively but are evicted when their memory slot is needed for a new item.
- When all slab pages are occupied and no expired items are available, Memcached uses **LRU** eviction to reclaim the least-recently-used slot within the target slab class.
- The segmented LRU (SLRU) introduced in Memcached 1.5 separates **hot** and cold item queues, reducing the chance that frequently accessed items are evicted by large sequential scans.
- Setting very long TTLs on rarely updated data combined with **explicit** deletes on updates is a common pattern that balances staleness risk with memory efficiency.

### Use Cases

- Session storage for stateless **web** applications stores short-lived user sessions so any server in the cluster can authenticate a request.
- Database query result **caching** stores the output of expensive SQL queries, reducing read load on the primary database.
- Object caching keeps deserialized application objects—product records, user profiles—in **memory** to avoid repeated database round-trips and deserialisation overhead.
- Rate limiting counters use `incr` with a TTL to **track** the number of API calls per client within a sliding window.
- Fragment caching stores partial **HTML** or JSON responses to avoid recomputing expensive template sections on every request.
- Pre-computed aggregate caching holds **summary** statistics (total users, daily revenue) that are expensive to recalculate but tolerate slight staleness.

### Memcached vs Redis

| Feature | Memcached | Redis |
|---------|-----------|-------|
| Data structures | Strings only (binary-safe) | Strings, lists, sets, hashes, sorted sets, streams |
| Threading model | Multi-threaded | Single-threaded event loop (I/O threads in Redis 6+) |
| Max value size | 1 MB (default) | 512 MB |
| Persistence | None | RDB snapshots, AOF log |
| Replication | Not built-in (client-side) | Built-in primary-replica |
| Clustering | Client-side consistent hashing | Redis Cluster (server-side, 16 384 hash slots) |
| Pub/Sub | Not supported | Native support |
| Lua scripting | Not supported | Built-in |
| Transactions | Not supported | MULTI/EXEC |
| Memory efficiency | Higher (slab allocator, no metadata) | Moderate (richer structures add overhead) |
| Horizontal scale | Excellent (stateless nodes) | Good (cluster mode required) |
| Best fit | Simple, high-throughput string caching | Multi-purpose cache, broker, and data store |

- Memcached is **preferred** when the workload is purely string caching, memory efficiency is critical, and durability is not required.
- Redis is **chosen** when the application needs complex data structures, persistence, pub/sub messaging, or server-side scripting.
- Both tools can **coexist** in the same architecture, with Memcached serving simple cache-aside patterns and Redis handling richer features like leaderboards or queues.

### Operational Considerations

- Memcached exposes a `stats` command that returns **counters** for get hits, get misses, evictions, bytes stored, and current connections.
- Watching the eviction counter is **critical** because a rising value indicates the cache is undersized for the working set and TTLs or capacity should be adjusted.
- The hit rate (hits / (hits + misses)) is the most **important** operational metric, typically targeting 95 %+ for production caches.
- Graceful node removal involves **redirecting** traffic to the remaining nodes before stopping the instance to avoid a sudden spike of cache misses.
- Memory overhead per item in Memcached is approximately **57 bytes** for the internal item structure plus the key and value sizes.
- Tuning the `-m` (max memory), `-t` (thread count), and `-I` (max item size) flags at startup is **necessary** to match available hardware resources.

### Security

- Memcached has no built-in **authentication** mechanism in its ASCII protocol, so it must be protected at the network layer.
- Binding Memcached to a loopback or private network interface is **essential** to prevent unauthorised external access.
- Firewall rules should **restrict** port 11211 (TCP/UDP) to trusted application servers only.
- Exposing Memcached's UDP port to the internet has been **exploited** in large-scale DDoS amplification attacks due to the asymmetric response size.
- Disabling the UDP listener with `-U 0` is **recommended** in deployments where UDP is not required.
- SASL authentication is available in some **builds** of Memcached and the binary protocol, offering a basic credential check for clients.
