## Network Communications

Network communications in a backend context involve the flow of data between clients and server-side systems. A client might be a browser, a mobile app, another backend service, an API gateway, or a scheduled job. The server might be a REST API, GraphQL API, gRPC service, WebSocket server, database, cache, or message broker.

This process spans multiple layers. At the lower levels, data moves over cables, fiber, or wireless signals. At the transport level, protocols such as TCP and UDP define how data is delivered. At the application level, protocols such as HTTP, WebSockets, and gRPC define how software systems structure requests, responses, and messages.

Understanding these layers helps backend developers build systems that are scalable, secure, and reliable. A slow DNS lookup, overloaded load balancer, missing timeout, or inefficient serialization format can affect the entire user experience, even if the application code itself is correct.

### The Layered Perspective

Networking concepts are often explained using layered models. The OSI model has seven layers, while the simplified TCP/IP model usually uses four layers. Backend developers do not always need to work with every low-level detail, but they do need to understand how data moves from the application down through the network and back again.

From a backend point of view, the **transport layer** and **application layer** are especially important. The transport layer handles delivery behavior through protocols such as TCP and UDP. The application layer defines higher-level communication patterns such as HTTP requests, gRPC calls, WebSocket messages, and API responses.

```text
+-------------------------------------------------+
|         Application Layer (HTTP, gRPC, etc.)    |
+-------------------------------------------------+
|         Transport Layer (TCP, UDP)              |
+-------------------------------------------------+
|         Internet Layer (IP)                     |
+-------------------------------------------------+
|         Network Access Layer (Ethernet, Wi-Fi)  |
+-------------------------------------------------+
```

Example application request:

```http
GET /api/posts HTTP/1.1
Host: api.example.com
Accept: application/json
```

