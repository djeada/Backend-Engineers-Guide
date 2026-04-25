## Data Transmission

Data transmission in API design describes how information moves between a client and a server. It includes the request format, response format, protocol, headers, authentication details, compression behavior, caching rules, and error-handling signals. Good transmission design helps APIs remain fast, secure, predictable, and easy for clients to consume.

Whether an application is stateful or stateless can change what gets transmitted. In a stateless design, each request usually carries more context because the server does not remember previous interactions. In a stateful design, requests may be smaller because the server stores session context, but the infrastructure may become more complex because session data has to be stored, replicated, or synchronized.

### Factors in Data Transmission

API design typically revolves around sending requests and receiving responses. A client sends structured data to the server, and the server returns structured data back to the client. This data is usually accompanied by headers that describe content type, authentication credentials, caching rules, compression support, and other metadata.

A few critical considerations come into play when deciding how to transmit data:

* **Transport Protocol**: HTTP, HTTP/2, and HTTP/3 are common for web-based APIs.
* **Serialization Format**: JSON, XML, Protocol Buffers, or other structured encodings.
* **Security and Encryption**: TLS/SSL protects data while it travels over the network.
* **Compression**: Gzip or Brotli can reduce payload sizes.
* **Caching**: Temporary storage of responses can reduce repeated requests.

Example request:

```http
GET /posts/1 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Accept-Encoding: gzip, br
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=60
Content-Encoding: gzip

{
  "id": 1,
  "title": "Understanding API Data Transmission",
  "author": "Jane"
}
```

This example shows a client requesting JSON data, sending an authorization token, and indicating that it supports compressed responses. The server responds with JSON, includes caching instructions, and may compress the response body to reduce the amount of data sent over the network.

In a stateless system, each request must include everything needed to process it. In a stateful system, the server may already know some context from a session, so the request can sometimes be smaller. However, stateful systems often require additional infrastructure work, such as storing sessions in Redis or replicating session data across nodes.

### Transmission Protocols

Different protocols come with their own rules for data framing, security, performance, and connection management. The best protocol depends on the type of API, the clients consuming it, and whether the application needs request-response communication, streaming, or real-time updates.

#### HTTP/1.1

HTTP/1.1 is still widely used for web APIs. It follows a simple request-response model where the client sends a request and the server returns a response. It is easy to understand, widely supported, and works well for many REST APIs.

However, HTTP/1.1 generally handles one request-response exchange at a time per TCP connection. To achieve concurrency, clients often open multiple connections. This can create overhead when many requests are made at once.

Example request:

```http
GET /books/1 HTTP/1.1
Host: api.example.com
Accept: application/json
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "1",
  "title": "API Design Basics",
  "author": "Jane Smith"
}
```

In this example, the client requests one book, and the server returns one JSON response. This style is simple and works well for many public APIs, but it may be less efficient when a page requires many separate API requests.

#### HTTP/2

HTTP/2 improves performance by allowing multiple requests and responses to be multiplexed over a single TCP connection. This means several streams of data can share one connection without waiting for each request to finish before starting the next one.

HTTP/2 also uses binary framing, which allows more efficient flow control and stream management. This is one reason gRPC uses HTTP/2 as its transport layer.

Example conceptual flow:

```text
Single HTTP/2 connection
├── Stream 1: GET /books/1
├── Stream 2: GET /authors/10
└── Stream 3: GET /reviews?bookId=1
```

Example output:

```json
{
  "connection": "single HTTP/2 connection",
  "streams": [
    { "path": "/books/1", "status": 200 },
    { "path": "/authors/10", "status": 200 },
    { "path": "/reviews?bookId=1", "status": 200 }
  ]
}
```

This example shows how multiple requests can be handled over the same connection. HTTP/2 can reduce connection overhead and improve performance, especially for APIs that make several related calls.

#### HTTP/3

HTTP/3 operates over QUIC, which is built on UDP rather than TCP. It is designed to improve performance, especially when packet loss occurs. With TCP, packet loss can delay multiple streams because all data shares the same ordered connection. QUIC can handle independent streams more efficiently.

