## Redis

Redis is a high-performance, in-memory data store commonly used as a cache, message broker, session store, rate limiter, leaderboard engine, and fast key-value database. It is often described as a **data structure server** because it supports rich built-in data types such as strings, lists, sets, sorted sets, hashes, streams, and more.

Redis is extremely fast because most operations happen in memory. This makes it useful when an application needs very low-latency reads and writes. In typical backend architectures, Redis often sits between the application and slower systems such as relational databases, external APIs, or disk-based storage.

One wording note: Redis used to be commonly described as open source under BSD licensing. Redis changed its licensing model in 2024, and Redis 8 later added AGPLv3 as an OSI-approved open-source option alongside Redis’s other licenses. Valkey was also created in 2024 as a Linux Foundation-backed BSD-licensed fork of Redis 7.2.4. So in modern notes, it is safest to describe Redis as a widely used in-memory data store, and mention licensing separately if needed. ([Redis][1])

```text
  +-----------+        +-----------+        +-----------+
  | Client A  |        | Client B  |        | Client C  |
  | Web App   |        | Worker    |        | CLI       |
  +-----+-----+        +-----+-----+        +-----+-----+
        |                     |                     |
        | SET/GET             | LPUSH/BRPOP         | PUBLISH
        |                     |                     |
        +----------+----------+----------+----------+
                   |                     |
                   v                     v
        +-------------------------------------------+
        |            Redis Server                   |
        |-------------------------------------------|
        |  Engine: Event-loop based command handling |
        |  Storage: In-memory key-value store        |
        |  Features:                                |
        |   - Strings, Lists, Sets, Hashes           |
        |   - Sorted Sets and Streams                |
        |   - Pub/Sub messaging                      |
        |   - Lua scripting                          |
        |   - Transactions with MULTI/EXEC           |
        |   - TTL-based key expiration               |
        +---------------------+---------------------+
                              |
                   Optional persistence
                              |
              +---------------+---------------+
              |                               |
              v                               v
        +-----------+                   +-----------+
        | RDB Dump  |                   | AOF Log   |
        | Snapshot  |                   | Append    |
        +-----------+                   +-----------+
```

### Concepts

Redis is best understood as a fast in-memory key-value system with specialized data structures and optional durability. It is not just a cache, although caching is one of its most common uses.

#### In-Memory Data Store

Redis stores data primarily in RAM. This avoids disk seek latency and allows very fast reads and writes. For many simple operations, Redis can serve responses in sub-millisecond time under the right conditions.

Example command:

```bash
SET user:1001:name "Alice"
GET user:1001:name
```

Example output:

```text
"Alice"
```

Because Redis is memory-based, memory sizing matters. If the dataset grows beyond available RAM, Redis may reject writes or evict keys depending on configuration.

Example memory policy:

```text
maxmemory 4gb
maxmemory-policy allkeys-lru
```

Example meaning:

```json
{
  "maxMemory": "4gb",
  "evictionPolicy": "allkeys-lru",
  "behavior": "evict least recently used keys when memory is full"
}
```

Redis uses efficient event-driven networking and processes commands in a way that avoids much of the locking complexity found in heavily threaded systems. Newer Redis versions also include improvements around I/O threading and modules, but the core mental model remains: keep hot data in memory and make operations fast.

#### Key-Value Store

Every Redis value is accessed through a key. The key is a binary-safe string, meaning it can represent many kinds of identifiers. In practice, teams usually use readable key naming conventions.

Example keys:

```text
user:1001:profile
product:8842:details
session:abc123
rate_limit:ip:203.0.113.10
leaderboard:weekly
```

Good key naming is important because Redis does not impose a schema like a relational database. The application is responsible for naming, grouping, and expiring keys consistently.

Example profile value:

```json
{
  "id": 1001,
  "name": "Alice",
  "plan": "premium"
}
```

Example Redis string command:

```bash
SET user:1001:profile '{"id":1001,"name":"Alice","plan":"premium"}'
GET user:1001:profile
```

Key design should include enough information to avoid collisions and make debugging easier. For multi-tenant systems, include the tenant ID or organization ID when necessary.

Example tenant-aware key:

```text
tenant:42:user:1001:profile
```

#### Data Expiration

Redis allows keys to expire automatically using TTLs, or time-to-live values. This is one reason Redis is popular for sessions, temporary tokens, rate limits, and cached database results.

