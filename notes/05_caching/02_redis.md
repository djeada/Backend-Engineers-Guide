# Redis

Redis is an open-source, in-memory data store that serves as a high-performance cache, message broker, and general-purpose database. It is often called a "data structure server" because it natively supports rich types like strings, lists, sets, sorted sets, and hashes. Because every operation happens in **memory**, Redis achieves sub-millisecond latency for both reads and writes, making it one of the most widely adopted caching layers in modern backend architectures. Understanding how to leverage Redis effectively can dramatically improve the performance, scalability, and responsiveness of your applications.

```
  +-----------+        +-----------+        +-----------+
  | Client A  |        | Client B  |        | Client C  |
  | (Web App) |        | (Worker)  |        |  (CLI)    |
  +-----+-----+        +-----+-----+        +-----+-----+
        |                     |                     |
        | SET/GET             | LPUSH/BRPOP         | PUBLISH
        |                     |                     |
        +----------+----------+----------+----------+
                   |                     |
                   v                     v
        +-------------------------------------------+
        |            Redis Server (Single)          |
        |-------------------------------------------|
        |  Engine: Single-threaded event loop        |
        |  Storage: In-memory key-value store        |
        |  Features:                                 |
        |   - Data Structures (String, List, Set...) |
        |   - Pub/Sub messaging                      |
        |   - Lua scripting                          |
        |   - Transactions (MULTI/EXEC)              |
        |   - TTL-based key expiration               |
        +---------------------+---------------------+
                              |
                   (Optional persistence)
                              |
              +---------------+---------------+
              |                               |
              v                               v
        +-----------+                   +-----------+
        | RDB Dump  |                   | AOF Log   |
        | (Snapshot) |                   | (Append)  |
        +-----------+                   +-----------+
```

## Key Concepts

### In-Memory Data Store

- Redis holds every dataset entirely in **RAM**, which eliminates disk seek latency and enables throughput of hundreds of thousands of operations per second on modest hardware.
- The single-threaded event loop processes commands **sequentially**, avoiding lock contention while still saturating network I/O through efficient multiplexing.
- When physical memory is exhausted, Redis can apply an **eviction** policy (e.g., LRU, LFU, random) to remove less-needed keys and keep the working set in memory.

### Key-Value Store

- Every piece of data in Redis is accessed through a unique **key**, which is always a binary-safe string.
- Values associated with keys can be simple strings or complex **structures** like lists, sets, hashes, and sorted sets.
- Namespacing keys with a colon-delimited **convention** (e.g., `user:1001:profile`) keeps the keyspace organized and easy to scan.

### Data Expiration

- Redis lets you attach a **TTL** (time-to-live) to any key, after which the key is automatically deleted.
- Expiration is handled through a combination of **lazy** deletion (checked on access) and periodic active cleanup by a background task.
- You can set expiration at write time with `SET key value EX 60` or add it later with the **EXPIRE** command.

## Redis Data Structures

Redis supports several first-class data structures, each optimized for different **access** patterns.

```
  +--------------------------------------------------------------+
  |                    Redis Data Structures                      |
  +--------------------------------------------------------------+
  |                                                              |
  |  STRING        LIST             SET           SORTED SET     |
  |  +------+     +---+---+---+   +---+---+---+  +-----+-----+  |
  |  | "Hi" |     | A | B | C |   | X | Y | Z |  |a:1.0|b:2.5|  |
  |  +------+     +---+---+---+   +---+---+---+  +-----+-----+  |
  |                                                              |
  |  HASH                           STREAM                       |
  |  +--------+---------+          +-----+-----+-----+           |
  |  | field1 | value1  |          | ID1 | ID2 | ID3 |           |
  |  | field2 | value2  |          +-----+-----+-----+           |
  |  +--------+---------+                                        |
  +--------------------------------------------------------------+
```

### Strings

- A string is the most **basic** Redis type and can hold text, serialized JSON, or raw binary data up to 512 MB.
- Atomic operations like `INCR` and `DECR` make strings ideal for **counters**, rate limiters, and simple flags.
- The `MGET` and `MSET` commands let you read or write multiple string keys in a single **roundtrip**, reducing network overhead.

### Lists

- Lists are ordered collections of strings maintained as **linked** structures, supporting O(1) pushes and pops from both ends.
- Commands like `LPUSH`, `RPUSH`, `LPOP`, and `RPOP` make lists a natural fit for **queues** and task pipelines.
- Blocking variants such as `BRPOP` allow workers to **wait** for new items without polling, enabling efficient consumer patterns.

### Sets

- A set stores an unordered collection of unique strings, and every add, remove, or membership check runs in **O(1)** time.
- Set operations like `SUNION`, `SINTER`, and `SDIFF` let you compute **relationships** between groups server-side.
- Common use cases include tracking unique **visitors**, storing tags, and implementing friend-of-friend graphs.