Example application response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "posts": [
    {
      "id": 1,
      "title": "Understanding Network Layers"
    }
  ]
}
```

The application sees an HTTP request and response, but underneath that exchange the data is split into packets, routed across networks, delivered through TCP or another transport protocol, and reconstructed by the receiving system. The layered model helps separate these responsibilities so developers can reason about where problems may occur.

### Transport Layer Choices

The transport layer determines how data is delivered between systems. Two common transport protocols are **TCP** and **UDP**. They make different trade-offs between reliability, ordering, and speed.

Backend applications frequently rely on TCP for requests that require reliable delivery, such as web pages, JSON APIs, database connections, and gRPC calls. UDP is often used where low latency matters more than guaranteed delivery, such as live audio, video, gaming, telemetry, DNS, or protocols built on top of UDP such as QUIC.

### TCP vs UDP

**TCP**, or Transmission Control Protocol, is connection-oriented. Before data is sent, the client and server establish a connection. TCP guarantees that data arrives in order and without corruption. If packets are lost, TCP retransmits them.

**UDP**, or User Datagram Protocol, is connectionless. It sends packets without establishing a formal connection and does not guarantee delivery or ordering. This makes UDP lighter and faster in some situations, but the application must handle missing or out-of-order data if that matters.

**TCP**

* Connection-oriented.
* Guarantees ordered delivery and data integrity.
* Uses flow control and congestion control to optimize throughput.

**UDP**

* Connectionless.
* No built-in overhead for acknowledgments or retransmissions.
* Well-suited for cases where low latency is more important than guaranteed delivery.

Example TCP-style exchange:

```text
Client → Server: SYN
Server → Client: SYN-ACK
Client → Server: ACK
Client → Server: HTTP request
Server → Client: HTTP response
```

Example UDP-style exchange:

```text
Client → Server: Datagram 1
Client → Server: Datagram 2
Client → Server: Datagram 3
```

Example output comparison:

```json
{
  "tcp": {
    "delivery": "reliable",
    "ordering": "guaranteed",
    "typicalUses": ["HTTP APIs", "databases", "gRPC"]
  },
  "udp": {
    "delivery": "best effort",
    "ordering": "not guaranteed",
    "typicalUses": ["streaming", "gaming", "DNS", "QUIC"]
  }
}
```

TCP is usually the safer default for backend APIs because most business operations require reliable delivery. UDP is useful when applications can tolerate some packet loss or when another protocol built on top of UDP provides reliability in a different way.

### Application Layer Protocols

Application layer protocols define how software systems communicate at a higher level. They determine request structure, response format, connection behavior, headers, message framing, and sometimes authentication patterns.

Common backend protocols include HTTP-based APIs, WebSockets, and gRPC. Each protocol is designed for different communication needs.

#### HTTP-Based APIs: REST and GraphQL

REST and GraphQL APIs commonly use HTTP. The server listens on a port, usually `80` for HTTP or `443` for HTTPS. The client sends a request with headers and sometimes a body. The server processes the request and returns a response with a status code, headers, and body.

REST usually maps operations to URLs and HTTP methods. GraphQL usually sends a query or mutation document to a single endpoint, often `/graphql`.

An example flow for a REST request looks like this:

1. **DNS Lookup**: The client resolves `api.example.com` to an IP address.
2. **TCP Handshake**: The client and server establish a TCP connection.
3. **TLS Handshake**: If HTTPS is used, encryption parameters are negotiated.
4. **HTTP Request**: The client sends request headers and an optional body.
5. **Application Logic**: The server processes the request and may call databases or other services.
6. **HTTP Response**: The server sends a status code, headers, and response body.

```text
Client (Browser / Mobile)        Server (HTTP/HTTPS Listener)
             |                                  |
   1. DNS     |---------------------------------> (DNS resolves hostname)
             |                                  |
   2. TCP     |------------------ SYN ----------> (Connection attempt)
   3. Hand-   |<----------- SYN-ACK ------------ (Server acknowledges)
      shake   |------------------ ACK ----------> (Connection established)
             |                                  |
   4. TLS     |<==== Key Exchange, if HTTPS ===>|
             |                                  |
   5. HTTP    |------ GET /api/posts HTTP/1.1 -->|
   Request    |                                  |
             |         6. Internal Logic        |
             |          (Database calls, etc.)  |
   7. HTTP    |<-- 200 OK + JSON in body --------|
   Response   |                                  |
```

Example REST request:

```http
GET /api/posts HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=60

{
  "posts": [
    {
      "id": 1,
      "title": "Network Communication Basics"
    },
    {
      "id": 2,
      "title": "Scaling Backend APIs"
    }
  ]
}
```

This response includes a successful HTTP status code, response headers, and a JSON body. The client can parse the JSON and display the posts in the application.

#### WebSockets

WebSockets enable persistent, two-way communication over a single TCP connection. The client begins with an HTTP request that asks the server to upgrade the connection. If the server accepts, the connection switches from normal HTTP request-response behavior to WebSocket message exchange.

WebSockets are useful when the server needs to push updates to the client without waiting for the client to repeatedly poll. Real-time chat, multiplayer games, collaboration tools, dashboards, and notifications often use WebSockets.

```text
+--------------------------+                +--------------------------+
|   WebSocket Client       |                |   WebSocket Server       |
| (Browser, etc.)          |                |  (Backend Service)       |
+--------------------------+                +-----------+--------------+
            |                                     ^
            | 1. HTTP handshake with upgrade       |
            |------------------------------------->|
            |                                     |
            | 2. Connection upgraded to WS        |
            |<-------------------------------------|
            |                                     |
            | 3. Bi-directional communication      |
            |<--------------->                     |
            |                                     |