Example:

```bash
SET session:abc123 '{"user_id":1001}' EX 3600
TTL session:abc123
```

Example output:

```text
(integer) 3597
```

This means the session key will expire after about one hour.

Expiration is handled through lazy deletion and active cleanup. Lazy deletion means Redis checks whether a key is expired when it is accessed. Active cleanup means Redis also periodically samples and removes expired keys.

Example use cases:

```json
{
  "session:abc123": "expires after 1 hour",
  "password_reset:user:1001": "expires after 15 minutes",
  "cache:product:8842": "expires after 5 minutes"
}
```

TTL design should reflect business correctness. A product description may tolerate a longer TTL, while a password reset token needs a short TTL.

### Redis Data Structures

Redis supports several first-class data structures. Choosing the right structure is important because each one is optimized for different access patterns.

```text
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

#### Strings

A Redis string is the simplest data type. It can store text, numbers, JSON, serialized objects, or binary data.

Example:

```bash
SET page:view_count 100
INCR page:view_count
GET page:view_count
```

Example output:

```text
"101"
```

Strings are useful for simple cache entries, counters, feature flags, JSON blobs, tokens, and rate limiter counters.

Example cached database result:

```bash
SET product:8842:details '{"id":8842,"name":"Laptop Stand","price":29.99}' EX 300
```

Example value:

```json
{
  "id": 8842,
  "name": "Laptop Stand",
  "price": 29.99
}
```

Commands such as `MGET` and `MSET` reduce network overhead by reading or writing multiple keys in one round trip.

```bash
MGET product:1:details product:2:details product:3:details
```

#### Lists

A Redis list is an ordered collection of strings. Lists support fast pushes and pops from both ends.

Example queue:

```bash
LPUSH email_queue '{"to":"alice@example.com","template":"welcome"}'
BRPOP email_queue 0
```

Example output:

```text
1) "email_queue"
2) "{\"to\":\"alice@example.com\",\"template\":\"welcome\"}"
```

Lists are useful for simple queues, task pipelines, recent activity feeds, and ordered buffers.

Blocking commands such as `BRPOP` allow workers to wait for jobs without repeatedly polling Redis.

Example worker behavior:

```json
{
  "worker": "email-worker-1",
  "command": "BRPOP email_queue 0",
  "status": "waiting_for_job"
}
```

For more reliable queues with acknowledgments and consumer groups, Redis Streams are usually a better fit than lists.

#### Sets

A Redis set stores unique unordered strings. Sets are useful when uniqueness matters and ordering does not.

Example:

```bash
SADD article:55:viewers user:1 user:2 user:1
SCARD article:55:viewers
```

Example output:

```text
(integer) 2
```

Even though `user:1` was added twice, it is stored once.

Sets support useful operations such as intersections, unions, and differences.

Example:

```bash
SINTER users:premium users:active
```

Example use:

```json
{
  "question": "Which users are both premium and active?",
  "operation": "SINTER users:premium users:active"
}
```

Sets are commonly used for unique visitors, tags, permissions, group membership, feature rollout cohorts, and relationship graphs.

#### Sorted Sets

A Redis sorted set stores unique members with numeric scores. Redis keeps the members ordered by score.

Example leaderboard:

```bash
ZADD leaderboard:weekly 1200 alice
ZADD leaderboard:weekly 950 bob
ZADD leaderboard:weekly 1500 carol

