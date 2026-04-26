## Database Caching

Database caching stores frequently requested **database query results, rows, aggregates, or relational lookup data** in a faster layer so the application does not repeatedly execute the same expensive database operations. The main goal is to reduce database read load, lower query latency, and protect the primary database from repetitive traffic.

In backend systems, databases often become bottlenecks because many requests depend on the same tables. For example, thousands of users may repeatedly request the same product page, category list, dashboard count, or account metadata. Instead of executing the same SQL query again and again, the application can cache the result and reuse it until the data changes or expires.

```text
+--------------+
| Application  |
+-------+------+
        |
        | 1. Need product id=123
        v
+-------+------+
| Database     |
| Cache        |
+-------+------+
        |
        | 2. Cache miss
        v
+-------+------+
| PostgreSQL / |
| MySQL / etc. |
+--------------+
```

Example uncached database query:

```sql
SELECT id, name, price, stock_count
FROM products
WHERE id = 123;
```

Example cached result:

```json
{
  "id": 123,
  "name": "Laptop Stand",
  "price": 29.99,
  "stock_count": 42
}
```

If many users request product `123`, the application can serve this cached row instead of repeatedly querying the `products` table.

### Why Database Caching Matters

Database queries can be expensive. Even a simple query may involve network latency, query parsing, permission checks, index lookups, row fetching, locking behavior, serialization, and result transfer. More complex queries may involve joins, grouping, sorting, filtering, subqueries, and scans over large tables.

Caching is especially helpful when:

* The same query is executed frequently.
* The result changes less often than it is read.
* The query is expensive because of joins, aggregations, or large table scans.
* The database is under heavy read load.
* Slightly stale data is acceptable for a short period.

Example expensive query:

```sql
SELECT category_id, COUNT(*) AS product_count
FROM products
WHERE active = true
GROUP BY category_id;
```

Example cached aggregate:

```json
{
  "1": 1842,
  "2": 921,
  "3": 377
}
```

Without caching, every request for category counts may force the database to aggregate data again. With caching, the result can be reused for a short period, such as 60 seconds or 5 minutes.

### Concrete Database Cache Targets

Database caching should focus on specific database access patterns. Not every query should be cached.

#### 1. Single-Row Lookups

Single-row lookups are common in APIs. They often use a primary key and return one entity.

Example query:

```sql
SELECT id, username, display_name, avatar_url
FROM users
WHERE id = 42;
```

Cache key:

```text
db:user:id:42
```

Cached value:

```json
{
  "id": 42,
  "username": "alice",
  "display_name": "Alice",
  "avatar_url": "https://cdn.example.com/alice.png"
}
```

This is useful when the same user profile is loaded frequently across pages, comments, posts, or notifications.

#### 2. Multi-Row List Queries

List queries return multiple rows and are often used for category pages, feeds, search results, or admin tables.

Example query:

```sql
SELECT id, name, price
FROM products
WHERE category_id = 7 AND active = true
ORDER BY popularity DESC
LIMIT 20;
```

Cache key:

```text
db:products:category:7:active:true:sort:popularity:limit:20
```

Cached value:

```json
[
  { "id": 123, "name": "Laptop Stand", "price": 29.99 },
  { "id": 456, "name": "USB-C Dock", "price": 79.99 }
]
```

This type of cache must include all query parameters in the key. If `category_id`, `sort`, `limit`, filters, or pagination values change, the cache key must change too.

#### 3. Expensive Join Results

Joins can be expensive, especially when they combine large tables or are executed frequently.

Example query:

```sql
SELECT
  o.id AS order_id,
  o.created_at,
  o.total,
  c.name AS customer_name,
  c.email AS customer_email
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.id = 9001;
```

Cache key:

```text
db:order_summary:id:9001
```

Cached value:

```json
{
  "order_id": 9001,
  "created_at": "2026-04-25T10:30:00Z",
  "total": 149.99,
  "customer_name": "Alice Example",
  "customer_email": "alice@example.com"
}
```

This avoids repeatedly joining `orders` and `customers` when the order summary is viewed many times.

#### 4. Aggregates and Counts

Aggregates are often good cache candidates because they may scan or group many rows.

Example query:

```sql
SELECT COUNT(*) AS open_ticket_count
FROM support_tickets
WHERE status = 'open';
```

Cache key:

```text
db:support_tickets:count:status:open
```

Cached value:

```json
{
  "open_ticket_count": 128
}
```

For dashboards, counts and aggregates can often tolerate short staleness.

Another example:

```sql
SELECT
  DATE(created_at) AS day,
  SUM(total) AS revenue
FROM orders
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY day;
```

Cache key:

```text
db:orders:revenue:last_30_days:daily
```

Cached value:

```json
[
  { "day": "2026-03-27", "revenue": 18420.50 },
  { "day": "2026-03-28", "revenue": 19311.25 }
]
```

This is a strong cache candidate because daily revenue charts are often read repeatedly but do not need millisecond-level freshness.

#### 5. Reference Tables

Reference tables are small, stable tables used frequently in joins or validations.

Examples:

```sql
SELECT code, name
FROM countries;
```