HTTP/3 can be helpful for mobile networks, unreliable connections, or latency-sensitive applications. It is still used through familiar HTTP semantics, but the underlying transport behaves differently from HTTP/1.1 and HTTP/2.

Example conceptual flow:

```text
Client uses HTTP/3 over QUIC
Packet loss occurs on one stream
Other streams continue without waiting for the lost packet
```

Example output:

```json
{
  "protocol": "HTTP/3",
  "transport": "QUIC",
  "benefit": "Independent streams can reduce delays caused by packet loss."
}
```

This means HTTP/3 can improve responsiveness in some network conditions. The API design may look similar from a developer’s point of view, but the transport layer can perform better under packet loss or unstable connectivity.

#### WebSockets

WebSockets provide a persistent, two-way communication channel between client and server. Unlike normal HTTP requests, where the client sends a request and waits for a response, WebSockets allow both sides to send messages whenever needed.

This is useful for real-time applications such as chat, live notifications, multiplayer games, collaborative editing, and dashboards. However, WebSockets can introduce complexity because the server may need to track open connections, user identity, subscriptions, and reconnect behavior.

```text
Client                               Server
   |                                   |
   |    1. Connect over WebSocket      |
   | --------------------------------->|
   |                                   |
   |    2. Server keeps an open        |
   |       channel for messages        |
   |<----------------------------------|
   |                                   |
   |    3. Messages flow freely        |
   |<--------------->                  |
   |                                   |
```

Example WebSocket message from client:

```json
{
  "type": "subscribe",
  "channel": "orders",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

Example output from server:

```json
{
  "type": "event",
  "channel": "orders",
  "data": {
    "orderId": "order-123",
    "status": "completed"
  }
}
```

In a stateful setting, the server might maintain a list of active connections and user contexts. In a stateless-style message design, each message can carry enough context, such as an authentication token or subscription ID, so the server can process it without relying heavily on stored session data.

### Serialization Formats

APIs must transmit data in a format that both client and server understand. Serialization is the process of converting structured data into a format that can be sent over the network. Deserialization is the reverse process, where the receiver converts transmitted data back into usable objects or structures.

Different serialization formats have different trade-offs. Some are easy for humans to read, while others are optimized for speed and compact size.

#### JSON

JSON, or JavaScript Object Notation, is one of the most common formats for REST and GraphQL APIs. It is human-readable, easy to parse, and supported by almost every programming language.

Example JSON response:

```json
{
  "id": 123,
  "name": "Example",
  "attributes": ["fast", "secure"]
}
```

Example interpretation:

```text
The response represents one item with an ID, a name, and a list of attributes.
```

JSON is popular because developers can easily inspect it in logs, browsers, terminals, and API testing tools. Its main drawback is that it is text-based, so it can be larger and slower to parse than compact binary formats.

#### XML

XML, or Extensible Markup Language, was more common in older enterprise systems and SOAP-based services. It is flexible and supports attributes, namespaces, and structured documents, but it is usually more verbose than JSON.

Example XML response:

```xml
<Item>
  <Id>123</Id>
  <Name>Example</Name>
  <Attributes>
    <Attribute>fast</Attribute>
    <Attribute>secure</Attribute>
  </Attributes>