ZREVRANGE leaderboard:weekly 0 2 WITHSCORES
```

Example output:

```text
1) "carol"
2) "1500"
3) "alice"
4) "1200"
5) "bob"
6) "950"
```

Sorted sets are useful for leaderboards, rankings, priority queues, scheduled jobs, time-windowed indexes, and feeds ordered by timestamp or score.

Example priority queue:

```bash
ZADD jobs:scheduled 1714050000 job:123
ZRANGEBYSCORE jobs:scheduled -inf 1714050000
```

This retrieves jobs whose scheduled timestamp is due.

Sorted sets are powerful because they combine uniqueness, ordering, and range queries.

#### Hashes

A Redis hash stores field-value pairs inside one Redis key. It is commonly used to represent objects.

Example user profile:

```bash
HSET user:1001 name "Alice" plan "premium" region "EU"
HGET user:1001 plan
```

Example output:

```text
"premium"
```

Hashes are useful when an object has several fields and you want to read or update individual fields without rewriting the whole object.

Example:

```bash
HSET product:8842 price "34.99"
HGETALL product:8842
```

Example output:

```json
{
  "name": "Laptop Stand",
  "price": "34.99",
  "stock": "42"
}
```

Hashes can be more memory-efficient than storing many tiny string keys, but they are still stored within Redis memory and should be sized carefully.

#### Streams

Redis Streams are append-only log-like data structures introduced for durable event-style messaging. They support message IDs, consumer groups, acknowledgments, and replay.

Example:

```bash
XADD orders:events * order_id 123 status created amount 79.99
```

Example output:

```text
"1714050000000-0"
```

Consumer group example:

```bash
XGROUP CREATE orders:events billing-group $ MKSTREAM
XREADGROUP GROUP billing-group worker-1 COUNT 10 STREAMS orders:events >
```

Example use:

```json
{
  "stream": "orders:events",
  "consumerGroup": "billing-group",
  "worker": "worker-1",
  "purpose": "process order events reliably"
}
```

Streams are better than Pub/Sub when messages must survive consumer disconnections or when multiple workers need coordinated consumption.

### Redis Persistence

Redis is primarily in-memory, but it provides persistence options so data can survive restarts or crashes. The two main mechanisms are **RDB snapshots** and **AOF logs**.

```text
                       Redis Server
                    +----------------+
                    |   In-Memory    |
                    |   Dataset      |
                    +-------+--------+
                            |
           +----------------+----------------+
           |                                 |
     Point-in-time                     Every write
       snapshot                         appended
           |                                 |
           v                                 v
   +---------------+                +----------------+
   |   RDB File    |                |   AOF File     |
   | binary dump   |                | command log    |
   +---------------+                +----------------+
```

#### RDB Snapshots

RDB persistence writes a point-in-time snapshot of the Redis dataset to disk. The snapshot is compact and usually fast to load.

Example configuration:

```text
save 900 1
save 300 10
save 60 10000
```

Meaning:

```json
{
  "saveAfter900SecondsIfAtLeast": "1 key changed",
  "saveAfter300SecondsIfAtLeast": "10 keys changed",
  "saveAfter60SecondsIfAtLeast": "10000 keys changed"
}
```

RDB is good for backups and fast restarts, but writes made after the latest snapshot may be lost if Redis crashes before the next snapshot.

Example risk:

```json
{
  "lastSnapshot": "12:00:00",
  "crashTime": "12:04:30",
  "possibleDataLoss": "writes after 12:00:00"
}
```

#### AOF Append-Only File

AOF persistence logs write commands to disk. On restart, Redis replays the log to rebuild the dataset.

Example configuration:

```text
appendonly yes
appendfsync everysec
```

Common `appendfsync` choices:

```json
{
  "always": "fsync every write, safest but slowest",
  "everysec": "fsync about once per second, common balance",
  "no": "let OS decide, fastest but less durable"
}
```

AOF gives stronger durability than periodic snapshots. With `appendfsync everysec`, Redis may lose up to about one second of writes in a crash.

Over time, AOF files can grow. Redis can rewrite them using `BGREWRITEAOF`.

```bash
BGREWRITEAOF
```

This compacts the log by writing the minimal commands needed to reconstruct the current state.

#### Combining RDB and AOF

Redis can use both RDB and AOF. RDB provides compact snapshots that are useful for backups, while AOF provides more complete recent write history.

Example setup:

```json
{
  "rdb": "enabled for backups",
  "aof": "enabled for durability",
  "startupPreference": "AOF usually preferred when present"
}
```

For pure caching, persistence may not be necessary. For session storage, queues, or Redis-as-primary-database use cases, persistence becomes more important.

### Redis Replication and Clustering

Redis can scale and improve availability through replication, Sentinel, and Redis Cluster.

#### Replication

Redis replication uses a primary-replica model. The primary accepts writes and streams changes asynchronously to replicas. Replicas can serve reads if the application can tolerate replication lag.

```text
                  +-----------------+
                  |    Primary      |
                  | Read + Write    |
                  +--------+--------+
                           |
            +--------------+--------------+
            | async replication           | async replication
            v                             v
   +-----------------+           +-----------------+
   |   Replica 1     |           |   Replica 2     |
   |   Read Only     |           |   Read Only     |
   +-----------------+           +-----------------+
