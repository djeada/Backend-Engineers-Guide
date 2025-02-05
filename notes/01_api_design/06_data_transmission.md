## Data transmissio  
Data transmission in API design covers how information is sent and received between a client and a server. This involves choosing data formats, transport protocols, security measures, and techniques to ensure both correctness and efficiency. Whether an application is stateful or stateless affects the data payloads and what metadata is carried on each request.

### Factors in Data Transmission  
API design typically revolves around sending requests and receiving responses. Data travels back and forth in a structured format, often accompanied by headers and security tokens. A few critical considerations come into play when deciding how to transmit data:

- **Transport Protocol**: HTTP, HTTP/2, and HTTP/3 are common for web-based APIs.  
- **Serialization Format**: JSON, XML, Protocol Buffers, or other structured encodings.  
- **Security and Encryption**: TLS/SSL for data in transit.  
- **Compression**: Gzip or Brotli can reduce payload sizes.  
- **Caching**: Storing responses temporarily to reduce redundant requests.  

In a stateless world, each request must contain everything needed to process it. In a stateful system, requests can be smaller because the server stores user context, but more overhead might appear at the infrastructure level, such as session replication across multiple nodes.

### Transmission Protocols  
Different protocols come with their own rules for data framing, security, and performance:

#### HTTP/1.1  
It is still widely used but supports only a single request-response at a time per TCP connection. To achieve concurrency, multiple connections are opened. This can cause overhead when requests are numerous.

#### HTTP/2  
It adds multiplexing, allowing multiple requests and responses to be interleaved over a single TCP connection. This reduces round trips and can speed up API calls. The binary framing layer also permits efficient flow control.

#### HTTP/3  
It operates over QUIC (built on UDP) rather than TCP and aims to offer improved performance, especially when packet loss occurs, because QUIC can handle data streams without resetting the entire connection.

#### WebSockets  
WebSockets provide a persistent, two-way channel over a single TCP connection. They are particularly useful in real-time applications where server and client frequently communicate. However, WebSockets can introduce complexity around state maintenance if the server must track each open connection.

```
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

In a stateful setting, the server might maintain a list of active connections and user contexts. In a stateless scenario, each message can carry necessary context (like an authentication token) so the server knows how to handle it without remembering session details.

### Serialization Formats  
APIs must transmit data in a way that client and server both understand. Common formats include:

#### JSON  
JavaScript Object Notation is human-readable and widely used in RESTful APIs. A typical JSON response might look like this:

```json
{
  "id": 123,
  "name": "Example",
  "attributes": ["fast", "secure"]
}
```

#### XML  
Extensible Markup Language was more common in older SOAP-based services. It is verbose compared to JSON, but some systems still rely on it:

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

#### Protocol Buffers  
Often used with gRPC, Protocol Buffers (protobuf) is a binary format defined by `.proto` files. It is compact and efficient but less human-readable. Protobuf works well in high-performance environments or internal microservices.

#### MessagePack, Avro, and Others  
These formats are also used to reduce size or improve parsing speed. They are less widespread than JSON and XML for public APIs but remain popular internally where performance matters.

### Stateless vs Stateful Transmission Patterns  
A stateless application requires each request to carry necessary context. A typical formula for additional payload size in a stateless design might be:

```
Extra_payload = N_contextFields * S_perField
```

N_contextFields is how many user/session fields must be included, and S_perField is the size (in bytes) of each field. Over many requests, stateless designs can lead to higher network usage if there is significant context. However, scaling is simpler because each request can be handled by any server instance.

By contrast, a stateful design might keep user/session data on the server, reducing request payload:

```
Request_payload_stateful < Request_payload_stateless
```

But the server has to replicate or synchronize sessions, which can introduce infrastructure complexity.

### Security in Transit  
Encryption is crucial to protect sensitive data. HTTPS (HTTP over TLS) ensures confidentiality and integrity. API keys, OAuth tokens, or other credentials typically go in headers. If the app is stateful, the server might store session IDs in cookies, while stateless designs often pass tokens (like JWT) with each request.

#### Example: Passing a Bearer Token  
```bash
curl -X GET \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  https://api.example.com/data
```

- The client includes a JWT in the `Authorization` header for each request.  
- The server verifies the token without storing session info (stateless) or might keep session claims in memory or a database (stateful).

### Compression and Chunking  
Compressing large responses can save bandwidth and speed up response times. The server can automatically compress data if the client’s `Accept-Encoding` header indicates support:

```text
Accept-Encoding: gzip, deflate, br
```

Chunked transfer encoding can break large responses into smaller pieces, so the client begins processing data before the entire payload arrives. This approach benefits streaming data but can complicate stateful logic if partial updates must be tracked.

### Caching Layers  
Caching can dramatically reduce data transmission by serving responses directly from a cache instead of re-fetching. HTTP headers (e.g., `Cache-Control`, `ETag`) can guide caching decisions. Even in a stateful setup, certain resources may not depend on session state and can be cached easily.

```
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

If the requested data hasn’t changed, the proxy returns the cached copy without reaching the server. This design often helps with static resources or read-heavy endpoints.

### Example Requests in Different Formats  

#### JSON-based REST  
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"userId":123,"action":"login"}' \
  https://example.com/api/login
```
- The server returns a JSON response with login status.  
- Session tokens might be included in a cookie or an authorization header.  

#### GraphQL  
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
        "query": "query { user(id: 123) { name, status } }"
      }' \
  https://example.com/graphql
```
- The request includes the query in JSON form.  
- GraphQL can reduce data transfer by returning only the requested fields.  

#### gRPC with Protobuf  
```bash
grpcurl \
  -d '{"id":"123"}' \
  -plaintext \
  localhost:50051 bookstore.Bookstore/GetBook
```
- The client transmits a protobuf message.  
- The server responds in a compact binary format.
