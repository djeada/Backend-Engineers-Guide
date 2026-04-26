## Load Balancing in Distributed Systems

Load balancing is central to designing robust distributed systems. It distributes incoming requests or workloads across multiple servers so that no single machine becomes overloaded. Instead of clients connecting directly to one backend server, they connect to a load balancer, which decides which server should handle each request.

This improves reliability, scalability, and performance. If one server becomes slow or unavailable, the load balancer can route traffic to healthier servers. If traffic increases, more servers can be added behind the load balancer to handle the extra demand.

```text
High-Level Load Balancing

         +---------+
         |  Client |
         +----+----+
              |
      HTTP/TCP Requests
              v
        +-----+------+
        | Load       |
        | Balancer   |
        +-----+------+
              |
      Distributes requests
              v
  +-----------+-----------+
  |    Server 1 (S1)     |
  +-----------+-----------+
  |    Server 2 (S2)     |
  +-----------+-----------+
  |    Server 3 (S3)     |
  +-----------+-----------+
```

Example request flow:

```text
Client sends request to app.example.com.
DNS resolves app.example.com to the load balancer.
The load balancer selects Server 2.
Server 2 processes the request.
The response returns through the load balancer to the client.
```

Example output:

```json
{
  "requestId": "req-123",
  "selectedServer": "server-2",
  "status": "success",
  "responseTimeMs": 42
}
```

The client does not need to know which backend server handled the request. The load balancer hides the server pool and presents a single stable entry point.

---

### Significance of Load Balancing

Load balancing is important because distributed systems need to handle traffic reliably even when demand changes or individual machines fail. Without load balancing, one server might become overloaded while others remain underused.

A load balancer helps use resources more evenly. It spreads requests across available servers so that CPU, memory, network, and connection capacity are used more efficiently.

Load balancing can also reduce latency. When requests are distributed across multiple servers, more work can happen in parallel. A user request is less likely to wait behind a long queue on one busy machine.

High availability is another major benefit. If one server crashes or stops responding, the load balancer can remove it from rotation and send traffic to healthy servers.

Load balancing also supports scalability. When traffic grows, teams can add more servers to the backend pool. The load balancer then starts distributing requests to the new servers.

Example scaling output:

```json
{
  "serversBefore": 3,
  "serversAfter": 6,
  "averageCpuBefore": "88%",
  "averageCpuAfter": "46%",
  "p95LatencyBeforeMs": 420,
  "p95LatencyAfterMs": 170
}
```

This shows how adding servers behind a load balancer can reduce resource pressure and improve response times.

---

### How Load Balancers Work

Load balancers use routing rules and algorithms to decide where each request should go. The decision may be based on server health, connection count, response time, bandwidth usage, client IP, cookies, request path, headers, or backend capacity.

A simple load balancer might send requests to servers in order. A more advanced load balancer might inspect application-level data and route `/api` requests to one cluster while sending `/static` requests to another.

---

#### Health Checks

Health checks allow the load balancer to determine whether each backend server is available and ready to receive traffic. The load balancer periodically sends a request to each server and checks the response.

A health check might call an endpoint such as `/health`, `/ready`, or `/status`. If a server fails multiple checks, the load balancer removes it from rotation. When it recovers, the load balancer can add it back.

Example health check request:

```http
GET /health HTTP/1.1
Host: server-1.internal
```

Example healthy output:

```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected"
}
```

Example unhealthy output:

```json
{
  "status": "unhealthy",
  "database": "timeout"
}
```

Example load balancer decision:

```json
{
  "server": "server-1",
  "health": "unhealthy",
  "action": "removed_from_rotation"
}
```

Health checks prevent the load balancer from sending users to broken or overloaded servers.

---

## Traffic Distribution Techniques

Different load balancing algorithms work better for different kinds of applications. Some are simple and predictable. Others are more adaptive and consider real-time server conditions.

---

### 1. Least Connection

The least connection algorithm sends each new request to the server with the fewest active connections. This is useful when requests vary in duration.

For example, one request may finish in 20 milliseconds, while another may keep a connection open for 30 seconds. Round robin would not know the difference, but least connection can avoid sending too many new requests to a server that is already busy.

Example server state:

```json
{
  "server-1": {
    "activeConnections": 120
  },
  "server-2": {
    "activeConnections": 45
  },
  "server-3": {
    "activeConnections": 80
  }
}
```

Example decision:

```json
{
  "selectedServer": "server-2",
  "reason": "fewest active connections"
}
```

Least connection is useful for APIs, file uploads, WebSockets, and systems where requests may have very different lifetimes.

---

### 2. Least Response Time

Least response time considers both server latency and active connections. It attempts to route requests to the server that is likely to respond fastest.

This is useful when servers have different performance characteristics or when one server is becoming slower due to CPU, database, or network pressure.

Example server state:

```json
{
  "server-1": {
    "activeConnections": 40,
    "averageResponseTimeMs": 180
  },
  "server-2": {
    "activeConnections": 55,
    "averageResponseTimeMs": 90
  },
  "server-3": {
    "activeConnections": 20,
    "averageResponseTimeMs": 300
  }
}
```