```

Example status:

```json
{
  "primary": "redis-1",
  "replicas": ["redis-2", "redis-3"],
  "replication": "asynchronous"
}
```

Because replication is asynchronous, a primary can acknowledge a write before replicas have received it. If the primary fails immediately afterward, a recently acknowledged write may be lost.

Example risk:

```json
{
  "writeAcknowledgedByPrimary": true,
  "replicaReceivedWrite": false,
  "primaryFailed": true,
  "possibleDataLoss": true
}
```

This is important when using Redis for more than disposable cache data.

#### Sentinel

Redis Sentinel monitors primary and replica nodes and can perform automatic failover. If the primary becomes unavailable, Sentinel can promote a replica.

Example:

```text
Primary fails.
Sentinel detects failure.
Sentinel promotes Replica 1.
Clients reconnect to new primary.
```

Example failover output:

```json
{
  "oldPrimary": "redis-1",
  "newPrimary": "redis-2",
  "failover": "completed"
}
```

Sentinel is useful for high availability when Redis is deployed as a primary-replica setup without sharding.

#### Redis Cluster

Redis Cluster shards data across multiple primary nodes. It divides the keyspace into 16,384 hash slots. Each key maps to one slot, and each primary owns a subset of slots.

```text
  +-------------------+    +-------------------+    +-------------------+
  | Node A Primary    |    | Node B Primary    |    | Node C Primary    |
  | Slots 0-5460      |    | Slots 5461-10922  |    | Slots 10923-16383 |
  +---------+---------+    +---------+---------+    +---------+---------+
            |                        |                        |
            v                        v                        v
  +-------------------+    +-------------------+    +-------------------+
  | Node A' Replica   |    | Node B' Replica   |    | Node C' Replica   |
  +-------------------+    +-------------------+    +-------------------+
```

Example slot ownership:

```json
{
  "slots_0_5460": "node-a",
  "slots_5461_10922": "node-b",
  "slots_10923_16383": "node-c"
}
```

If a client sends a command to the wrong node, Redis Cluster may respond with `MOVED` or `ASK`. Cluster-aware clients handle these redirects automatically.

Example redirect:

```text
MOVED 3999 10.0.0.2:6379
```

Redis Cluster is useful when a single Redis primary cannot hold all data or handle all throughput.

#### Hash Tags in Redis Cluster

In Redis Cluster, multi-key operations work only when all keys are in the same hash slot. Hash tags allow related keys to be placed in the same slot by wrapping part of the key in `{}`.

Example:

```text
user:{1001}:profile
user:{1001}:settings
user:{1001}:sessions
```

All three keys hash using `1001`, so they land in the same slot.

Example:

```json
{
  "keys": [
    "user:{1001}:profile",
    "user:{1001}:settings"
  ],
  "sameSlot": true,
  "multiKeyOperationAllowed": true
}
```

Hash tags are important for transactions, Lua scripts, or multi-key commands in Redis Cluster.

### Pub/Sub Capabilities

Redis Pub/Sub lets publishers send messages to channels, and subscribers receive messages in real time.

```text
  +-----------+           +------------------+          +--------------+
  | Publisher | PUBLISH   |  Redis Channel   | message  | Subscriber A |
  | Service   +---------->| "notifications"  +--------->| WebSocket    |
  +-----------+           +--------+---------+          +--------------+
                                   |
                                   | message
                                   v
                          +--------------+
                          | Subscriber B |
                          | Worker       |
                          +--------------+
```

Example publisher:

```bash
PUBLISH notifications '{"user_id":1001,"message":"Order shipped"}'
```

Example subscriber:

```bash
SUBSCRIBE notifications
```

Example received message:

```json
{
  "user_id": 1001,
  "message": "Order shipped"
}
```

Pub/Sub is fast and simple, but it is not durable. If a subscriber is offline when a message is published, that subscriber misses the message.

Example limitation:

```json
{
  "subscriberOnline": false,
  "messagePublished": true,
  "messageDeliveredLater": false
}
```

For durable messaging, use Redis Streams instead of Pub/Sub.

### Using Redis as a Database Cache

Redis is commonly used to cache database query results, rows, aggregates, and computed objects. The goal is to reduce load on the primary database and improve response times.

#### Cache-Aside

Cache-aside is the most common Redis caching pattern. The application checks Redis first. If the value is missing, it queries the database, stores the result in Redis, and returns it.

Example:

```python
def get_product(product_id):
    key = f"product:{product_id}:details"

    cached = redis.get(key)
    if cached:
        return json.loads(cached)

    product = db.query_one(
        "SELECT id, name, price FROM products WHERE id = %s",
        [product_id]
    )

    redis.set(key, json.dumps(product), ex=300)
    return product