</Item>
```

Example interpretation:

```text
The XML response describes the same item as the JSON example, but with more markup.
```

XML can still be useful in systems that rely on schemas, strict document structure, or legacy integrations. However, for modern public APIs, JSON is generally more common because it is lighter and easier for web clients to use.

#### Protocol Buffers

Protocol Buffers, often called Protobuf, is a compact binary serialization format commonly used with gRPC. Data structures are defined in `.proto` files, and code generation tools create language-specific classes or structs.

Example `.proto` message:

```proto
message Item {
  int32 id = 1;
  string name = 2;
  repeated string attributes = 3;
}
```

Example logical data:

```json
{
  "id": 123,
  "name": "Example",
  "attributes": ["fast", "secure"]
}
```

Example interpretation:

```text
The logical data is similar to JSON, but on the wire it is encoded as compact binary Protobuf data.
```

Protobuf is efficient and strongly typed, making it useful for internal microservices, high-throughput systems, and services where performance matters. The trade-off is that binary payloads are not as easy for humans to read without tools.

#### MessagePack, Avro, and Others

Other serialization formats are also used depending on the system’s requirements. MessagePack is similar to JSON in structure but uses a compact binary encoding. Avro is common in data pipelines and event streaming systems because it supports schemas and schema evolution.

Example MessagePack-style logical data:

```json
{
  "event": "user.login",
  "userId": 123,
  "success": true
}
```

Example output description:

```text
The data may look like JSON conceptually, but it is transmitted in a compact binary format.
```

These formats are less common than JSON for public APIs, but they can be valuable inside large systems where payload size, parsing speed, and schema control matter.

### Stateless vs Stateful Transmission Patterns

A stateless application requires each request to carry the necessary context. This may include authentication tokens, user identifiers, request metadata, pagination cursors, filters, or other details needed to complete the request.

A typical formula for additional payload size in a stateless design might be:

```text
Extra_payload = N_contextFields * S_perField
```

Example calculation:

```text
N_contextFields = 5
S_perField = 80 bytes

Extra_payload = 5 * 80
Extra_payload = 400 bytes
```

Example output:

```text
Additional stateless payload size: 400 bytes per request
```

This formula shows that stateless requests may become larger if the client has to repeatedly send context. Over many requests, that extra payload can increase network usage.

By contrast, a stateful design might keep user or session data on the server, reducing the request payload:

```text
Request_payload_stateful < Request_payload_stateless
```

Example stateful request:

```http
GET /profile
Cookie: session_id=abc123
```

Example stateless request:

```http
GET /profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
X-User-Context: region=EU;plan=premium;locale=en-US
```

Example output:

```json
{
  "name": "Alice",
  "plan": "premium",
  "locale": "en-US"
}
```

The stateful request may be smaller because it sends only a session ID. The stateless request may carry a larger token and additional context. However, stateless systems are often easier to scale because any server instance can process the request without needing access to local session memory.

### Security in Transit

Encryption is helpful for protecting sensitive data while it travels between client and server. HTTPS uses TLS to provide confidentiality, integrity, and server authentication. This helps prevent attackers from reading or modifying data in transit.

API keys, OAuth tokens, session cookies, and JWTs should always be sent over HTTPS. Without encryption, credentials can be intercepted and reused by attackers.

#### Example: Passing a Bearer Token

```bash
curl -X GET \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  https://api.example.com/data
```

Example output:

```json
{
  "data": {
    "id": 123,
    "status": "active",
    "owner": "alice"
  }
}
```

In this example, the client includes a bearer token in the `Authorization` header. The server validates the token before returning protected data.

In a stateless design, the server may verify the token signature without storing session information. In a stateful design, the server might use a token or cookie to look up session claims in memory, Redis, or a database.

Example unauthorized output:

```json
{
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED"
}
```

This response means the server rejected the request because the authentication credential was missing, invalid, or expired.

### Compression and Chunking

Compression reduces payload size before data is sent over the network. This can improve response times, especially for large JSON, XML, HTML, or text-based responses. Common compression algorithms include gzip, deflate, and Brotli.

The client can tell the server which compression formats it supports using the `Accept-Encoding` header:

```text
Accept-Encoding: gzip, deflate, br
```

Example response headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: br
```

Example output:

```json
{
  "items": [
    { "id": 1, "name": "Item One" },
    { "id": 2, "name": "Item Two" }
  ]
}
```

The client receives the compressed response and decompresses it before using the data. Compression is helpful for large payloads, but it also adds CPU work for compression and decompression.

Chunked transfer encoding allows a server to send a large response in smaller pieces. This lets the client begin processing before the full response has arrived.

Example chunked-style output:

```text
Chunk 1: {"items":[
Chunk 2: {"id":1,"name":"Item One"},
Chunk 3: {"id":2,"name":"Item Two"}
Chunk 4: ]}
```

Chunking is useful for streaming large files, logs, search results, or long-running responses. However, it can complicate application logic if partial updates must be tracked carefully.

### Caching Layers

Caching reduces data transmission by serving stored responses instead of repeatedly fetching the same data from the origin server. A cache may exist in the browser, a proxy, a CDN, or an application layer.