Example decision:

```json
{
  "selectedServer": "server-2",
  "reason": "best balance of active connections and response time"
}
```

This strategy can improve user experience because it responds to actual server performance rather than simply counting requests.

---

### 3. Least Bandwidth

Least bandwidth sends new requests to the server currently using the least network bandwidth. This is useful when responses are large or when servers handle different payload sizes.

For example, a video service, file download service, or image processing platform might care more about bandwidth usage than simple request count.

Example server bandwidth usage:

```json
{
  "server-1": "850 Mbps",
  "server-2": "300 Mbps",
  "server-3": "620 Mbps"
}
```

Example decision:

```json
{
  "selectedServer": "server-2",
  "reason": "lowest current bandwidth usage"
}
```

This helps avoid saturating one server’s network interface while others still have available capacity.

---

### 4. Round Robin

Round robin distributes requests sequentially across the server pool. If there are three servers, the first request goes to Server 1, the second to Server 2, the third to Server 3, and then the cycle repeats.

```text
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1
Request 5 → Server 2
```

Example output:

```json
{
  "algorithm": "round_robin",
  "requestNumber": 4,
  "selectedServer": "server-1"
}
```

Round robin is simple and works well when servers have similar capacity and requests have similar processing costs.

Weighted round robin extends this idea by assigning more traffic to stronger servers.

Example weighted distribution:

```json
{
  "server-1": {
    "weight": 1
  },
  "server-2": {
    "weight": 2
  },
  "server-3": {
    "weight": 1
  }
}
```

Example request pattern:

```text
Server 1 → Server 2 → Server 2 → Server 3 → Server 1 → Server 2 → Server 2 → Server 3
```

Server 2 receives more requests because it has a higher weight.

---

### 5. IP Hash

IP hash uses the client’s IP address to select a backend server. The same client IP usually maps to the same backend server.

This can be useful for session persistence. If session data is stored locally on a backend server, routing the same client to the same server can prevent session loss.

Example:

```text
hash(198.51.100.20) → Server 2
```

Example output:

```json
{
  "clientIp": "198.51.100.20",
  "selectedServer": "server-2",
  "reason": "IP hash mapping"
}
```

The downside is that traffic may become uneven if many users come from the same NAT gateway, office network, or mobile carrier IP range. It also depends on the stability of the client IP address.

---

### 6. Consistent Hashing

Consistent hashing maps requests, session IDs, cache keys, or user IDs onto a hash ring. Servers are also placed on the ring. A request goes to the server closest to its hash position.

The main benefit is stability. When a server is added or removed, only a subset of keys needs to move to different servers. This is especially useful for caching systems, distributed storage, and stateful routing.

Example mapping:

```text
hash(user-123) → Server A
hash(user-456) → Server C
hash(user-789) → Server B
```

Example output after adding a server:

```json
{
  "serversBefore": ["server-a", "server-b", "server-c"],
  "serversAfter": ["server-a", "server-b", "server-c", "server-d"],
  "remappedKeys": "small subset only"
}
```

Consistent hashing helps preserve cache locality. Most users or keys continue going to the same server even after the cluster changes.

---

### 7. Layer 7 Load Balancing

Layer 7 load balancing operates at the application layer. It can inspect HTTP headers, paths, methods, cookies, hostnames, and sometimes request bodies.

This allows content-aware routing. For example, static assets can go to a static cluster, API requests can go to an application cluster, and admin requests can go to a restricted backend.

Example Layer 7 routing rules:

```text
/static/*        → static-server-pool
/api/*           → api-server-pool
/admin/*         → admin-server-pool
Host: shop.*     → ecommerce-pool
Host: docs.*     → documentation-pool
```

Example output:

```json
{
  "requestPath": "/api/orders",
  "selectedPool": "api-server-pool",
  "reason": "path-based routing"
}
```

Layer 7 load balancing is powerful, but it requires more processing because the load balancer must inspect application-level data. It is common in reverse proxies, API gateways, ingress controllers, and cloud application load balancers.

```text
ASCII DIAGRAM: Multiple Load Balancing Methods

           +------------------+
           |   Load Balancer  |
           +--------+---------+
                    |
    +---------------+---------------+
    |                               |
    v                               v
+----------------+            +----------------+
|   Server Pool  |            |   Routing via  |
| LeastConn, RR  |            | IP/Consistent  |
| etc.           |            | Hash, etc.     |
+----------------+            +----------------+
```

---

## Load Balancer Resilience

A load balancer improves resilience for backend servers, but the load balancer itself can become a single point of failure if it is not deployed carefully.

If all traffic must pass through one load balancer and that load balancer fails, the entire application may become unreachable. Production systems usually use redundancy to avoid this.

---

### 1. Load Balancer Clustering

Load balancer clustering runs multiple load balancers together. They may operate in active-active or active-passive mode.