```

Example first request:

```json
{
  "cache": "MISS",
  "databaseQueried": true,
  "latencyMs": 80
}
```

Example second request:

```json
{
  "cache": "HIT",
  "databaseQueried": false,
  "latencyMs": 3
}
```

Cache-aside is flexible because only requested data enters the cache.

#### Write-Through

Write-through updates Redis whenever the database is updated. This keeps the cache warm and fresh.

Example:

```sql
UPDATE products
SET price = 34.99
WHERE id = 8842;
```

Then:

```bash
SET product:8842:details '{"id":8842,"name":"Laptop Stand","price":34.99}' EX 300
```

Example result:

```json
{
  "databaseUpdated": true,
  "redisUpdated": true,
  "cacheFresh": true
}
```

Write-through improves read freshness but makes writes more complex.

#### Cache Invalidation

Cache invalidation removes stale Redis keys when the underlying database changes.

Example update:

```sql
UPDATE products
SET price = 34.99
WHERE id = 8842;
```

Example invalidation:

```bash
DEL product:8842:details
DEL product:category:7:popular
```

Example output:

```json
{
  "updatedRow": "products.id=8842",
  "invalidatedKeys": [
    "product:8842:details",
    "product:category:7:popular"
  ]
}
```

Invalidation is difficult because one database row may affect many cached query results.

#### Cache Key Design

Good cache keys are predictable, specific, and versioned when the shape of cached data changes.

Example:

```text
v1:product:8842:details
v1:product:category:7:sort:popular:limit:20
v1:user:1001:permissions
```

If the cached JSON format changes, increment the version:

```text
v2:product:8842:details
```

Example benefit:

```json
{
  "oldKey": "v1:product:8842:details",
  "newKey": "v2:product:8842:details",
  "benefit": "avoid deserializing old format as new schema"
}
```

### Common Usage Patterns

Redis is useful for many backend patterns beyond simple database caching.

#### Session Storage

Redis can store user sessions so any application server can validate a session without sticky routing.

Example:

```bash
SET session:abc123 '{"user_id":1001,"role":"admin"}' EX 3600
```

Example lookup:

```json
{
  "sessionId": "abc123",
  "userId": 1001,
  "role": "admin"
}
```

This is useful when multiple stateless web servers sit behind a load balancer.

#### Rate Limiting

Redis can implement counters with TTLs for rate limiting.

Example:

```bash
INCR rate_limit:ip:203.0.113.10
EXPIRE rate_limit:ip:203.0.113.10 60
```

Example decision:

```json
{
  "ip": "203.0.113.10",
  "requestsThisMinute": 82,
  "limit": 100,
  "allowed": true
}
```

For production rate limiters, use atomic Lua scripts or Redis functions to avoid race conditions between `INCR` and `EXPIRE`.

#### Leaderboards

Sorted sets are ideal for leaderboards.

Example:

```bash
ZADD game:leaderboard 2500 alice
ZADD game:leaderboard 1800 bob
ZADD game:leaderboard 3100 carol

