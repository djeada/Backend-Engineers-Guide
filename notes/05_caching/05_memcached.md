## Memcached

Memcached is a high-performance, distributed, in-memory key-value cache. It is designed for one main purpose: storing small pieces of frequently accessed data in RAM so applications can avoid repeatedly querying slower systems such as relational databases, APIs, or disk-backed storage.

Unlike Redis, Memcached is intentionally simple. It stores keys and values, supports expiration, distributes data across multiple cache nodes through client-side hashing, and focuses on very fast cache reads and writes. It does not provide rich data structures, persistence, streams, Pub/Sub, or built-in replication in the same way Redis does.

Memcached is best understood as a **temporary, disposable cache**. If a Memcached node restarts or evicts data, the application should be able to rebuild missing values from the source of truth, usually a database.

```text id="45ksv5"
  +-----------+        +-----------+        +-----------+
  | Client A  |        | Client B  |        | Client C  |
  | Web App   |        | Worker    |        | API       |
  +-----+-----+        +-----+-----+        +-----+-----+
        |                     |                     |
        | get/set             | get/set             | get/delete
        |                     |                     |
        +----------+----------+----------+----------+
                   |
                   v
        +-------------------------------------------+
        |              Memcached Layer              |
        |-------------------------------------------|
        |  Storage: In-memory key-value cache        |
        |  Model: Simple strings / binary values     |
        |  Expiration: TTL-based item expiry         |
        |  Distribution: Client-side hashing         |
        |  Persistence: None                         |
        |  Best use: Disposable database cache        |
        +---------------------+---------------------+
                              |
                              | cache miss
                              v
                    +-------------------+
                    | Primary Database  |
                    | Source of Truth   |
                    +-------------------+
```

### Concepts

Memcached is deliberately minimal. Its simplicity is one of its main strengths. It works well when the application needs a fast, shared, distributed cache and does not need advanced Redis-style features.

#### In-Memory Cache

Memcached stores data in RAM. This makes it much faster than reading from disk or repeatedly executing database queries.

Example database query:

```sql id="5dbl1h"
SELECT id, name, price
FROM products
WHERE id = 8842;
```

Example cached value in Memcached:

```json id="u765d5"
{
  "id": 8842,
  "name": "Laptop Stand",
  "price": 29.99
}
```

Example cache behavior:

```json id="oo1zmn"
{
  "cache": "HIT",
  "databaseQueried": false,
  "latencyMs": 2
}
```

If the key is missing, the application queries the database and stores the result in Memcached for future requests.

```json id="v9epjp"
{
  "cache": "MISS",
  "databaseQueried": true,
  "latencyMs": 75
}
```

Memcached should not be treated as durable storage. It can lose data when a node restarts, when memory fills up, or when items expire.

#### Simple Key-Value Model

Memcached stores data by key. Each key maps to a value, which is usually a string, serialized object, JSON blob, or binary payload.

Example keys:

```text id="irbbex"
product:8842:details
user:1001:profile
dashboard:orders:last_30_days
category:7:popular_products
```

Example command style:

```text id="ahih4v"
set product:8842:details 0 300 52
{"id":8842,"name":"Laptop Stand","price":29.99}
```

Example retrieval:

```text id="tjsw3x"
get product:8842:details
```

Example output:

```text id="a29vb9"
VALUE product:8842:details 0 52
{"id":8842,"name":"Laptop Stand","price":29.99}
END
```

The application is responsible for serialization and deserialization. Memcached does not understand the structure of your value.

Example application interpretation:

```json id="seyea1"
{
  "key": "product:8842:details",
  "serializedFormat": "JSON",
  "applicationParsesValue": true
}
```

#### TTL and Expiration

Memcached supports expiration times. When setting a key, the application can provide a TTL. After the TTL expires, the item is no longer returned.

Example:

```text id="sjxi2r"
set product:8842:details 0 300 52
{"id":8842,"name":"Laptop Stand","price":29.99}
```

This stores the product details for 300 seconds.

Example TTL design:

```json id="mln9qa"
{
  "productDetails": "5 minutes",
  "categoryLists": "2 minutes",
  "dashboardAggregates": "15 minutes",
  "referenceData": "1 hour"
}
```

Memcached can also evict items before their TTL expires if memory is full. This is why cached data must always be rebuildable from the database or another source of truth.

#### Client-Side Distribution

Memcached does not have built-in clustering in the same way Redis Cluster does. In most deployments, the client library distributes keys across multiple Memcached servers using hashing.

Example:

```text id="w4yr23"
hash(product:8842:details) -> memcached-node-2
hash(user:1001:profile)    -> memcached-node-1
hash(category:7:popular)   -> memcached-node-3
```

Diagram:

```text id="j1k1sp"
        +-------------+
        | Application |
        +------+------+
               |
       client-side hashing
               |
   +-----------+-----------+
   |           |           |
   v           v           v
+------+    +------+    +------+
| MC 1 |    | MC 2 |    | MC 3 |
+------+    +------+    +------+
```

Example routing output:

```json id="6c882m"
{
  "key": "product:8842:details",
  "selectedNode": "memcached-node-2",
  "method": "client-side hashing"
}
```

Many clients use consistent hashing so that adding or removing a Memcached node remaps only a portion of keys rather than the entire keyspace.

#### Memcached Data Model

Memcached has a much simpler data model than Redis. It stores opaque values. The server does not provide lists, sets, sorted sets, hashes, streams, or server-side querying.

#### Strings and Serialized Objects

Most Memcached values are strings or serialized objects.

Example JSON value:

```json id="25wvov"
{
  "id": 1001,
  "name": "Alice",
  "plan": "premium"
}
```

Stored under:

```text id="rmupp1"
user:1001:profile
```

Example application pseudo-code:

```python id="xc28mj"
profile = memcached.get("user:1001:profile")

if profile is None:
    profile = db.query_one(
        "SELECT id, name, plan FROM users WHERE id = %s",
        [1001]
    )
    memcached.set("user:1001:profile", json.dumps(profile), expire=300)

return json.loads(profile)
```

Example first request:

```json id="f9adxh"
{
  "cacheStatus": "MISS",
  "databaseQueried": true,
  "storedInMemcached": true
}
```

Example second request:

```json id="v751nk"
{
  "cacheStatus": "HIT",
  "databaseQueried": false
}
```

#### Numeric Counters

Memcached supports atomic increment and decrement operations for numeric values. This is useful for counters, lightweight rate limiting, and temporary metrics.

Example:

```text id="q4s5q0"
set page:123:views 0 3600 1
0

incr page:123:views 1
```

Example output:

```text id="j72ws6"
1
```

Example use:

```json id="453dbw"
{
  "key": "rate_limit:ip:203.0.113.10",
  "count": 42,
  "windowSeconds": 60
}
```

Counters in Memcached are temporary. They are not durable and should not be used as the only source of truth for important business data.

#### CAS: Compare-And-Swap

Memcached supports CAS, or compare-and-swap, for optimistic concurrency. CAS lets a client update a value only if it has not changed since the client last read it.

Example flow:

```text id="azd70q"
1. Client reads key with gets.
2. Memcached returns value plus CAS token.
3. Client modifies value.
4. Client writes using cas token.
5. Write succeeds only if token still matches.
```

Example:

```text id="mf6ryb"
gets user:1001:profile
VALUE user:1001:profile 0 38 927364
{"id":1001,"name":"Alice","visits":3}
END
```

The last number is the CAS token.

Example CAS update:

```text id="lpb46m"
cas user:1001:profile 0 300 38 927364
{"id":1001,"name":"Alice","visits":4}
```

Example successful output:

```text id="5a1hwf"
STORED
```

Example failed output:

```text id="0q2769"
EXISTS
```

`EXISTS` means another client updated the value first. The application should reread and retry if appropriate.

### Memory Management

Memcached is designed around fixed memory allocation. When you start Memcached, you assign a memory limit. Memcached uses that memory for cached items and evicts old items when needed.

#### Slab Allocator

Memcached uses a slab allocator. It divides memory into slab classes for different item sizes. This reduces fragmentation and makes memory allocation fast.

Conceptual layout:

```text id="425fje"
Memcached Memory

+--------------------+
| Slab Class 1       | small items
+--------------------+
| Slab Class 2       | medium items
+--------------------+
| Slab Class 3       | larger items
+--------------------+
```

Example:

```json id="0tdlv5"
{
  "smallItems": "user session IDs",
  "mediumItems": "profile JSON",
  "largeItems": "dashboard result blobs"
}
```

This is one reason Memcached is efficient for simple caching workloads.

#### Eviction

When memory is full, Memcached evicts items. Its traditional eviction policy is based on least recently used behavior within slab classes.

Example eviction:

```json id="3n0tu4"
{
  "evictedKey": "product:old:details",
  "reason": "memory pressure",
  "slabClass": "medium"
}
```

Eviction does not mean an error occurred. It is normal behavior for a cache. The application should treat evicted keys as cache misses and reload from the database.

Example:

```json id="55qey8"
{
  "cacheMissReason": "evicted",
  "fallback": "query database and repopulate cache"
}
```

If evictions are very frequent, the cache may be undersized or storing data that is not useful enough.

#### Value Size

Memcached is optimized for relatively small values. The default maximum item size is commonly 1 MB, though it can be configured.

Example poor fit:

```json id="plk7re"
{
  "key": "report:huge_export",
  "valueSize": "20MB",
  "problem": "too large for typical Memcached usage"
}
```

Better approach:

```json id="48mf4y"
{
  "largeReportStoredIn": "object storage or database",
  "memcachedStores": "small metadata or precomputed summary"
}
```

Memcached works best when caching compact values that are frequently reused.

### Using Memcached as a Database Cache

Memcached is most often used to cache database query results. This is its strongest and most common use case.

#### Cache-Aside Pattern

The cache-aside pattern is the standard Memcached pattern. The application controls the cache.

Flow:

```text id="eykuk1"
1. Application needs product details.
2. Check Memcached.
3. If hit, return cached value.
4. If miss, query database.
5. Store result in Memcached.
6. Return result.
```

Example pseudo-code:

```python id="pdnw1p"
def get_product(product_id):
    key = f"product:{product_id}:details"

    cached = memcached.get(key)
    if cached is not None:
        return json.loads(cached)

    product = db.query_one(
        """
        SELECT id, name, price, stock_count
        FROM products
        WHERE id = %s
        """,
        [product_id]
    )

    memcached.set(key, json.dumps(product), expire=300)
    return product
```

Example cache miss:

```json id="b8p73s"
{
  "key": "product:8842:details",
  "cacheStatus": "MISS",
  "databaseQuery": "executed",
  "memcachedSet": true
}
```

Example cache hit:

```json id="fgagov"
{
  "key": "product:8842:details",
  "cacheStatus": "HIT",
  "databaseQuery": "skipped"
}
```

This reduces repeated database reads for popular records.

#### Caching Single-Row Queries

Single-row primary-key lookups are excellent candidates for Memcached.

Example SQL:

```sql id="iegm5h"
SELECT id, username, display_name
FROM users
WHERE id = 1001;
```

Cache key:

```text id="1x5vmm"
user:1001:profile
```

Cached value:

```json id="53qku7"
{
  "id": 1001,
  "username": "alice",
  "display_name": "Alice"
}
```

This avoids repeating the same database query whenever the user appears in comments, posts, messages, or profile pages.

#### Caching Expensive List Queries

Memcached can store results of expensive list queries, as long as the cache key includes all important query parameters.

Example SQL:

```sql id="pry762"
SELECT id, name, price
FROM products
WHERE category_id = 7 AND active = true
ORDER BY popularity DESC
LIMIT 20;
```

Cache key:

```text id="ki58rb"
products:category:7:active:true:sort:popularity:limit:20
```

Cached value:

```json id="6mkzk5"
[
  { "id": 8842, "name": "Laptop Stand", "price": 29.99 },
  { "id": 9910, "name": "USB-C Dock", "price": 79.99 }
]
```

If the query changes, the key must change. For example, sorting by price needs a different key.

```text id="w14ifh"
products:category:7:active:true:sort:price_asc:limit:20
```

#### Caching Aggregates

Memcached works well for expensive aggregate query results.

Example SQL:

```sql id="np1taa"
SELECT
  DATE(created_at) AS day,
  COUNT(*) AS order_count,
  SUM(total) AS revenue
FROM orders
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY day;
```

Cache key:

```text id="mmk5mh"
dashboard:orders:last_30_days
```

Cached value:

```json id="s5xcu0"
[
  {
    "day": "2026-04-01",
    "order_count": 892,
    "revenue": 45210.75
  },
  {
    "day": "2026-04-02",
    "order_count": 914,
    "revenue": 46883.20
  }
]
```

Example benefit:

```json id="kq7bd9"
{
  "dashboardRequestsPerMinute": 300,
  "ttlSeconds": 300,
  "databaseQueriesAvoided": "many repeated aggregate scans"
}
```

Aggregate caching is useful when dashboards are read frequently but can tolerate slightly stale data.

#### Caching Reference Tables

Reference tables are strong Memcached candidates because they change rarely and are read often.

Example SQL:

```sql id="0p2abr"
SELECT code, name, currency
FROM countries;
```

Cache key:

```text id="0a35yx"
ref:countries
```

Cached value:

```json id="5z3no7"
{
  "DE": {
    "name": "Germany",
    "currency": "EUR"
  },
  "US": {
    "name": "United States",
    "currency": "USD"
  }
}
```