### Sorted Sets

- Sorted sets extend regular sets by associating a floating-point **score** with each member, keeping elements ordered by that score.
- The `ZRANGEBYSCORE` command retrieves members within a score **range**, which is useful for time-series data or ranked feeds.
- Leaderboards and priority queues often rely on sorted sets because insertion and ranked **retrieval** both run in O(log N) time.

### Hashes

- A hash maps string fields to string values inside a single key, making it a natural way to represent an **object** (e.g., a user profile).
- Individual fields can be read or written with `HGET` and `HSET` without fetching the entire **structure**, saving bandwidth.
- Redis internally encodes small hashes as a compact **ziplist**, which keeps memory usage low for objects with few fields.

## Redis Persistence

By default Redis is an in-memory store, but it offers two **durability** mechanisms that can be used independently or together.

```
                       Redis Server
                    +----------------+
                    |   In-Memory    |
                    |   Dataset      |
                    +-------+--------+
                            |
           +----------------+----------------+
           |                                 |
     (Point-in-time                   (Every write
       snapshot)                        appended)
           |                                 |
           v                                 v
   +---------------+                +----------------+
   |   RDB File    |                |   AOF File     |
   | (binary dump) |                | (command log)  |
   +---------------+                +----------------+
   | - Compact     |                | - Durable      |
   | - Fast load   |                | - Human-readable|
   | - Data loss   |                | - Larger size  |
   |   between     |                | - Rewritable   |
   |   snapshots   |                |   via BGREWRITE|
   +---------------+                +----------------+
```

### RDB (Redis Database)

- RDB creates a point-in-time **snapshot** of the entire dataset and writes it to a compact binary file on disk.
- Snapshots are triggered by configurable rules such as "save after 900 seconds if at least 1 key **changed**."
- RDB files are excellent for backups and disaster **recovery**, but any writes between snapshots will be lost on a crash.

### AOF (Append-Only File)

- AOF logs every write command to an append-only **file**, providing much stronger durability guarantees than RDB alone.
- The `appendfsync` directive controls how often the OS flushes the log to **disk**: `always`, `everysec`, or `no`.
- Over time the AOF file grows, so Redis can run `BGREWRITEAOF` to **compact** it by replaying only the commands needed to reconstruct the current state.

### Combining RDB and AOF

- Running both mechanisms together gives you fast **restarts** from the AOF plus compact backups from RDB snapshots.
- On startup Redis will prefer the AOF when both files are present, because it is generally more **complete**.

## Redis Cluster and Replication

### Replication

- Redis supports a primary-replica model where one **primary** node accepts all writes and asynchronously streams them to one or more replicas.
- Replicas serve read traffic, providing horizontal **scaling** for read-heavy workloads while keeping write logic simple.
- If the primary fails, Redis Sentinel can **promote** a replica automatically, minimizing downtime.

```
                  +-----------------+
                  |    Primary      |
                  | (Read + Write)  |
                  +--------+--------+
                           |
            +--------------+--------------+
            |  async replication          |  async replication
            v                             v
   +-----------------+           +-----------------+
   |   Replica 1     |           |   Replica 2     |
   |  (Read Only)    |           |  (Read Only)    |
   +-----------------+           +-----------------+
```

### Redis Cluster

- Redis Cluster partitions the keyspace into 16,384 hash **slots** distributed across multiple primary nodes.
- Each node owns a subset of slots and is responsible for the keys that **hash** into that range.
- Clients are redirected with `MOVED` or `ASK` responses when a key lives on a different **node**, and smart client libraries handle this transparently.
- The cluster tolerates failures by replicating each primary to at least one **replica**, which can be promoted if the primary becomes unreachable.

```
  +-------------------+    +-------------------+    +-------------------+
  | Node A (Primary)  |    | Node B (Primary)  |    | Node C (Primary)  |
  | Slots 0-5460      |    | Slots 5461-10922  |    | Slots 10923-16383 |
  +---------+---------+    +---------+---------+    +---------+---------+
            |                        |                        |
            v                        v                        v
  +-------------------+    +-------------------+    +-------------------+
  | Node A' (Replica) |    | Node B' (Replica) |    | Node C' (Replica) |
  +-------------------+    +-------------------+    +-------------------+
```

## Pub/Sub Capabilities

- Redis Pub/Sub lets publishers send messages to named **channels** without knowing which subscribers are listening.
- Subscribers receive messages in real time with very low **latency**, making this pattern ideal for chat systems, live notifications, and event broadcasting.
- Messages are fire-and-forget; if a subscriber is **offline** when a message is published, that message is lost.
- For durable messaging with consumer groups and acknowledgments, Redis **Streams** (introduced in Redis 5.0) are a more robust alternative.