ZREVRANGE game:leaderboard 0 2 WITHSCORES
```

Example output:

```text
carol 3100
alice 2500
bob 1800
```

The score controls ranking, and Redis can return top players efficiently.

#### Distributed Locking

Redis is sometimes used for distributed locks. A basic lock uses `SET key value NX PX`.

Example:

```bash
SET lock:daily-report worker-1 NX PX 30000
```

Meaning:

```json
{
  "lock": "daily-report",
  "owner": "worker-1",
  "ttlMs": 30000,
  "onlySetIfNotExists": true
}
```

Locks must be used carefully. The lock value should be unique, and release should check ownership before deleting. For critical correctness, consider whether a consensus system such as etcd, ZooKeeper, or a database transaction is more appropriate.

#### Full-Page or Fragment Caching

Redis can store rendered HTML or page fragments.

Example:

```bash
SET page:/products/8842 "<html>...</html>" EX 60
```

Example result:

```json
{
  "page": "/products/8842",
  "servedFromRedis": true,
  "databaseQueried": false,
  "templateRendered": false
}
```

This is useful for read-heavy pages that are expensive to render.

### Redis vs Memcached

Redis and Memcached are both used for caching, but Redis offers more data structures and features.

| Feature                | Redis                                              | Memcached                    |
| ---------------------- | -------------------------------------------------- | ---------------------------- |
| Data structures        | Strings, lists, sets, hashes, sorted sets, streams | Strings / blobs              |
| Persistence            | RDB snapshots, AOF log                             | None by default              |
| Replication            | Built-in primary-replica                           | Not built-in in the same way |
| Clustering             | Redis Cluster hash slots                           | Usually client-side hashing  |
| Pub/Sub                | Supported                                          | Not supported                |
| Streams                | Supported                                          | Not supported                |
| Scripting              | Lua / server-side execution                        | Not supported                |
| Typical model          | Cache, broker, data structure store                | Simple high-throughput cache |
| Operational complexity | Higher                                             | Lower                        |
| Best fit               | Rich data structures and advanced patterns         | Simple key-value caching     |

Example choice:

```json
{
  "useRedisWhen": [
    "you need sorted sets",
    "you need counters and TTLs",
    "you need streams or pub/sub",
    "you need persistence"
  ],
  "useMemcachedWhen": [
    "you need a simple disposable cache",
    "you only store blobs or strings",
    "you want minimal operational complexity"
  ]
}
```

### Redis Clients

Backend applications usually talk to Redis through a language-specific client library.

Common clients include:

* **ioredis** for Node.js.
* **node-redis** for Node.js.
* **StackExchange.Redis** for .NET.
* **Jedis** for Java.
* **Lettuce** for Java and reactive frameworks.
* **redis-py** for Python.
* **go-redis** for Go.

Choose a client that supports your deployment mode. If you use Redis Cluster, the client should understand cluster redirects. If you use Sentinel, the client should support Sentinel discovery and failover.

Example client requirements:

```json
{
  "deployment": "Redis Cluster",
  "clientMustSupport": [
    "cluster slot discovery",
    "MOVED redirects",
    "ASK redirects",
    "connection pooling"
  ]
}
```

### Monitoring and Maintenance

Redis should be monitored carefully because it often sits on a critical request path.

Useful commands:

```bash
INFO
SLOWLOG GET
MEMORY STATS
CLIENT LIST
```

Example `INFO` metrics to watch:

```json
{
  "used_memory": "memory currently used",
  "connected_clients": "active client connections",
  "keyspace_hits": "cache hits",
  "keyspace_misses": "cache misses",
  "evicted_keys": "keys removed due to memory pressure",
  "expired_keys": "keys removed due to TTL",
  "instantaneous_ops_per_sec": "current command rate"
}
```

Important metrics include:

* Memory usage.
* Evictions.
* Hit ratio.
* Command latency.
* Slowlog entries.
* Replication lag.
* Connected clients.
* CPU usage.
* Persistence rewrite duration.
* Cluster slot health.

Example monitoring output:

```json
{
  "cacheHitRatio": "91%",
  "usedMemory": "3.2GB",
  "maxMemory": "4GB",
  "evictedKeysLastHour": 1200,
  "replicationLagMs": 18,
  "status": "healthy"
}
```

Persistence tasks such as `BGSAVE` and `BGREWRITEAOF` should be monitored because they can increase disk and CPU load.

### Security Considerations

Redis should never be exposed directly to the public internet. It should run on a private network and accept connections only from trusted applications.

Important security controls include:

* Use authentication.
* Use ACLs for fine-grained permissions.
* Bind Redis to private interfaces.
* Restrict access with firewall rules or security groups.
* Enable TLS where sensitive data crosses networks.
* Disable or rename dangerous commands when appropriate.
* Avoid storing highly sensitive data unless encrypted or strictly controlled.
* Monitor access and command usage.

Example ACL:

```bash
ACL SETUSER appuser on >strong-password ~app:* +get +set +del +expire
```

Example meaning:

```json
{
  "user": "appuser",
  "keyPattern": "app:*",
  "allowedCommands": ["GET", "SET", "DEL", "EXPIRE"]
}
```

Example dangerous exposure:

```json
{
  "redisPort": 6379,
  "publicInternetAccessible": true,
  "risk": "critical"
}
```

Redis is powerful and fast, but because it often contains sessions, tokens, cached private data, or operational state, access must be tightly controlled.