Example use:

```json id="kmb0a7"
{
  "countryCode": "DE",
  "countryName": "Germany",
  "source": "memcached"
}
```

Reference data can often have long TTLs because it changes infrequently.

### Cache Invalidation

Memcached does not automatically know when the database changes. The application must delete or refresh cached values when underlying database rows change.

#### Delete on Write

A common strategy is to delete cache entries after updating the database. The next read repopulates the cache.

Example database update:

```sql id="9stbrr"
UPDATE products
SET price = 34.99
WHERE id = 8842;
```

Example invalidation:

```text id="28147t"
delete product:8842:details
delete products:category:7:active:true:sort:popularity:limit:20
```

Example result:

```json id="cjlnzv"
{
  "databaseUpdated": true,
  "cacheKeysDeleted": [
    "product:8842:details",
    "products:category:7:active:true:sort:popularity:limit:20"
  ]
}
```

Deleting is often safer than trying to update every cached copy because the next read will rebuild from the database.

#### TTL-Based Invalidation

TTL-based invalidation lets cached values expire automatically.

Example:

```text id="5ja6t7"
set dashboard:orders:last_30_days 0 300 4096
...
```

This keeps the dashboard result for 5 minutes.

Example trade-off:

```json id="yft37c"
{
  "ttl": "5 minutes",
  "benefit": "fewer database queries",
  "risk": "dashboard may show data up to 5 minutes stale"
}
```

TTL-based invalidation is simple, but it allows temporary staleness.

#### Versioned Keys

Versioned keys avoid stale data when the cached format changes.

Old key:

```text id="mp8ick"
v1:user:1001:profile
```

New key:

```text id="frxgxs"
v2:user:1001:profile
```

Example result:

```json id="cyzrum"
{
  "oldCacheIgnored": true,
  "newKeyUsed": "v2:user:1001:profile"
}
```

This is useful when application code changes the shape of cached JSON or serialized objects.

### Common Usage Patterns

Memcached is intentionally narrow, but it is very effective in the right roles.

#### Database Query Cache

This is the primary Memcached use case.

Example:

```json id="5swczy"
{
  "query": "SELECT id, name, price FROM products WHERE id = 8842",
  "cacheKey": "product:8842:details",
  "ttl": "300 seconds"
}
```

The database remains the source of truth. Memcached only stores a temporary copy.

#### Session Cache

Memcached can store session data, although Redis is often chosen when persistence or richer features are needed.

Example key:

```text id="z68wyz"
session:abc123
```

Example value:

```json id="0b11l8"
{
  "user_id": 1001,
  "csrf_token": "token-value",
  "expires_at": "2026-04-25T12:30:00Z"
}
```

If Memcached loses session data, users may be logged out. This may be acceptable for some applications but not others.

#### Fragment or Page Cache

Memcached can store rendered HTML fragments or full pages.

Example key:

```text id="a8z1jx"
page:/products/8842
```

Example value:

```html id="01t1v9"
<div class="product">
  <h1>Laptop Stand</h1>
  <span>$29.99</span>
</div>
```

Example benefit:

```json id="7yr7ua"
{
  "templateRenderingSkipped": true,
  "databaseQuerySkipped": true,
  "servedFrom": "memcached"
}
```

This is useful for high-traffic pages that are expensive to render.

#### Lightweight Rate Limiting

Memcached counters can support simple rate limiting.

Example flow:

```text id="wkvmof"
Key: rate:ip:203.0.113.10
TTL: 60 seconds
Increment on each request
Reject when count > 100
```

Example output:

```json id="4jydar"
{
  "ip": "203.0.113.10",
  "count": 84,
  "limit": 100,
  "allowed": true
}
```

For complex or high-assurance rate limiting, Redis Lua scripts or a dedicated rate-limit service may be better.

### Memcached vs Redis

Memcached and Redis are often compared because both are used as in-memory caches. Their design goals are different.

| Feature                | Memcached                 | Redis                                                     |
| ---------------------- | ------------------------- | --------------------------------------------------------- |
| Main purpose           | Simple distributed cache  | Data structure store, cache, broker, lightweight database |
| Data model             | Key-value blobs           | Strings, hashes, lists, sets, sorted sets, streams        |
| Persistence            | None                      | RDB and AOF available                                     |
| Distribution           | Client-side hashing       | Redis Cluster hash slots                                  |
| Replication            | Not built-in like Redis   | Built-in primary-replica                                  |
| Pub/Sub                | Not supported             | Supported                                                 |
| Streams                | Not supported             | Supported                                                 |
| Scripting              | Not supported             | Lua / functions                                           |
| Memory model           | Slab allocator            | More varied structures and encodings                      |
| Operational complexity | Lower                     | Higher                                                    |
| Best fit               | Disposable database cache | Richer caching and data-structure use cases               |

