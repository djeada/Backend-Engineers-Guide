## HTTP

Hypertext Transfer Protocol, or **HTTP**, is the foundational communication protocol of the World Wide Web. It defines how clients and servers exchange messages, how requests are structured, and how responses are returned. A client might be a browser, mobile app, command-line tool, or backend service. A server might be a website, REST API, GraphQL API, file server, or reverse proxy.

HTTP was originally designed for fetching hypertext documents such as HTML pages, but it now transports many kinds of data, including JSON, XML, images, videos, files, and API responses. Modern backend systems rely heavily on HTTP because it is simple, widely supported, and flexible enough for many communication patterns.

HTTP usually follows a **client-server request-response model**. The client sends a request, the server processes it, and the server returns a response. HTTP itself is stateless, meaning each request is independent unless the application adds state through cookies, sessions, tokens, or other mechanisms.

---

### Historical Context and Versions

HTTP began as a simple protocol for retrieving documents from web servers. Early versions were minimal and focused mainly on transferring basic HTML pages. Over time, HTTP evolved to support persistent connections, better caching, compression, multiplexing, security, and improved performance.

Each major HTTP version was created to solve limitations in earlier versions. HTTP/1.1 improved connection reuse and caching. HTTP/2 improved performance by allowing multiple streams over a single connection. HTTP/3 changed the transport layer by using QUIC over UDP instead of TCP.

* **HTTP/0.9 and HTTP/1.0**: Early forms of HTTP. They generally used one request per TCP connection and had limited support for persistent connections.
* **HTTP/1.1**: Introduced persistent connections by default, chunked transfer encoding, caching directives, and improved header handling.
* **HTTP/2**: Added multiplexing, header compression, and binary framing to improve performance.
* **HTTP/3**: Uses QUIC over UDP to reduce latency and improve behavior when packet loss occurs.

```text
          Timeline
     HTTP/0.9  ----> HTTP/1.0  ----> HTTP/1.1  ----> HTTP/2  ----> HTTP/3
        ^               ^            (Chunking,        ^         (QUIC)
        |               |            persistent         |
        |               |            connections)       |
        |               |                              (Multiplexing,
        |               |                              header compression)
        |               |
      Early Web    Basic request/response model
```

Example version comparison output:

```json
{
  "HTTP/1.1": {
    "connectionReuse": true,
    "multiplexing": false,
    "transport": "TCP"
  },
  "HTTP/2": {
    "connectionReuse": true,
    "multiplexing": true,
    "transport": "TCP"
  },
  "HTTP/3": {
    "connectionReuse": true,
    "multiplexing": true,
    "transport": "QUIC over UDP"
  }
}
```

This comparison shows how HTTP has evolved from simple request-response behavior into a more efficient protocol family that supports modern web and API workloads.

---

### Core HTTP Concepts

HTTP is based on a simple request-response cycle. A client sends a request message to a server. The server reads the request, determines what resource or action is being requested, runs the necessary application logic, and returns a response message.

A request usually includes a method, path, headers, and sometimes a body. A response usually includes a status code, headers, and sometimes a body. The response body might contain HTML, JSON, XML, binary data, or another content type.

HTTP is stateless by design. This means the protocol does not automatically remember earlier requests. However, applications can build stateful behavior using cookies, sessions, JWTs, or database-backed user records.

---

#### Request-Response Lifecycle

The request-response lifecycle shows the typical path of an HTTP exchange. Before the HTTP request is sent, the client may need to establish a TCP connection and negotiate TLS if HTTPS is being used.

```text
 Client (Browser/App)                      Server (HTTP Listener)
          |                                             |
   1. TCP handshake if needed (and TLS if HTTPS)        |
          |                                             |
          | 2. HTTP Request (Method, Path, Headers, Body)
          |--------------------------------------------->|
          |                                             |
          |                  3. Process Request          |
          |                    Locate Resource           |
          |                    Possibly query DB         |
          |                                             |
          | 4. HTTP Response (Status Code, Headers, Body)
          |<---------------------------------------------|
          |                                             |
          |                5. Client reads response      |
```

Example request:

```http
GET /api/posts/1 HTTP/1.1
Host: api.example.com
Accept: application/json
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "title": "Understanding HTTP",
  "status": "published"
}
```

In this example, the client requests one post from the server. The server returns a `200 OK` status and a JSON response body. The client can then parse the JSON and display the post.

