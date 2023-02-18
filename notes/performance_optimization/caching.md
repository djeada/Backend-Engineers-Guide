
## Caching

Caching data in a distributed system allows you to store copies of data on faster hardware or hardware located closer to the end user. This can greatly improve application performance, however, caching can become complicated as storing multiple copies of data can lead to having to deal with stale (outdated) data. Additionally, as caches are designed for faster reads, they often have far fewer memory than databases, so it is important to delete old entries from the cache.

### Types of Cache

There are various types of caches that can be employed in a distributed system:

- **Hardware caches** - On CPU (L1, L2, L3 cache). Often the computer will use memory to cache disk results.
- **Application server cache** - Memory on the application server that remembers the results of certain queries, and returns them back if they are requested again. Caches at this level may not guarantee that all requests will hit them, and instead a global or distributed cache may need to be used.
- **Content Distribution Network (CDN)** - Serve large amounts of static media. A request asks the CDN for content, and if it is not there it queries the backend, serves it, and caches it locally (pull CDN). It is also possible to directly upload content, which is beneficial for sites with either low traffic or data that does not change very frequently (like a newspaper). When using a CDN, URLs for static content will need to be changed, and care must be taken to not serve stale content.

### Cache Write Policies

When dealing with caches, there are various write policies that can be employed:

- **Write Through** - Data is written to the cache and database at the same time. This allows for complete data consistency (assuming neither fails, in which case distributed transactions may need to be used, which are slow). However, this can slow down write requests. 
- **Write Around** - Data is written to the database only. On a cache miss, the data is then pulled from the database into the cache.
- **Write Back** - Data is first written to the cache only. Writing to permanent storage is done after some amount of time. This is the fastest, but risks inconsistencies in the data if the cache crashes and cannot push to the database.

### Cache Eviction Policies

When dealing with caches, there are various eviction policies that can be employed:

- **First In First Out (FIFO)** 
- **Last In First Out (LIFO)**
- **Least Recently Used (LRU)** - Probably the best option
- **Least Frequently Used (LFU)**
- **Random Replacement**