Example decision:

```json id="xu8lsa"
{
  "chooseMemcachedWhen": [
    "you need a simple cache",
    "values are small serialized blobs",
    "data is disposable",
    "you want low operational complexity"
  ],
  "chooseRedisWhen": [
    "you need sorted sets or hashes",
    "you need persistence",
    "you need streams or pub/sub",
    "you need atomic server-side logic"
  ]
}
```

Memcached is often the better choice when the use case is simply “cache database query result by key.” Redis is better when the cache also needs richer behavior.

### Monitoring and Maintenance

Memcached should be monitored because cache health directly affects database load and application latency.

Useful command:

```text id="rs7fel"
stats
```

Example metrics:

```json id="x0zye7"
{
  "curr_items": "number of currently stored items",
  "bytes": "memory currently used",
  "limit_maxbytes": "configured memory limit",
  "get_hits": "successful cache reads",
  "get_misses": "cache misses",
  "evictions": "items removed due to memory pressure",
  "curr_connections": "current client connections"
}
```

Important metrics include:

* Hit ratio.
* Miss ratio.
* Eviction count.
* Memory usage.
* Current connections.
* Item count.
* Network throughput.
* Get/set command rates.
* Database load during cache misses.

Example monitoring output:

```json id="n5gvak"
{
  "hitRatio": "88%",
  "memoryUsage": "76%",
  "evictionsLastHour": 320,
  "getMissesLastHour": 45000,
  "status": "healthy"
}
```

If hit ratio is low, the cache may not be storing the right data, TTLs may be too short, or keys may be poorly designed.

If evictions are high, the cache may need more memory or better item selection.

### Failure Behavior

Memcached should be treated as an optional acceleration layer. The application should keep working if Memcached is unavailable, although it may be slower.

Example failure:

```json id="zo1q62"
{
  "memcached": "unavailable",
  "fallback": "query database",
  "userImpact": "higher latency"
}
```

The danger is that if Memcached fails under heavy traffic, the database may suddenly receive a large number of requests.

Example failure cascade:

```json id="rbr13t"
{
  "event": "cache_cluster_down",
  "databaseTrafficBefore": "5k qps",
  "databaseTrafficAfter": "80k qps",
  "risk": "database overload"
}
```

Mitigations include:

* Database query limits.
* Circuit breakers.
* Request coalescing.
* Stale cache fallback where possible.
* Gradual cache warmup.
* Avoiding simultaneous expiration of many hot keys.

### Security Considerations

Memcached should not be exposed to the public internet. It has historically been abused in amplification attacks when publicly reachable over UDP.

Basic security practices:

* Bind Memcached to private interfaces.
* Use firewall rules or security groups.
* Disable UDP if not needed.
* Restrict access to trusted application servers.
* Do not store sensitive data unless encrypted by the application.
* Use SASL authentication if supported and required.
* Place Memcached inside private networks only.

Example safe network posture:

```json id="mdiw1i"
{
  "publicInternetAccessible": false,
  "allowedClients": ["app-server-subnet"],
  "udpEnabled": false,
  "sensitiveDataStored": false
}
```

Example risky posture:

```json id="j5l6ni"
{
  "port": 11211,
  "publicInternetAccessible": true,
  "risk": "critical"
}
```

Because Memcached is a cache, applications often put user profiles, sessions, or rendered content in it. Treat this data as sensitive if it contains private information.

### Best Practices

1. **Use Memcached for disposable cached data**  The database or source service should remain the source of truth.
2. **Cache repeated database reads** Focus on primary-key lookups, expensive list queries, aggregates, and reference data.
3. **Design clear cache keys** Include entity type, ID, filters, sorting, pagination, tenant, and schema version where needed.
4. **Set appropriate TTLs** Use shorter TTLs for frequently changing data and longer TTLs for stable reference data.
5. **Invalidate on writes** Delete affected keys after database updates.
6. **Avoid huge values** Memcached is best for compact serialized values, not large files or reports.
7. **Monitor hit ratio and evictions** A cache with low hit ratio or high eviction rate may not be helping enough.
8. **Prepare for cache failure** Applications should degrade gracefully when Memcached is unavailable.
9. **Use consistent hashing** This reduces key remapping when cache nodes are added or removed.
10. **Keep it private** Never expose Memcached directly to the internet.
