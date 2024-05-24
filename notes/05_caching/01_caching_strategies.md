## Caching

Caching accelerates application execution by keeping frequently accessed or computationally expensive data closer to where it's needed. This involves trade-offs between memory use, stale data, and system complexity.

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
  +------v------+           +------+------+ 
  |   Cache     |           |             |
  |(Fast Access)|<----------+             |
  +-------------+  Cached   |             |
                            |             |
                            +-------------+
```

### Types of Cache

Caches appear at various levels in modern systems, serving different roles:

- **Hardware caches**: These caches reside within the CPU itself (L1, L2, L3 caches) or between the CPU and the disk, caching memory pages (disk cache).

- **Application server cache**: A cache within an application server holds often-queried data, reducing load on databases. In a distributed system, each server might possess its own cache (local cache), or servers may share a common cache (distributed cache).

- **Content Distribution Network (CDN)**: A CDN acts as a cache for static content, relieving origin servers from handling all traffic and delivering content from locations closer to users. CDNs may employ "pull" models, caching requested content, or "push" models, caching content uploaded directly to the CDN.

### Cache Write Policies

Write policies manage how caches handle write operations:

- **Write Through**: The cache and database receive write operations simultaneously, preserving consistency at the cost of write speed.

- **Write Around**: Writes go directly to the database, bypassing the cache. The cache only pulls data from the database in response to a cache miss.

- **Write Back (or Write Behind)**: Writes initially go to the cache, which asynchronously updates the database. This approach minimizes write latency but risks inconsistencies or data loss.

### Cache Eviction Policies

When a cache is full, the eviction policy determines which items to discard:

- **First In First Out (FIFO)**: Removes the oldest items first.

- **Last In First Out (LIFO)**: Removes the newest items first.

- **Least Recently Used (LRU)**: Removes items that haven't been accessed for the longest time.

- **Least Frequently Used (LFU)**: Removes items accessed less frequently.

- **Random Replacement (RR)**: Removes items randomly.