```

Example WebSocket subscription message:

```json
{
  "type": "subscribe",
  "channel": "chat-room-123",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

Example output from server:

```json
{
  "type": "message",
  "channel": "chat-room-123",
  "data": {
    "user": "Alice",
    "text": "Hello everyone!"
  }
}
```

The server can send this message immediately when the event occurs. The client does not need to make a new HTTP request to check whether a new message is available.

WebSockets can introduce operational complexity because servers may need to track open connections, user subscriptions, authentication state, reconnects, and message delivery behavior.

#### gRPC

gRPC is an RPC framework that runs on top of HTTP/2 and commonly uses Protocol Buffers as its data format. Instead of designing endpoints around resources, developers define services and methods in `.proto` files. Generated client and server code then allows clients to call remote methods in a type-safe way.

gRPC supports unary request-response calls, server streaming, client streaming, and bidirectional streaming. This makes it useful for internal microservices, high-performance backend communication, and systems that need strongly defined contracts.

Example `.proto` service:

```proto
service Bookstore {
  rpc GetBook(GetBookRequest) returns (Book);
}
```

Example grpcurl request:

```bash
grpcurl -plaintext -d '{"id":"123"}' localhost:50051 bookstore.Bookstore/GetBook
```

Example output:

```json
{
  "id": "123",
  "title": "A Sample Book",
  "author": "An Author"
}
```

Although tools like `grpcurl` display data as JSON for readability, the actual gRPC communication usually uses compact binary Protobuf messages over HTTP/2.

### Name Resolution and Service Discovery

Before most application traffic can flow, the client needs to know where to send the request. Humans usually use names such as `api.example.com`, but computers communicate using IP addresses. Name resolution converts a hostname into an address.

Public traffic commonly depends on DNS records such as `A`, `AAAA`, `CNAME`, and `MX`. Internal backend systems may also use service discovery systems, load balancer hostnames, Kubernetes service names, Consul, or cloud provider discovery mechanisms.

* **Recursive DNS resolution** walks from root servers to top-level domain servers and finally to an authoritative server.
* **Caching with TTLs** reduces repeated lookups and lowers latency.
* **Service discovery** gives backend systems stable names even when individual instance IPs change.

Example DNS lookup result:

```text
api.example.com → 203.0.113.10
TTL: 300 seconds
```

Example Kubernetes-style service name:

```text
bookstore-service.default.svc.cluster.local
```

Example output:

```json
{
  "service": "bookstore-service",
  "resolvedTargets": [
    "10.0.1.15",
    "10.0.1.16",
    "10.0.1.17"
  ],
  "ttlSeconds": 30
}
```

If name resolution is slow, stale, or incorrect, the rest of the request path suffers. Backend teams often monitor DNS latency, cache hit rates, and TTL choices alongside application metrics.

### Middleware, Load Balancing, and Reverse Proxies

Backend systems often use load balancers and reverse proxies to manage incoming traffic. A load balancer distributes requests across multiple backend instances. A reverse proxy receives requests from clients and forwards them to the appropriate internal service.

Middleware sits in the request path and handles cross-cutting concerns such as authentication, logging, rate limiting, compression, tracing, request validation, and error handling.

```text
       Internet
          |
          |  Inbound Traffic (User Requests)
          v
+---------------------+
|   Load Balancer /   |
|   Reverse Proxy     |
+---------+-----------+
          |
          | Requests distributed
          |
+---------v---------------------+
|    Pool of Server Instances   |
|  e.g., multiple Docker nodes  |
+------------------------------+
```

Example incoming request:

```http
GET /api/posts HTTP/1.1
Host: api.example.com
X-Request-ID: req-123
```

Example proxy-forwarded request:

```http
GET /api/posts HTTP/1.1
Host: posts-service.internal
X-Request-ID: req-123
X-Forwarded-For: 198.51.100.25
X-Forwarded-Proto: https
```

Example output:

```json
{
  "handledBy": "posts-service-2",
  "requestId": "req-123",
  "status": "success"
}
```

Reverse proxies such as Nginx, HAProxy, Envoy, or cloud load balancers may terminate TLS, apply routing rules, compress responses, enforce rate limits, and forward traffic to internal services.

### Concurrency and Scaling

Scalability depends on how effectively a backend handles many requests at the same time. In a blocking server model, the maximum number of in-flight requests is often limited by the number of available workers, threads, or connections. Throughput depends on how quickly each request finishes.

```text
Max_In_Flight_Requests ≈ Available_Workers
Throughput ≈ Max_In_Flight_Requests / Average_Req_Duration
```

Example calculation:

```text
Available_Workers = 200
Average_Req_Duration = 0.1 seconds

Throughput ≈ 200 / 0.1
Throughput ≈ 2,000 requests per second
```

Example output:

```text
Estimated throughput: 2,000 requests per second
```

This is a simplified formula, but it shows the relationship between concurrency and request duration. If each request takes longer, fewer requests can be completed per second. If the server can handle more concurrent work efficiently, throughput can increase.

When load becomes too high, teams may scale horizontally by adding more instances. Some runtimes and frameworks use asynchronous I/O to handle many connections efficiently. Node.js, Go, Java asynchronous frameworks, and Python async frameworks can support large numbers of concurrent network operations when used correctly.

Example scaling output:

```json
{
  "instancesBefore": 3,
  "instancesAfter": 6,
  "averageCpuBefore": "85%",
  "averageCpuAfter": "48%"
}
```

This example shows horizontal scaling: more instances are added, and traffic is distributed across a larger pool.

### Security Layers

Network security protects data, infrastructure, and users. Security is usually applied at multiple layers, including encrypted transport, firewall rules, authentication, authorization, and monitoring.

#### TLS/SSL

Most production APIs use HTTPS, which is HTTP over TLS. TLS encrypts traffic between the client and server so attackers cannot easily read or tamper with data in transit.

Certificates are issued by Certificate Authorities. During the TLS handshake, the client verifies the server’s certificate and negotiates encryption parameters.

Example HTTPS request:

```http
GET /profile HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Example output:

```json
{
  "name": "Alice",
  "email": "alice@example.com"
}
```

The request and response may look like normal HTTP at the application level, but on the network they are encrypted. This is especially important for credentials, personal data, payment data, session cookies, and API tokens.

#### Firewalls and Security Groups

Backend infrastructure is often protected by firewalls, security groups, network ACLs, or private networking rules. These controls restrict which systems can connect to which ports.

For example, a public load balancer may accept traffic on port `443`, while application servers accept traffic only from the load balancer. A database may accept connections only from application servers.

Example security rule:

```text
Allow inbound TCP 443 from 0.0.0.0/0 to Load Balancer
Allow inbound TCP 8080 from Load Balancer to App Servers
Allow inbound TCP 5432 from App Servers to Database
Deny all other inbound traffic
```

Example output:

```json
{
  "requestToLoadBalancer": "allowed",
  "directRequestToDatabase": "blocked"
}
```

This limits the attack surface by preventing public clients from connecting directly to internal services.

#### Authentication and Authorization

Authentication verifies who the caller is. Authorization verifies what the caller is allowed to do. Backend APIs often use JWTs, OAuth2 access tokens, API keys, or session cookies.

Example authenticated request:

```http
GET /admin/users HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Example unauthorized output:

```json
{
  "error": "Permission denied",
  "code": "PERMISSION_DENIED"
}
```

In this example, the caller may be authenticated but not authorized to access the admin endpoint. Both checks are necessary for secure networked systems.

### Data Formats and Transmission Efficiency

Backend systems need to choose formats that balance readability, performance, compatibility, and size. Common formats include JSON, XML, and Protocol Buffers.

#### JSON, XML, and Protocol Buffers

JSON is widely used because it is human-readable and easy to work with in web applications. XML is still common in some enterprise and legacy systems. Protocol Buffers are common in gRPC and internal microservices where compact binary messages and strong contracts are useful.

Example JSON:

```json
{
  "id": 1,
  "title": "Network Efficiency"
}
```

Example XML:

```xml
<Post>
  <Id>1</Id>
  <Title>Network Efficiency</Title>
</Post>
```

Example Protobuf schema:

```proto
message Post {
  int32 id = 1;
  string title = 2;
}
```

Example output comparison:

```json
{
  "json": "human-readable and widely supported",
  "xml": "structured but verbose",
  "protobuf": "compact and efficient but not directly human-readable"
}
```

The best choice depends on the clients, tooling, performance needs, and whether the API is public or internal.

#### Compression and Caching

Compression reduces payload size by encoding responses more efficiently. Common options include gzip and Brotli. Caching reduces repeated network calls by storing responses temporarily at the client, proxy, CDN, or server layer.

Example compressed request header:

```http
Accept-Encoding: gzip, br
```

Example cacheable response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=300
ETag: "post-123-v1"

{
  "id": 123,
  "title": "Cached Response Example"
}
```

Example cached output:

```http
HTTP/1.1 304 Not Modified
ETag: "post-123-v1"
```

In this example, the client can avoid downloading the full response again if the resource has not changed. Compression saves bandwidth, while caching can reduce latency and server load.

### Reliability Patterns for Networked Backends

Real networks are imperfect. Requests may time out, packets may be dropped, services may become overloaded, and dependencies may fail. Production backends add defensive patterns on top of transport protocols to handle these conditions.

* **Timeouts** prevent requests from waiting forever.
* **Retries with backoff and jitter** recover from short-lived failures without overwhelming the target.
* **Circuit breakers** stop sending traffic to unhealthy dependencies.
* **Idempotency keys** make retries safer for write operations.

These patterns matter because TCP alone does not solve application-level reliability. TCP can retransmit dropped packets, but it cannot decide whether a payment request should be retried, cancelled, or blocked to avoid duplicate charges.

Example request with idempotency key:

```http
POST /orders HTTP/1.1
Host: api.example.com
Idempotency-Key: order-request-abc123
Content-Type: application/json

{
  "itemId": "book-1",
  "quantity": 1
}
```

Example first output:

```json
{
  "orderId": "order-789",
  "status": "created"
}
```

Example retry output:

```json
{
  "orderId": "order-789",
  "status": "already_created_from_same_idempotency_key"
}
```

The idempotency key allows the server to recognize that a retried request is the same operation, not a new order. This is especially important for payments, order creation, and other write operations.

Example circuit breaker output:

```json
{
  "dependency": "payment-service",
  "circuitState": "open",
  "message": "Requests temporarily blocked because the dependency is unhealthy."
}
```

This protects the system from repeatedly calling a failing dependency and making the failure worse.

### Common Network Communication Patterns in Backends

Backend systems use several common communication patterns. The right pattern depends on whether the system needs a direct response, real-time updates, background processing, or continuous streams.

* **Request-Response**: The client sends a request and waits for a response.
* **Pub/Sub**: Publishers send messages to topics, and subscribers receive them.
* **Streaming**: Long-lived connections send continuous data.
* **Fail-Fast Dependency Calls**: Timeouts, retries, and circuit breakers prevent cascading failures.

Example request-response:

```http
GET /users/1 HTTP/1.1
Host: api.example.com
```

Example output:

```json
{
  "id": 1,
  "name": "Alice"
}
```

Example pub/sub event:

```json
{
  "eventType": "UserCreated",
  "userId": 1,
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Example streaming output:

```text
event: order.updated
data: {"orderId":"order-1","status":"processing"}

event: order.updated
data: {"orderId":"order-1","status":"shipped"}
```

Request-response is simple and common for APIs. Pub/sub is useful for decoupling services. Streaming is useful for live data. Fail-fast patterns protect systems when dependencies are slow or unavailable.

Together, these communication patterns give backend systems the flexibility to support normal API calls, real-time updates, asynchronous workflows, and resilient service-to-service communication.