Caching works best for data that does not change often or can tolerate short periods of staleness. Static resources, product catalogs, public posts, documentation pages, and read-heavy endpoints are common candidates.

```text
        Client
          |
          v
    +-------------+
    |   Cache     |
    |   (Proxy)   |
    +-------------+
          |
          v
+-----------------------+
|      API Server       |
|  (Stateless or not)   |
+-----------------------+
```

Example request:

```http
GET /posts/1
Accept: application/json
```

Example cached output:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=300
X-Cache: HIT

{
  "id": 1,
  "title": "Cached API Responses"
}
```

The `X-Cache: HIT` header indicates that the response came from a cache rather than the origin server. This reduces latency and decreases load on the API server.

Even in a stateful application, some resources may be cacheable if they do not depend on user-specific session state. For example, public product details may be cached, while a user’s private shopping cart should not be cached publicly.

### Conditional Requests and ETags

Conditional requests help clients avoid downloading data that has not changed. The server sends an `ETag`, which acts like a version identifier for a resource. On a later request, the client sends that ETag back using `If-None-Match`.

If the resource has not changed, the server returns `304 Not Modified` and does not send the full response body. This saves bandwidth and processing time.

```text
Client                                 Server
  |   GET /posts/1                      |
  | ----------------------------------> |
  |   200 OK                            |
  |   ETag: "abc123"                    |
  |   {id: 1, title: "Hello"}           |
  | <---------------------------------- |
  |                                     |
  |   GET /posts/1                      |
  |   If-None-Match: "abc123"           |
  | ----------------------------------> |
  |   304 Not Modified                  |
  | <---------------------------------- |
```

Example first response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "abc123"

{
  "id": 1,
  "title": "Hello"
}
```

Example second request:

```http
GET /posts/1
If-None-Match: "abc123"
```

Example second output:

```http
HTTP/1.1 304 Not Modified
ETag: "abc123"
```

In the second response, the server does not return the full JSON body because the client already has the latest version. The client can reuse its cached copy.

| Header              | Direction | Purpose                                                          |
| ------------------- | --------- | ---------------------------------------------------------------- |
| `ETag`              | Response  | Unique identifier for a specific version of a resource           |
| `If-None-Match`     | Request   | Return the resource only if the ETag has changed                 |
| `Last-Modified`     | Response  | Timestamp of the last modification                               |
| `If-Modified-Since` | Request   | Return the resource only if modified after this date             |
| `Cache-Control`     | Both      | Directives for caching behavior, such as `max-age` or `no-cache` |

### Content Negotiation in Detail

Content negotiation allows a client to tell the server what kind of response it prefers. This can include media type, language, compression format, and character encoding.

The server chooses the best available representation based on what the client requests and what the server supports.

Example request headers:

```http
Accept: application/json; q=1.0, application/xml; q=0.5
Accept-Language: en-US, fr; q=0.8
Accept-Encoding: gzip, br
Accept-Charset: utf-8
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Language: en-US
Content-Encoding: br

{
  "message": "Welcome back"
}
```

The `q` value indicates preference. A value of `1.0` is the highest preference. In this example, the client prefers JSON over XML and English over French. The server responds with JSON in English and uses Brotli compression.

Content negotiation helps APIs support different clients without requiring separate endpoints for every format or language.

### Pagination in Data Transmission

Transmitting large datasets in a single response wastes bandwidth and increases latency. Pagination splits large result sets into smaller pages so clients can request only the amount of data they need.

Common pagination strategies include:

* **Offset-based pagination**, which uses `offset` and `limit`.
* **Cursor-based pagination**, which uses an opaque cursor to mark position.
* **Keyset-based pagination**, which uses the last seen value of a sorted column.

Example offset-based request:

```http
GET /posts?offset=20&limit=10
```

Example cursor-based request:

```http
GET /posts?cursor=eyJpZCI6MTAwfQ==&limit=10
```

Example keyset-based request:

```http
GET /posts?created_after=2024-01-15T00:00:00Z&limit=10
```

Example output:

