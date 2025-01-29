## Load Balancing in Distributed Systems

Load balancing is central to designing robust distributed systems. It ensures that incoming requests or workloads are equitably distributed across multiple servers or nodes, thereby preventing any single server from becoming a bottleneck. This technique also boosts system resilience, providing higher availability and scalability.

```
ASCII DIAGRAM: High-Level Load Balancing

         +---------+
         |  Client |
         +----+----+
              |
      (HTTP/TCP Requests)
              v
        +-----+------+
        | Load       |
        | Balancer   |
        +-----+------+
              |
      (Distributes requests)
              v
  +-----------+-----------+
  |    Server 1 (S1)     |
  +-----------+-----------+
  |    Server 2 (S2)     |
  +-----------+-----------+
  |    Server 3 (S3)     |
  +-----------+-----------+
```

- A client sends requests to the **Load Balancer (LB)** instead of a single server.  
- The load balancer **distributes** requests among multiple servers based on a chosen algorithm.  
- **Responses** are returned to the load balancer, which then passes them back to the client.

### Significance of Load Balancing

Implementing a load balancer in a distributed system offers **multiple** advantages:

- **Resource Utilization**  
  - Each server handles a fair portion of the traffic, avoiding under-utilization or overburdening.
- **Reduced Latency**  
  - Requests can be processed **concurrently**, leading to faster response times.
- **High Availability**  
  - If a server fails, the load balancer redirects traffic to other active servers.  
  - Ensures minimal disruption during hardware or software failures.
- **Scalability**  
  - Additional servers can be **added** seamlessly behind the load balancer to handle increased loads.

### How Load Balancers Work

Load balancers apply algorithms to decide where each incoming request goes. They typically include:

#### Health Checks

- The load balancer **pings** or **sends heartbeats** to servers to verify if they are up and responding correctly.  
- Unresponsive servers are **taken** out of rotation until they recover.

#### Traffic Distribution Techniques

Below are common methods for distributing requests:

1. **Least Connection**  
   - Routes new requests to the server with the fewest active connections.  
   - Helpful if requests have varying durations, preventing busy servers from becoming overloaded.

2. **Least Response Time**  
   - Considers both the **current number** of active connections and the **average latency**.  
   - Aims to pick the server that can respond **fastest**.

3. **Least Bandwidth**  
   - Monitors ongoing traffic in Mbps or Gbps and sends new requests to the server with the **lowest** bandwidth utilization.

4. **Round Robin**  
   - Sequentially distributes requests across servers in a **cyclical** order (S1 → S2 → S3 → S1 …).  
   - **Weighted Round Robin** accounts for each server’s capacity, giving a powerful server more requests.

5. **IP Hash**  
   - Uses a **hash** of the client’s IP address to pick a server.  
   - Ensures the same client IP typically routes to the same server (session persistence), common in Layer 4 load balancing.

6. **Consistent Hashing**  
   - The hash of the request (e.g., session ID, cache key) maps to a server “ring.”  
   - When a server is **added** or **removed**, only a small subset of the keys or requests are remapped, aiding caching consistency.

7. **Layer 7 Load Balancing**  
   - **Application-level** load balancing that inspects HTTP headers, URLs, cookies, etc.  
   - Allows content-aware routing (e.g., static file requests go to a specialized cluster, API requests go elsewhere).  
   - More resource-intensive but offers **fine-grained** control.

```
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
| (LeastConn, RR)|            |   IP/Consistent|
| etc.           |            |   Hash, etc.   |
+----------------+            +----------------+
```


### Load Balancer Resilience

Ironically, load balancers can become a **single point of failure** if not designed carefully. Various techniques mitigate this risk:

1. **Load Balancer Clustering**  
   - Multiple load balancers run in **active-active** or **active-passive** configurations.  
   - A *heartbeat* mechanism monitors whether a load balancer node has failed.

2. **Active-Passive Pair**  
   - If the **active** LB node fails, the **passive** node takes over, preventing downtime.  
   - Usually involves sharing a **virtual IP** or using DNS-based failover.

3. **DNS-based Load Balancing**  
   - DNS records (like `round-robin DNS`) distribute traffic among multiple LB IPs.  
   - Can be combined with **health checks** at the DNS level.

### Best Practices for Load Balancing

- **Use Health Checks**: Regularly verify server availability to avoid sending requests to unhealthy nodes.
- **Monitor Performance**: Track metrics like **requests per second**, **latency**, **error rates**, and **connection counts** to optimize distribution.
- **Enable TLS Offloading**: Terminate SSL/TLS at the load balancer to reduce CPU overhead on backend servers.
- **Implement Caching**: If feasible, use **edge caching** or LB caching to minimize requests hitting servers.
- **Session Persistence**: For applications needing sticky sessions, configure IP hash, cookies, or other *persistence* methods carefully.
- **Automate Scaling**: Integrate load balancer configuration with **auto-scaling** groups so that adding/removing servers updates load balancing pools dynamically.