In an **active-active** configuration, multiple load balancers handle traffic at the same time. In an **active-passive** configuration, one load balancer handles traffic while another waits as a standby.

Example active-active output:

```json
{
  "loadBalancers": ["lb-1", "lb-2", "lb-3"],
  "mode": "active-active",
  "trafficDistribution": "shared"
}
```

Example active-passive output:

```json
{
  "active": "lb-1",
  "passive": "lb-2",
  "failoverReady": true
}
```

A heartbeat mechanism can monitor whether each load balancer node is still alive.

---

### 2. Active-Passive Pair

In an active-passive setup, one load balancer is active and the other is on standby. If the active load balancer fails, the passive one takes over.

This often uses a virtual IP address or DNS failover so clients continue using the same endpoint.

Example failover sequence:

```text
lb-1 is active.
lb-2 is passive.
lb-1 stops responding.
lb-2 takes over the virtual IP.
Traffic resumes through lb-2.
```

Example output:

```json
{
  "failedLoadBalancer": "lb-1",
  "newActiveLoadBalancer": "lb-2",
  "failoverStatus": "completed"
}
```

This prevents one load balancer failure from taking down the whole service.

---

### 3. DNS-Based Load Balancing

DNS-based load balancing distributes traffic by returning different IP addresses for the same hostname. For example, `app.example.com` may resolve to multiple load balancer IPs.

Example DNS response:

```text
app.example.com → 203.0.113.10
app.example.com → 203.0.113.11
app.example.com → 203.0.113.12
```

Example output:

```json
{
  "hostname": "app.example.com",
  "returnedIps": [
    "203.0.113.10",
    "203.0.113.11",
    "203.0.113.12"
  ],
  "strategy": "DNS round robin"
}
```

DNS-based load balancing can be useful, but it has limitations. DNS caching means clients may continue using an old IP until the TTL expires. For this reason, DNS load balancing is often combined with health checks and low TTL values.

---

## Best Practices for Load Balancing

A load balancer should be configured with both performance and reliability in mind. Poor configuration can cause uneven traffic, failed requests, duplicate writes, or unnecessary latency.

### Use Health Checks

Health checks should verify that a server is truly ready to handle requests. A simple process check may not be enough. A good health check may confirm that the application is running, dependencies are reachable, and the server is not in a maintenance state.

Example health response:

```json
{
  "status": "ready",
  "database": "ok",
  "cache": "ok"
}
```

---

### Monitor Performance

Track metrics such as requests per second, latency, error rates, backend health, active connections, queue depth, and response codes.

Example monitoring output:

```json
{
  "requestsPerSecond": 2400,
  "p95LatencyMs": 160,
  "backend5xxRate": "0.2%",
  "activeConnections": 12500,
  "healthyBackends": 8,
  "unhealthyBackends": 1
}
```

These metrics help teams detect uneven traffic distribution, slow servers, overload, or failing backends.

---

### Enable TLS Offloading

TLS offloading means the load balancer handles HTTPS encryption and decryption. Backend servers can then receive plain HTTP traffic or use internal TLS depending on security requirements.

Example output:

```json
{
  "clientToLoadBalancer": "HTTPS",
  "loadBalancerToBackend": "HTTP",
  "tlsCertificateManagedAt": "load_balancer"
}
```

For sensitive internal environments, teams may still use TLS or mutual TLS between the load balancer and backend services.

---

### Implement Caching

If the load balancer or edge layer supports caching, it can serve repeated requests directly without forwarding them to backend servers.

Example cached response:

```http
HTTP/1.1 200 OK
X-Cache: HIT
Cache-Control: max-age=300
```

Example output:

```json
{
  "cacheStatus": "HIT",
  "backendContacted": false,
  "latencyMs": 12
}
```

Caching is especially useful for static assets, public pages, and read-heavy endpoints that do not change frequently.

---

### Use Session Persistence Carefully

Some applications need sticky sessions, meaning the same client must keep going to the same backend. This can be done with IP hash, cookies, or session-aware routing.

Example sticky-session cookie:

```http
Set-Cookie: LB_SERVER=server-2; Path=/; Secure; HttpOnly
```

Example output:

```json
{
  "client": "user-123",
  "stickyBackend": "server-2",
  "reason": "session persistence cookie"
}
```

Sticky sessions are useful, but they can reduce load-balancing flexibility. If a sticky backend fails, the user’s session may be interrupted unless session state is stored in a shared database or cache.

---

### Automate Scaling

Load balancer configuration should integrate with auto-scaling systems. When new servers are added, they should automatically join the backend pool after passing health checks. When servers are removed, they should be drained gracefully.

Example auto-scaling event:

```json
{
  "event": "scale_out",
  "newServer": "server-9",
  "healthCheck": "passed",
  "action": "added_to_load_balancer_pool"
}
```

Example graceful removal:

```json
{
  "server": "server-3",
  "action": "draining",
  "newRequests": "blocked",
  "existingRequests": "allowed_to_finish"
}
```

Graceful draining prevents active users from being disconnected when servers are removed for scaling, deployments, or maintenance.
