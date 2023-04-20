## Caching

Caching stores copies of data on faster hardware or closer to users, improving application performance. It can become complex due to stale data and limited memory.

### Types of Cache
- **Hardware caches**: On CPU (L1, L2, L3 cache); memory caches disk results
- **Application server cache**: Memory on server stores query results; global or distributed cache may be needed
- **Content Distribution Network (CDN)**: Serves static media; can use pull CDN or directly upload content; requires URL changes and stale content management

### Cache Write Policies
- **Write Through**: Data written to cache and database simultaneously; ensures consistency but slows write requests
- **Write Around**: Data written to database only; on cache miss, data pulled from database into cache
- **Write Back**: Data written to cache first, then to permanent storage later; fastest but risks inconsistencies

### Cache Eviction Policies
- **First In First Out (FIFO)**
- **Last In First Out (LIFO)**
- **Least Recently Used (LRU)**: Often the best option
- **Least Frequently Used (LFU)**
- **Random Replacement**