```
  +-----------+           +------------------+          +--------------+
  | Publisher |  PUBLISH  |  Redis Channel   | message  | Subscriber A |
  | (Service) +---------->| "notifications"  +--------->| (Web Socket) |
  +-----------+           +--------+---------+          +--------------+
                                   |
                                   | message
                                   v
                          +--------------+
                          | Subscriber B |
                          | (Worker)     |
                          +--------------+
```

## Using Redis as a Cache

### Cache-Aside (Lazy Loading)

- The application first checks the **cache** for the requested data before querying the primary database.
- On a cache miss the application fetches from the database, writes the result to Redis, and returns it to the **caller**.
- This strategy only caches data that is actually **requested**, keeping memory usage efficient.

### Write-Through

- Every write to the database is simultaneously written to the **cache**, ensuring cached data is always fresh.
- This approach trades higher write **latency** for consistently up-to-date reads and fewer cache misses.

### Cache Invalidation

- Time-based invalidation uses **TTL** values so stale entries expire automatically without extra application logic.
- Event-driven invalidation publishes a message or calls a hook whenever the underlying data **changes**, triggering an explicit delete from the cache.

### Cache Key Design

- Prefix keys with the entity type and include a unique **identifier** (e.g., `product:8842:details`) for clarity.
- Include a schema **version** in the key when the cached data format evolves, preventing deserialization errors on old entries.

## Common Usage Patterns

- **Session** storage keeps user sessions in Redis so that any application server can validate and retrieve session data without sticky routing.
- **Rate** limiting uses `INCR` with a TTL-bound key to count requests per client and reject traffic that exceeds the threshold.
- **Leaderboard** implementations rely on sorted sets where the score represents points and `ZREVRANGE` returns the top-ranked members instantly.
- **Distributed** locking with the Redlock algorithm coordinates access to shared resources across multiple services.
- **Full-page** caching stores rendered HTML in a string key with a short TTL, offloading expensive template rendering from application servers.

## Redis vs Memcached

| Feature               | Redis                                  | Memcached                          |
|-----------------------|----------------------------------------|------------------------------------|
| Data structures       | Strings, lists, sets, hashes, streams  | Strings only                       |
| Persistence           | RDB snapshots, AOF log                 | None (pure cache)                  |
| Replication           | Built-in primary-replica               | Not built-in                       |
| Clustering            | Redis Cluster (hash slots)             | Client-side consistent hashing     |
| Pub/Sub               | Native support                         | Not supported                      |
| Scripting             | Lua scripting on the server            | Not supported                      |
| Threading model       | Single-threaded event loop             | Multi-threaded                     |
| Max value size        | 512 MB                                 | 1 MB (default)                     |
| Memory efficiency     | Moderate (structural overhead)         | High (slab allocator)              |
| Use case              | Cache, message broker, data store      | Simple high-throughput caching     |

## Redis Clients

To interact with Redis from your backend code, you need a Redis client library. Popular options include:

- **ioredis**: A robust, high-performance Redis client for Node.js with built-in cluster and sentinel support.
- **StackExchange.Redis**: A .NET library used heavily in the Microsoft ecosystem with connection multiplexing.
- **Jedis**: A lightweight, synchronous Java client suitable for simple use cases and thread-per-connection models.
- **Lettuce**: An asynchronous, non-blocking Java client built on Netty that works well with reactive frameworks.
- **redis-py**: The standard Python client, offering both synchronous and async interfaces via `redis.asyncio`.
- **go-redis**: A type-safe Go client supporting Redis Cluster, Sentinel, and pipelining out of the box.

Choose a client library that best fits your programming language, concurrency model, and deployment requirements.

## Monitoring and Maintenance

- The `INFO` command returns detailed **statistics** about memory usage, connected clients, keyspace hits and misses, and replication status.
- Running `SLOWLOG GET` surfaces commands that exceeded the configured **threshold**, helping you find and optimize expensive operations.
- Redis Sentinel monitors primary and replica nodes and performs automatic **failover** when a primary becomes unreachable.
- External tools like RedisInsight, Prometheus with the Redis exporter, and Grafana dashboards provide visual **observability** into cluster health and performance trends.
- Schedule regular `BGSAVE` or `BGREWRITEAOF` operations during off-peak hours to reduce the **impact** of persistence I/O on live traffic.

## Security Considerations

- Protect your instance with the `requirepass` directive and use **ACLs** (introduced in Redis 6) to grant fine-grained per-user permissions.
- Bind Redis to a private network interface and restrict **access** to trusted IP addresses using firewall rules.
- Enable **TLS** encryption for client-server and replica-to-primary connections to prevent eavesdropping on sensitive data.
- Disable dangerous commands like `FLUSHALL` and `CONFIG` in production by renaming them in the **configuration** file.
- Never expose a Redis port directly to the public internet; instead route traffic through a **VPN** or an SSH tunnel.
