## Load Balancing

Load balancing is a key component of distributed systems, allowing for the spread of traffic across multiple servers or nodes. By keeping track of the status of each server, load balancing helps to avoid overloading any single server or, in the event of a crash, sending requests to a server that is no longer operational. Load balancers should be added between any layers of the system that involve multiple nodes.

### Benefits of Load Balancing
- Improved parallelization of server tasks 
- Reduced downtime of servers 

### How Load Balancers Work
Load balancers periodically send **health checks** or **heartbeats** to servers in order to assess their availability, updating their pool of healthy servers accordingly. Traffic is then routed using one of many algorithms, including:
- **Least Connection Method**: Traffic is directed to the server with the fewest active connections. This is useful when dealing with many persistent connections, such as webhooks. 
- **Least Response Time Method**: Traffic is directed to the server with the fewest active connections and the lowest average response time. 
- **Least Bandwidth Method**: Traffic is directed to the server currently serving the least amount of traffic (in megabits per second). 
- **Round Robin**: An order is created for the servers and requests are sent to the next server in the order. 
- **Weighted Round Robin**: The same as Round Robin, but taking into account a weight for each server which indicates its computing capacity. 
- **IP Hash Method**: The client IP address is hashed in order to determine which server to route to (layer 4 load balancing, which can only look at network details). 
- **Consistent Hashing**: The majority of requests go to the same server even when servers are added and taken away, in order to increase in-memory cache relevance on the server itself. 
- **Layer 7 Load Balancing**: Requests are hashed based on the content of the request, requiring more computing resources but providing more flexibility. 

### Fault Tolerance
The load balancer is itself a single point of failure, making it important to ensure its fault tolerance. This can be done by using a cluster of load balancers that send heartbeats to one another, such that if one load balancer fails the other takes over (active and passive load balancer).