When HTTPS is used, the HTTP data is encrypted inside a TLS-protected connection. This prevents attackers from easily reading or modifying the request and response while they travel across the network.

---

### HTTP Request Structure

An HTTP request includes a **start-line**, zero or more headers, and an optional message body. The start-line tells the server what action the client wants to perform and which resource is being targeted.

The general HTTP/1.1 request layout looks like this:

```text
Method SP Request-URI SP HTTP-Version CRLF
Header1: Value1 CRLF
Header2: Value2 CRLF
...
HeaderN: ValueN CRLF
CRLF
[Optional Message Body]
```

* **Method**: Indicates the action, such as `GET`, `POST`, `PUT`, or `DELETE`.
* **Request-URI**: Identifies the target resource, such as `/index.html` or `/api/users/1`.
* **HTTP-Version**: Indicates the protocol version, such as `HTTP/1.1`.
* **Headers**: Provide metadata such as host, content type, accepted formats, authentication, and caching preferences.
* **Body**: Optional data sent with the request, often used with methods like `POST`, `PUT`, and `PATCH`.

---

#### Example HTTP/1.1 GET Request

```http
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Connection: keep-alive
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 84
Connection: keep-alive

<html>
  <body>
    <h1>Welcome to example.com</h1>
  </body>
</html>
```

In this request, the client asks for `/index.html` from `www.example.com`. The `Accept: text/html` header tells the server that the client prefers an HTML response. The `Connection: keep-alive` header indicates that the client would like to reuse the connection for future requests.

A `GET` request usually does not include a body. It is mainly used to retrieve information from the server.

---

### HTTP Response Structure

An HTTP response includes a **status line**, headers, and an optional body. The status line tells the client whether the request succeeded, failed, redirected, or requires some other action.

The general HTTP/1.1 response layout looks like this:

```text
HTTP-Version SP Status-Code SP Reason-Phrase CRLF
Header1: Value1 CRLF
Header2: Value2 CRLF
...
HeaderN: ValueN CRLF
CRLF
[Optional Message Body]
```

The status code is especially important because it gives the client a quick summary of the outcome. For example, `200` means success, `404` means the resource was not found, and `500` means the server encountered an internal error.

---

#### Example HTTP/1.1 Response

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 129
Connection: keep-alive

<html>
  <head>
    <title>Hello World</title>
  </head>
  <body>
    This is a minimal HTML response.
  </body>
</html>
```

Example output interpretation:

```json
{
  "statusCode": 200,
  "meaning": "The request succeeded.",
  "contentType": "text/html",
  "connection": "keep-alive"
}
```

The server indicates that the request succeeded with `200 OK`. The `Content-Type` header tells the client that the body contains HTML. The `Content-Length` header tells the client how many bytes are in the response body.

If the resource does not exist, the server might return a different response:

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "Resource not found"
}
```

This tells the client that the server understood the request, but no matching resource was found.

---

### Common HTTP Methods

HTTP methods describe the intended action for the target resource. APIs use methods to make interactions more predictable. For example, `GET` usually retrieves data, while `POST` usually submits data or creates something new.

1. **GET**: Retrieves a resource. Usually does not include a request body.
2. **POST**: Sends data to the server, often creating a new resource or triggering an action.
3. **PUT**: Replaces a resource entirely with the request payload.
4. **DELETE**: Removes the specified resource.
5. **HEAD**: Like `GET`, but returns only headers and no response body.
6. **OPTIONS**: Asks the server which methods or options are available.
7. **PATCH**: Partially modifies a resource.

```text
GET /resource        -> Requests resource
POST /resource       -> Sends data to create or modify resource
PUT /resource        -> Replaces resource
PATCH /resource      -> Modifies partially
DELETE /resource     -> Deletes resource
```

Example method outputs:

```http
GET /posts/1
```

```json
{
  "id": 1,
  "title": "Existing Post"
}
```

```http
POST /posts
Content-Type: application/json

{
  "title": "New Post"
}
```

```json
{
  "id": 2,
  "title": "New Post",
  "status": "created"
}
```

```http
DELETE /posts/2
```

```http
HTTP/1.1 204 No Content
```

These examples show how the method communicates the client’s intent. The same resource path can behave differently depending on the HTTP method used.

---

### HTTP Status Codes

HTTP status codes tell the client what happened to the request. The first digit indicates the general category of the response.

