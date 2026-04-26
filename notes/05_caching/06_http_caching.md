## HTTP Caching

HTTP caching is the process of storing copies of HTTP responses so that future requests can be served without contacting the origin server. It operates at multiple layers — the browser, intermediate proxies, reverse proxies, and CDN edge nodes — and is controlled primarily through standardised HTTP headers. Correctly configured HTTP caching can dramatically reduce latency, lower server load, and improve the experience for end users on slow or expensive connections.

```
               HTTP Caching Layers

  +----------+        +----------+        +----------+        +----------+
  | Browser  |        | Forward  |        | Reverse  |        |  Origin  |
  | Cache    |<------>| Proxy    |<------>| Proxy /  |<------>|  Server  |
  | (client) |        | (ISP/org)|        |   CDN    |        |          |
  +----------+        +----------+        +----------+        +----------+
      |                    |                   |                    |
   Private             Shared             Shared              Authoritative
   per user           per org           per region              source

  Each layer stores a cached copy keyed on the request URL (and Vary fields).
  A cache HIT at any layer avoids a round-trip to every layer to its right.
```

- Browser caches are **private** and store responses only for the user whose session created them.
- Shared caches such as CDN edge nodes are **public** and may serve the same stored response to many different users.
- Each caching layer reduces **latency** proportionally to how close it sits to the end user.
- A response that is cached at the browser avoids **all** network I/O, making it the fastest possible outcome.
- Caching at the reverse proxy level is **effective** at shielding origin servers from repeated identical requests.

### Cache-Control Header

`Cache-Control` is the primary HTTP header for specifying caching directives. It appears in both request and response messages.

```
  Example response with Cache-Control:

  HTTP/1.1 200 OK
  Content-Type: application/json
  Cache-Control: public, max-age=3600, stale-while-revalidate=60
  ETag: "v3-abc123"
  Last-Modified: Sat, 26 Apr 2026 06:00:00 GMT

  { "id": 7, "name": "Widget" }
```

#### Response Directives

| Directive | Effect |
|-----------|--------|
| `public` | Response may be stored by any shared cache |
| `private` | Response is only for the requesting user; shared caches must not store it |
| `no-cache` | Cache must revalidate with origin before serving a stored response |
| `no-store` | Cache must not store the response at all |
| `max-age=N` | Response is fresh for N seconds from the time it was generated |
| `s-maxage=N` | Overrides `max-age` for shared caches (CDNs, proxies) |
| `must-revalidate` | Once stale, cache must not serve the response without successful revalidation |
| `proxy-revalidate` | Like `must-revalidate` but applies only to shared caches |
| `immutable` | Response will not change during its freshness lifetime; browsers skip revalidation |
| `stale-while-revalidate=N` | Serve stale response for up to N seconds while fetching a fresh one in the background |
| `stale-if-error=N` | Serve stale response for up to N seconds if origin returns an error |

#### Request Directives

| Directive | Effect |
|-----------|--------|
| `no-cache` | Force revalidation even if cache has a fresh copy |
| `no-store` | Do not cache the response to this request |
| `max-age=0` | Treat any cached copy as stale |
| `max-stale=N` | Accept a response that has been stale for at most N seconds |
| `min-fresh=N` | Require the response to be fresh for at least another N seconds |
| `only-if-cached` | Return a stored response or a 504; never contact the origin |

- The `no-cache` directive does **not** disable caching entirely; it forces revalidation before the stored entry can be used.
- The `no-store` directive is the correct way to **prevent** any persistent copy of a sensitive response from being retained.
- Setting `immutable` on versioned assets is **optimal** because browsers skip the conditional request entirely, saving a round-trip.
- `stale-while-revalidate` improves **perceived** performance by serving an old copy immediately while silently refreshing in the background.

### Freshness and Staleness

A cached response transitions from fresh to stale after its freshness lifetime expires.

```
  Freshness Lifetime Calculation

  Response stored at t=0
  max-age = 3600 s (1 hour)

  t=0       t=1800        t=3600      t=4200
  |---------|-------------|-----------|-------->
  |< fresh (serve without revalidation) >|stale|

  Age header = current_time - Date header value
  Fresh if Age < max-age
```

- The `Age` header is **set** by caches to indicate how many seconds the response has been held in the cache.
- A heuristic freshness value may be **applied** when no explicit directives are present, typically 10 % of the interval since `Last-Modified`.
- Stale responses are **served** only if the origin is unreachable and `stale-if-error` is configured, or when `stale-while-revalidate` permits it.
- Shared caches compare the `Date` header against the current time to calculate **staleness** correctly even across time zones.

### Conditional Requests and Revalidation

When a cached response becomes stale, the cache can ask the origin whether the content has changed rather than fetching the full body.

```
  Revalidation Flow (ETag)

  Client/Cache           Origin Server
      |                       |
      |-- GET /api/user ------>|
      |   If-None-Match: "v3" |
      |                       |
      |<-- 304 Not Modified --|  (no body, headers only)
      |   ETag: "v3"          |
      |                       |
      Cache is refreshed and   |
      freshness timer resets.  |
      Response served from     |
      local copy.              |
```

