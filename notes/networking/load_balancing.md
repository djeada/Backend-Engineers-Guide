## Load Balancing

Load balancing is a key component of distributed systems, spreading traffic across multiple servers or nodes. It helps avoid overloading any single server and prevents sending requests to non-operational servers.

### Benefits of Load Balancing

- Better parallelization of server tasks
- Reduced server downtime

### How Load Balancers Work

- Load balancers send health checks or heartbeats to assess server availability.
- Traffic is routed using various algorithms, including:
  - Least Connection Method: Routes to server with fewest active connections.
  - Least Response Time Method: Routes to server with fewest active connections and lowest average response time.
  - Least Bandwidth Method: Routes to server serving the least amount of traffic (in megabits per second).
  - Round Robin: Requests are sent to servers in a set order.
  - Weighted Round Robin: Similar to Round Robin, but considers server computing capacity.
  - IP Hash Method: Client IP address is hashed to determine server routing (layer 4 load balancing).
  - Consistent Hashing: Most requests go to the same server, even when servers are added or removed, improving in-memory cache relevance.
  - Layer 7 Load Balancing: Requests are hashed based on content, requiring more resources but offering more flexibility.

### Fault Tolerance

- Load balancers can be a single point of failure.
- Use a cluster of load balancers with heartbeats to ensure fault tolerance (active and passive load balancers).