* **1xx Informational**: The request was received and processing is continuing.
* **2xx Successful**: The request succeeded.
* **3xx Redirection**: The client needs to take further action, often by following another URL.
* **4xx Client Error**: The request has a problem, such as invalid syntax or missing permissions.
* **5xx Server Error**: The server failed while trying to process a valid request.

| Code | Meaning               |
| ---: | --------------------- |
|  200 | OK                    |
|  201 | Created               |
|  301 | Moved Permanently     |
|  302 | Found                 |
|  400 | Bad Request           |
|  401 | Unauthorized          |
|  403 | Forbidden             |
|  404 | Not Found             |
|  500 | Internal Server Error |
|  503 | Service Unavailable   |

Example success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success"
}
```

Example client error response:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Missing required field: email"
}
```

Example server error response:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Unexpected server error"
}
```

Clients should use status codes to decide what to do next. A `400` response usually means the client should fix the request. A `500` response usually means something went wrong on the server side.

---

### Headers and Caching

HTTP headers carry metadata about the request or response. Request headers can describe what the client accepts, who the client is, what credentials are being sent, or what cached version the client already has. Response headers can describe the returned content, caching rules, security policies, cookies, and server behavior.

Examples of request headers include `Accept`, `Authorization`, `User-Agent`, and `If-None-Match`. Examples of response headers include `Content-Type`, `Cache-Control`, `ETag`, `Set-Cookie`, and `Content-Encoding`.

Caching is one of the most important uses of HTTP headers. Proper caching can reduce latency, save bandwidth, and lower server load.

---

#### Example of Caching Control

`Cache-Control` tells clients and proxies how long a response can be reused.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=3600

{
  "id": 1,
  "title": "Cacheable Post"
}
```

Example output interpretation:

```json
{
  "cacheable": true,
  "maxAgeSeconds": 3600,
  "meaning": "The response may be reused for up to one hour."
}
```

`ETag` provides a version identifier for a resource. The client can later send `If-None-Match` to ask the server whether the resource has changed.

Example first response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "post-1-v1"

{
  "id": 1,
  "title": "Hello"
}
```

Example later request:

```http
GET /posts/1 HTTP/1.1
Host: api.example.com
If-None-Match: "post-1-v1"
```

Example output:

```http
HTTP/1.1 304 Not Modified
ETag: "post-1-v1"
```

The `304 Not Modified` response tells the client that its cached copy is still valid, so the server does not need to send the full response body again.

A formula for effective load reduction might be:

```text
Effective_Load = Original_Load * (1 - Cache_Hit_Rate)
```

Example calculation:

```text
Original_Load = 10,000 requests
Cache_Hit_Rate = 0.70

Effective_Load = 10,000 * (1 - 0.70)
Effective_Load = 3,000 requests
```

Example output:

```text
Only 3,000 requests reach the origin server when the cache hit rate is 70%.
```

This shows why caching can be so valuable for high-traffic APIs and websites.

---

### Keep-Alive and Persistent Connections

Before persistent connections became common, each HTTP request often required a new TCP connection. Opening a TCP connection takes time because it requires a handshake. If HTTPS is used, a TLS handshake may also be needed.

HTTP/1.1 introduced persistent connections by default. This allows multiple requests and responses to reuse the same TCP connection. Reusing connections reduces latency and connection overhead.

```text
Client (HTTP/1.1)        Server
     |    (Open TCP Connection)  
     |---- GET /page1 ---------->  
     |<--- 200 OK  --------------  
     |---- GET /page2 ---------->  
     |<--- 200 OK  --------------  
     |    (Close TCP Connection)
```

Example request:

```http
GET /page1 HTTP/1.1
Host: example.com
Connection: keep-alive
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Connection: keep-alive

<html>Page 1</html>
```

Example second request over the same connection:

```http
GET /page2 HTTP/1.1
Host: example.com
Connection: keep-alive
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Connection: keep-alive

<html>Page 2</html>
```

If the client or server wants to close the connection after the current exchange, it can use:

```http
Connection: close
```

Persistent connections improve performance because the cost of connection setup is spread across multiple requests.

---

### Chunked Transfer Encoding

Sometimes a server cannot know the final response size before it starts sending data. This can happen when the response is generated dynamically, streamed from another source, or produced gradually.

Chunked transfer encoding allows the server to send the response in pieces. Each chunk begins with its size, followed by the chunk data. A final chunk of size `0` indicates the end of the response.

```http
HTTP/1.1 200 OK
Transfer-Encoding: chunked