- `ETag` is a **fingerprint** (opaque string) that uniquely identifies a specific version of a resource.
- `Last-Modified` is a **timestamp** that represents when the origin last changed the resource.
- The `If-None-Match` request header sends the **ETag** from the cached copy; the server returns 304 if the ETag still matches.
- The `If-Modified-Since` request header sends the `Last-Modified` **date**; the server returns 304 if the resource has not changed since that time.
- A 304 Not Modified response **omits** the body, saving bandwidth while allowing the cache to reset its freshness timer.
- Strong ETags (`"abc123"`) require **byte-level** equality, while weak ETags (`W/"abc123"`) allow semantically equivalent responses to match even if bytes differ.

### Vary Header

The `Vary` header instructs caches to store separate copies of a response based on the value of specified request headers.

```
  Vary: Accept-Encoding

  Request 1: Accept-Encoding: gzip   -> cached under key (URL + gzip)
  Request 2: Accept-Encoding: br     -> cached under key (URL + br)
  Request 3: Accept-Encoding: (none) -> cached under key (URL + identity)

  Three separate cache entries for the same URL.
```

- A `Vary: Accept-Encoding` directive tells shared caches to **maintain** separate copies for each compression variant.
- `Vary: Accept-Language` causes CDNs to **store** per-language versions, which is useful for server-side localised responses.
- Varying on `Cookie` or `Authorization` effectively **disables** caching at shared proxies because each user has a unique header value.
- Minimising the set of `Vary` fields improves **cache hit rates** by reducing key cardinality.

### Pragma and Expires (Legacy)

- `Pragma: no-cache` is a **legacy** HTTP/1.0 directive that behaves like `Cache-Control: no-cache` and is retained only for backward compatibility.
- The `Expires` header sets an absolute expiry date and is **superseded** by `max-age` in HTTP/1.1, but some older CDNs and proxies still honour it.
- When both `Expires` and `Cache-Control: max-age` are present, `max-age` takes **precedence** in HTTP/1.1-compliant caches.

### Browser Caching

Browsers maintain their own private cache stored on the user's disk or in memory.

```
  Browser Cache Decision Tree

  New navigation to URL
         |
         v
   Check memory cache
         |
   HIT --+-- MISS
    |              |
    v              v
  Serve       Check disk cache
  immediately       |
              HIT --+-- MISS
               |            |
               v            v
         Check freshness  Fetch from
               |           network
         FRESH-+-STALE
           |          |
           v          v
         Serve    Revalidate
         copy     (conditional
                   request)
```

- Memory cache in browsers is **fastest** because it survives only for the current navigation session and requires no disk I/O.
- Disk cache persists **across** browser sessions and is used for large or frequently reused resources like fonts and images.
- Hard refreshes (`Ctrl+Shift+R`) **bypass** the disk cache and force a full network request with `Cache-Control: no-cache` on every outgoing request.
- Service workers give developers **programmatic** control over the browser cache, enabling offline support and customised caching strategies.
- `Link: rel=preload` hints tell the browser to **fetch** resources early into the memory cache before they are needed by the page.

### Cache Busting

When content changes but the URL stays the same, stale cached copies continue to be served until they expire.

- Appending a content **hash** to the filename (e.g., `main.a3c4d5.js`) changes the URL on every deploy, bypassing cached copies automatically.
- A query string version parameter (e.g., `?v=42`) is a **simpler** but less reliable technique because some caches ignore query strings.
- Using a short `max-age` (e.g., 60 s) on HTML pages while setting a **long** TTL (e.g., 1 year) on versioned static assets balances freshness with performance.
- CDN cache purge APIs allow **immediate** invalidation of specific URLs after a deployment without waiting for TTL expiry.
- The `Surrogate-Key` or `Cache-Tag` header groups related resources so that a single **tag-based** purge call can invalidate all affected entries at once.

### HTTP/2 and HTTP/3 Caching

- HTTP/2 server push allows the origin to **proactively** send assets into the browser cache before the client requests them.
- Cache digests (a proposed extension) let the **browser** advertise which resources it already has cached, preventing redundant pushes.
- HTTP/3 runs over QUIC, which **reduces** connection establishment latency but does not change the caching semantics defined by HTTP headers.
- Early hints (103 status code) allow servers to **stream** `Link: rel=preload` headers before the full response is ready, accelerating resource discovery.

### Security Considerations

- Sensitive responses such as authentication tokens must carry `Cache-Control: private, no-store` to **prevent** shared caches from retaining them.
- Cache poisoning attacks **inject** crafted responses into a shared cache so subsequent users receive malicious content; strict URL normalisation and input validation are defences.
- The `Vary: Origin` header mitigates **CORS**-related cache poisoning by ensuring responses are only served to requests with matching origin headers.
- Web application firewalls and CDN rules can **block** abnormal request headers that are commonly used in cache deception attacks.
- Responses containing personally identifiable information should **never** be stored in a shared cache, even with short TTLs.

### Best Practices

- Serve all static assets with `Cache-Control: public, max-age=31536000, immutable` and **embed** a content hash in the filename to achieve aggressive caching with instant invalidation.
- Set `Cache-Control: no-cache` on HTML entry points so browsers always **revalidate** the page, picking up updated asset fingerprints on each deploy.
- Use `ETag` or `Last-Modified` on API responses to enable **conditional** revalidation and reduce unnecessary data transfer.
- Avoid `Vary: *`, which **disables** caching entirely by telling caches no two responses are equivalent regardless of headers.
- Monitor cache hit ratios at every layer and **investigate** a low CDN hit rate caused by overly short TTLs or excessive query-string variation.
- Test caching behaviour with `curl -I` and browser DevTools Network panel (look for `(disk cache)` or `304` responses) to **verify** headers before going to production.