```sql
SELECT id, name, tax_rate
FROM tax_regions;
```

```sql
SELECT id, label
FROM order_statuses;
```

Cache key:

```text
db:reference:countries
```

Cached value:

```json
{
  "DE": "Germany",
  "FR": "France",
  "US": "United States"
}
```

Reference data is one of the safest database-specific cache targets because it changes rarely and is read often.

### Cache-Aside with a Database Example

The most common database caching pattern is **cache-aside**. The application explicitly checks the cache before querying the database.

Flow:

```text
1. Application needs product 123.
2. Check cache key db:product:id:123.
3. If found, return cached product.
4. If missing, query database.
5. Store database result in cache.
6. Return result.
```

Example Python-style pseudo-code:

```python
def get_product(product_id):
    cache_key = f"db:product:id:{product_id}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    product = db.query_one(
        """
        SELECT id, name, price, stock_count
        FROM products
        WHERE id = %s
        """,
        [product_id]
    )

    if product is not None:
        cache.set(cache_key, product, ttl=300)

    return product
```

Example first request:

```json
{
  "product_id": 123,
  "cache": "MISS",
  "database_query_executed": true,
  "latency_ms": 84
}
```

Example second request:

```json
{
  "product_id": 123,
  "cache": "HIT",
  "database_query_executed": false,
  "latency_ms": 4
}
```

This example is specifically caching the result of a database lookup, not general application state.

### Read-Through Database Cache

In a read-through pattern, the cache layer knows how to load missing data from the database. The application asks the cache for data, and the cache handles the database read on a miss.

Example:

```text
Application asks cache for db:user:id:42.
Cache misses.
Cache loader executes SELECT query.
Cache stores result.
Cache returns result to application.
```

Example loader query:

```sql
SELECT id, username, display_name
FROM users
WHERE id = 42;
```

Example output:

```json
{
  "strategy": "read-through",
  "cache_key": "db:user:id:42",
  "cache_status": "MISS",
  "loaded_from_database": true
}
```

Read-through can keep application code cleaner, but it requires a cache abstraction that understands how to fetch data from the database.

### Write-Through Database Cache

In a write-through pattern, the application writes changes to the database and cache together. This helps keep cached database rows fresh.

Example update:

```sql
UPDATE products
SET price = 34.99
WHERE id = 123;
```

Cache update:

```text
SET db:product:id:123 {"id":123,"name":"Laptop Stand","price":34.99,"stock_count":42}
```

Example output:

```json
{
  "database_updated": true,
  "cache_updated": true,
  "cache_key": "db:product:id:123"
}
```

Write-through is useful when cached rows must stay close to the current database state. The downside is that writes become more complex because both the database and cache must be updated correctly.

### Cache Invalidation with Database Writes

Database cache invalidation means deleting or refreshing cached query results when the underlying database rows change.

Example cached keys:

```text
db:product:id:123
db:products:category:7:active:true:sort:popularity:limit:20
db:orders:revenue:last_30_days:daily
```

If product `123` changes, it may not be enough to invalidate only `db:product:id:123`. The product might also appear in category lists, search results, recommendations, or aggregate counts.

Example update:

```sql
UPDATE products
SET price = 34.99
WHERE id = 123;
```

Invalidation actions:

```text
DELETE db:product:id:123
DELETE db:products:category:7:active:true:sort:popularity:limit:20
DELETE db:homepage:popular_products
```

Example output:

```json
{
  "database_row_updated": "products.id=123",
  "invalidated_cache_keys": [
    "db:product:id:123",
    "db:products:category:7:active:true:sort:popularity:limit:20",
    "db:homepage:popular_products"
  ]
}
```

This is the hard part of database caching: one row can influence many cached query results.

### TTLs for Database Query Results

A TTL, or time to live, controls how long a cached database result remains valid before expiring.

Different database data should have different TTLs.

| Data Type           | Example Query                                   |                           Suggested TTL |
| ------------------- | ----------------------------------------------- | --------------------------------------: |
| Country list        | `SELECT * FROM countries`                       |                           Hours or days |
| Product details     | `SELECT * FROM products WHERE id = ?`           |                                 Minutes |
| Inventory count     | `SELECT stock_count FROM products WHERE id = ?` |                                 Seconds |
| Dashboard aggregate | `SELECT COUNT(*) FROM events ...`               |                            1–15 minutes |
| User permissions    | `SELECT role FROM user_roles ...`               | Very short TTL or explicit invalidation |

Example TTL configuration:

```json
{
  "db:reference:countries": "24h",
  "db:product:id:*": "5m",
  "db:inventory:product:*": "10s",
  "db:dashboard:*": "15m"
}
```

The TTL should depend on how often the database value changes and how harmful stale data would be.

### Database-Specific Consistency Problems

Caching database results introduces consistency problems because the cache and database can disagree.

Example:

```sql
SELECT price
FROM products
WHERE id = 123;
```

Database value:

```json
{
  "price": 34.99
}
```

Cached value:

```json
{
  "price": 29.99
}
```

Problem:

```json
{
  "status": "inconsistent",
  "database_price": 34.99,
  "cache_price": 29.99,
  "cause": "cache was not invalidated after product update"
}
```

For product descriptions, this might be acceptable briefly. For account balances, payment status, permissions, or inventory reservations, it may not be acceptable.

### Queries That Usually Should Not Be Cached

Some database queries are poor cache candidates.

#### Highly Personalized Queries

Example:

```sql
SELECT *
FROM notifications
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 20;
```

This may change frequently and may have a low reuse rate across users. Caching it can be useful in some cases, but the cache key must include the user ID and invalidation must be precise.

#### Security-Critical Permission Checks

Example:

```sql
SELECT role
FROM user_roles
WHERE user_id = 42 AND organization_id = 9;
```

Caching permissions for too long can be dangerous. If an admin removes a user’s access, stale cached permissions may still allow access.

Safer approach:

```text
Use very short TTLs or explicit invalidation on role changes.
```

#### Rapidly Changing Counters

Example:

```sql
SELECT stock_count
FROM products
WHERE id = 123;
```

Inventory and counters can change rapidly. If stale values are harmful, either avoid caching or use very short TTLs and strong invalidation.

### Concrete Example: Caching Product Pages from SQL

Suppose an e-commerce product page needs this query:

```sql
SELECT
  p.id,
  p.name,
  p.description,
  p.price,
  p.stock_count,
  c.name AS category_name
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE p.id = 123 AND p.active = true;
```

Cache key:

```text
db:product_page:id:123
```

Cached value:

```json
{
  "id": 123,
  "name": "Laptop Stand",
  "description": "Adjustable aluminum laptop stand",
  "price": 29.99,
  "stock_count": 42,
  "category_name": "Accessories"
}
```

When the product is updated:

```sql
UPDATE products
SET price = 34.99
WHERE id = 123;
```

Invalidate:

```text
DELETE db:product_page:id:123
```

Then the next page request reloads the fresh value from the database.

Example reload output:

```json
{
  "cache_status": "MISS",
  "database_query_executed": true,
  "new_price": 34.99
}
```

### Concrete Example: Caching Dashboard Aggregates

A dashboard may run this expensive query:

```sql
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

```text
db:dashboard:orders:last_30_days
```

Cached value:

```json
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

This query may be expensive because it scans and groups many order rows. If the dashboard is viewed often, caching the result for 5 minutes can significantly reduce database load.

Example cache result:

```json
{
  "cache_key": "db:dashboard:orders:last_30_days",
  "ttl": "5m",
  "database_queries_avoided_last_hour": 1140
}
```

### Concrete Example: Caching Reference Tables

Reference tables are excellent database cache candidates because they change rarely and are read often.

Example query:

```sql
SELECT code, name, currency
FROM countries;
```

Cache key:

```text
db:ref:countries
```

Cached value:

```json
{
  "DE": {
    "name": "Germany",
    "currency": "EUR"
  },
  "US": {
    "name": "United States",
    "currency": "USD"
  },
  "GB": {
    "name": "United Kingdom",
    "currency": "GBP"
  }
}
```

Example use in application:

```text
Order has country_code = "DE".
Application reads country metadata from cache.
Application displays Germany, EUR.
```

Example output:

```json
{
  "country_code": "DE",
  "country_name": "Germany",
  "currency": "EUR",
  "source": "database_cache"
}
```

This avoids repeatedly querying the `countries` table for stable lookup data.

### Monitoring Database Cache Effectiveness

Database cache monitoring should focus on whether the cache is actually reducing database work.

Useful metrics include:

```json
{
  "cache_hit_ratio": "87%",
  "database_queries_avoided": 250000,
  "average_cached_read_ms": 4,
  "average_database_read_ms": 92,
  "evictions_per_minute": 80,
  "stale_read_incidents": 0
}
```

Important questions:

```text
Which SQL queries are being cached?
Which cache keys have the most hits?
Which cache keys miss too often?
Are cached results becoming stale?
Is the database CPU lower after caching?
Are slow queries reduced?
```

A high cache hit ratio is useful only if it reduces expensive database work. Caching cheap queries that are rarely repeated may add complexity without meaningful benefit.

### Database Caching Best Practices

1. **Cache expensive and repeated database reads** Focus on repeated SQL queries, joins, aggregates, and lookup tables.
2. **Design cache keys from query parameters** Include IDs, filters, sort order, pagination, tenant ID, and user scope where relevant.
3. **Use short TTLs for frequently changing data** Inventory, permissions, and status fields should not stay stale for long.
4. **Invalidate caches on writes** When database rows change, delete or refresh related cached query results.
5. **Avoid caching sensitive permission checks for too long** Stale authorization data can create security issues.
6. **Measure database impact** Track reduced query volume, lower database CPU, improved p95 latency, and fewer slow queries.
7. **Protect against cache stampedes** When an expensive cached query expires, prevent thousands of requests from recomputing it at once.

Example stampede-safe behavior:

```json
{
  "cache_key": "db:dashboard:orders:last_30_days",
  "cache_expired": true,
  "first_request_recomputes": true,
  "other_requests_wait_or_use_stale_value": true
}
```