4
Wiki
5
pedia
0
```

Example reconstructed output:

```text
Wikipedia
```

In this example, the server sends two chunks: `"Wiki"` and `"pedia"`. The client combines them into the final response body, `"Wikipedia"`.

Chunked transfer is useful for streaming data or dynamically generated responses. The client can begin receiving data before the server has finished generating the entire response.

---

### HTTP/2: Multiplexing and Performance

HTTP/2 introduced a binary framing layer that allows multiple request-response streams to share one TCP connection. This is called **multiplexing**. It reduces the need to open many separate connections and helps make better use of a single connection.

HTTP/2 also includes header compression, which reduces repeated header overhead. This is useful because HTTP headers can become large, especially when cookies, authorization headers, and custom metadata are included.

Key HTTP/2 features include:

1. **Multiplexing**: Multiple streams can be active on one connection.
2. **Header Compression**: Repeated headers are compressed to reduce overhead.
3. **Server Push**: The server can proactively send resources it expects the client to need.

```text
   HTTP/2 Connection (Single TCP)
   +----------+----------+----------+
   | Stream 1 | Stream 3 | Stream 5 |   -- streams can be interleaved
   |          |          |          |
   +----------+----------+----------+
   | Stream 2 | Stream 4 | Stream 6 |   -- data frames arrive in any order
   +----------+----------+----------+
```

Example conceptual output:

```json
{
  "connection": "single TCP connection",
  "streams": [
    { "id": 1, "request": "/index.html", "status": 200 },
    { "id": 3, "request": "/styles.css", "status": 200 },
    { "id": 5, "request": "/app.js", "status": 200 }
  ]
}
```

HTTP/2 reduces much of the application-layer blocking found in older HTTP/1.1 patterns. However, because HTTP/2 still runs over TCP, packet loss at the TCP layer can affect all streams sharing that connection.

---

### HTTP/3: QUIC Protocol

HTTP/3 uses QUIC instead of TCP. QUIC runs over UDP and includes transport-level features such as encryption, congestion control, stream multiplexing, and improved recovery from packet loss.

The main advantage of HTTP/3 is that independent streams can recover from packet loss without blocking all other streams in the same way TCP-based multiplexing can. This can improve performance on unreliable networks, such as mobile or high-latency connections.

Example conceptual flow:

```text
HTTP/3 over QUIC
├── Stream 1: /index.html
├── Stream 2: /style.css
└── Stream 3: /app.js

Packet loss on Stream 2 does not fully block Stream 1 and Stream 3.
```

Example output:

```json
{
  "protocol": "HTTP/3",
  "transport": "QUIC over UDP",
  "benefits": [
    "Lower connection setup latency",
    "Improved packet loss recovery",
    "Independent stream handling"
  ]
}
```

HTTP/3 is designed to improve performance in modern network conditions. From an API design perspective, the request and response model remains familiar, but the underlying transport behaves differently.

---

### Security with HTTPS and TLS

HTTPS is HTTP over TLS. TLS provides encryption, authentication, and integrity. Encryption helps prevent attackers from reading sensitive data. Authentication helps clients verify they are communicating with the correct server. Integrity helps detect tampering.

Most production APIs and websites should use HTTPS. This is especially important for login forms, payment data, personal information, API tokens, cookies, and private user data.

```text
Client                             Server
   |-- TCP 3-Way Handshake --------->|
   |<-------------------------------|
   |-- TLS Handshake (Key Exchange)->|
   |<-------------------------------|
   |-- HTTP Request (Encrypted) ---->|
   |<-- HTTP Response (Encrypted) --|
```

Example HTTPS request at the application level:

```http
GET /account HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Example output:

```json
{
  "accountId": "acct_123",
  "user": "Alice",
  "status": "active"
}
```

Although the request and response look readable in application code, they are encrypted while traveling across the network. This protects the user’s account data and authorization token from being exposed in transit.

---

### HTTP Performance and Capacity

HTTP performance depends on many factors, including connection reuse, request size, response size, server processing time, database latency, caching, compression, concurrency, and network conditions.

A useful mental model is to separate concurrency from throughput:

```text
Max_In_Flight_Requests ≈ Available_Workers
Throughput ≈ Max_In_Flight_Requests / Avg_Request_Processing_Time
```

Example calculation:

```text
Available_Workers = 200
Avg_Request_Processing_Time = 0.1 seconds

Throughput ≈ 200 / 0.1
Throughput ≈ 2,000 requests per second
```

Example output:

```text
Estimated throughput: 2,000 requests per second
```

This formula is simplified, but it shows the basic relationship. If each request takes longer, throughput drops. If the system can handle more concurrent work efficiently, throughput can increase.

Non-blocking I/O, connection pooling, caching, database optimization, and horizontal scaling can all improve performance. Administrators often monitor requests per second, error rates, p95 latency, p99 latency, CPU usage, memory usage, and connection counts.

Example monitoring output:

```json
{
  "requestsPerSecond": 1850,
  "p95LatencyMs": 120,
  "p99LatencyMs": 280,
  "errorRate": "0.4%",
  "activeConnections": 430
}
```

This kind of data helps teams detect slow endpoints, overloaded servers, or failing dependencies.

---

### Timeouts, Retries, and Idempotency

Real HTTP systems need clear failure-handling policies. Networks fail, servers become overloaded, and downstream dependencies can become slow. Without timeouts and retry strategies, one slow service can cause a chain reaction of delays.

* **Timeouts** prevent clients from waiting forever.
* **Retries with backoff** help recover from temporary failures.
* **Idempotency** helps make retries safer, especially for write operations.

A `GET` request is usually safe to retry because it normally only retrieves data. A `POST` request may create something new, so retrying it without protection could create duplicates. Idempotency keys help the server recognize repeated attempts as the same operation.

Example request with timeout concept:

```text
Client timeout: 2 seconds
Request: GET /inventory/book-1
Result: fail if no response arrives within 2 seconds
```

Example timeout output:

```json
{
  "error": "Request timed out",
  "code": "TIMEOUT"
}
```

Example idempotent write request:

```http
POST /orders HTTP/1.1
Host: api.example.com
Idempotency-Key: order-abc123
Content-Type: application/json

{
  "productId": "book-1",
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

This prevents duplicate orders when a client retries after a timeout or temporary network failure.

---

### Example Usage with curl

`curl` is a common command-line tool for testing HTTP requests. It can send different methods, headers, and request bodies, making it useful for debugging APIs.

---

### GET Request

```bash
curl -X GET http://example.com
```

Example output:

```html
<html>
  <head><title>Example Domain</title></head>
  <body>Example website content.</body>
</html>
```

Explanation: The server returns an HTML page. The status code is typically `200 OK` if the request succeeds. A `GET` request is used to retrieve data without modifying server state.

---

#### POST with JSON Data

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"username":"alice","password":"secret"}' \
http://example.com/login
```

Example output:

```json
{
  "status": "logged_in",
  "session": "abc123"
}
```

Explanation: The client sends JSON data to the server. The `Content-Type: application/json` header tells the server how to interpret the request body. If the login succeeds, the response may include session information, a token, or a cookie.

---

#### HEAD Request

```bash
curl -I http://example.com/index.html
```

Example output:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 128
Last-Modified: Sat, 25 Apr 2026 10:00:00 GMT
```

Explanation: A `HEAD` request returns headers without the response body. This is useful for checking whether a resource exists, how large it is, what type it is, or when it was last modified.

---

### Best Practices and Modern Patterns

Good HTTP API design focuses on security, performance, reliability, and clarity. Even though HTTP is simple at its core, production systems need careful handling of headers, caching, retries, compression, and observability.

1. Use **HTTPS** to secure data in transit.
2. Employ **caching headers** such as `Cache-Control` and `ETag` to reduce bandwidth and latency.
3. Prefer **HTTP/2** or **HTTP/3** in modern environments for multiplexing and better performance.
4. Use **content negotiation** with `Accept` headers when serving multiple response formats.
5. Monitor logs and metrics such as status codes, latency, and error rates.
6. Implement structured **rate limiting** or **throttling** to protect against excessive requests.
7. Keep payloads minimal and use **gzip or Brotli** compression for large responses.

Example best-practice response headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=300
ETag: "users-v1"
Content-Encoding: br
Strict-Transport-Security: max-age=31536000
X-Request-ID: req-123
```

Example output:

```json
{
  "status": "success",
  "requestId": "req-123",
  "data": {
    "message": "Response returned securely and efficiently."
  }
}
```

These headers support caching, compression, security, and traceability. Together, they make HTTP APIs easier to operate, debug, and scale.