```json
{
  "data": [
    {
      "id": 101,
      "title": "Efficient API Pagination"
    },
    {
      "id": 102,
      "title": "Reducing Payload Size"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6MTAyfQ==",
    "has_more": true,
    "total_count": 5432
  }
}
```

The response includes both the data and pagination metadata. The `next_cursor` value tells the client how to request the next page. The `has_more` field tells the client whether additional results are available.

Cursor-based and keyset-based pagination are often better for large or frequently changing datasets because they avoid some of the consistency problems caused by offset-based pagination.

### Rate Limiting and Throttling

Rate limiting controls how many requests a client can make within a certain time period. Throttling slows or rejects requests when clients exceed allowed limits. These techniques protect the server from overload and help ensure fair usage.

APIs often send rate limit information in response headers so clients can adjust their behavior.

Example successful response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1713465600

{
  "status": "success"
}
```

This response tells the client that the limit is `1000` requests, `847` requests remain, and the limit resets at the provided timestamp.

Example exceeded-limit response:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60

{
  "error": "Rate limit exceeded",
  "code": "TOO_MANY_REQUESTS"
}
```

The `429 Too Many Requests` status tells the client that it has exceeded the allowed rate. The `Retry-After` header tells the client how long to wait before trying again.

### Webhooks for Asynchronous Data Delivery

Webhooks allow a provider to push data to a consumer when an event occurs. Instead of the consumer repeatedly polling the provider for updates, the provider sends an HTTP request to a callback URL.

This reduces unnecessary network traffic and delivers information closer to real time. Webhooks are commonly used for payment events, order updates, build notifications, repository events, and messaging integrations.

```text
Provider                              Consumer
  |   Event occurs                     |
  |   POST https://consumer.com/hook   |
  |   {event: "order.completed", ...}  |
  | ---------------------------------> |
  |   200 OK acknowledgement           |
  | <--------------------------------- |
```

Example webhook request:

```http
POST /hook
Content-Type: application/json
X-Signature: sha256=abc123

{
  "event": "order.completed",
  "orderId": "order-789",
  "amount": 49.99
}
```

Example output from consumer:

```http
HTTP/1.1 200 OK

{
  "received": true
}
```

The provider typically signs the webhook payload with a shared secret. The consumer verifies the signature to confirm that the webhook really came from the trusted provider and was not modified in transit.

If the consumer is temporarily unavailable, the provider may retry delivery according to a retry policy.

Example retry output:

```json
{
  "deliveryId": "evt_123",
  "status": "retry_scheduled",
  "nextAttemptInSeconds": 300
}
```

This means the provider will try again later because the webhook was not successfully delivered.

### Example Requests in Different Formats

Different API styles transmit data in different ways. REST commonly uses JSON over HTTP. GraphQL sends query documents inside JSON request bodies. gRPC uses Protobuf messages over HTTP/2, usually in binary form.

#### JSON-based REST

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"userId":123,"action":"login"}' \
  https://example.com/api/login
```

Example output:

```json
{
  "status": "success",
  "userId": 123,
  "message": "Login recorded"
}
```

In this example, the client sends JSON data to a REST endpoint. The server returns a JSON response with the login status. Depending on the authentication design, session tokens might be returned in a cookie or in an authorization response body.

#### GraphQL

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
        "query": "query { user(id: 123) { name, status } }"
      }' \
  https://example.com/graphql
```

Example output:

```json
{
  "data": {
    "user": {
      "name": "Alice",
      "status": "active"
    }
  }
}
```

The request includes the GraphQL query in JSON form. The response includes only the fields requested by the client: `name` and `status`. This can reduce data transfer when the client needs only a small part of a larger object.

#### gRPC with Protobuf

```bash
grpcurl \
  -d '{"id":"123"}' \
  -plaintext \
  localhost:50051 bookstore.Bookstore/GetBook
```

Example output:

```json
{
  "id": "123",
  "title": "A Sample Book",
  "author": "An Author"
}
```

The client sends a request that corresponds to a Protobuf message. Although `grpcurl` displays the request and response as JSON for readability, the actual gRPC communication normally uses compact binary Protobuf data over HTTP/2.

This makes gRPC efficient for internal service-to-service communication, while REST and GraphQL are often easier to inspect and use directly from web clients.
