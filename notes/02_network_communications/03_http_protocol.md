## HTTP  
Hypertext Transfer Protocol (HTTP) is the foundational communication protocol of the World Wide Web. It follows a client-server model and defines how messages are formatted and transmitted, as well as how servers and clients respond to various commands. HTTP was originally designed for fetching hypertext documents (HTML), but it has since evolved to transport data of all types across the internet. These notes explore the structure of HTTP requests and responses, its key features, common headers, methods, status codes, and how modern versions like HTTP/2 and HTTP/3 address performance challenges.

### Historical Context and Versions  
HTTP began with simple, stateless transactions. Over time, improvements tackled performance and scalability bottlenecks:

- **HTTP/0.9 and 1.0**: Earliest forms, one request per TCP connection, no persistent connections by default.  
- **HTTP/1.1**: Introduced persistent connections, chunked transfer encoding, caching directives, and more robust header management.  
- **HTTP/2**: Added multiplexing (multiple concurrent requests over one TCP connection), header compression, and server push.  
- **HTTP/3**: Replaces TCP with QUIC, operating over UDP for improved latency and loss recovery.

```
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

### Core HTTP Concepts  
HTTP is based on a simple request-response cycle. The client (often a browser or API consumer) sends a request message. The server processes the request, locates the resource, and replies with a response message. The protocol focuses on a stateless model, although applications can implement sessions and maintain state through cookies or other mechanisms.

#### Request-Response Lifecycle  
The diagram below presents an overview of the typical sequence:

```
 Client (Browser/App)                      Server (HTTP Listener)
          |                                             |
   1. TCP handshake if needed (and TLS if HTTPS)        |
          |                                             |
          | 2. HTTP Request (Method, Path, Headers, Body)
          |--------------------------------------------->|
          |                                             |
          |                  3. Process Request          |
          |                    Locate Resource            |
          |                    Possibly query DB          |
          |                                             |
          | 4. HTTP Response (Status Code, Headers, Body)
          |<---------------------------------------------|
          |                                             |
          |                5. Client reads response      |
```

When using HTTPS, a TLS handshake encrypts the channel, preserving confidentiality and integrity. Once the connection is established, the client issues HTTP requests and the server responds.

### HTTP Request Structure  
A request includes a start-line, zero or more headers, and an optional body. The start-line contains the HTTP method, the target resource, and the HTTP version. Here is the general layout:

```
Method SP Request-URI SP HTTP-Version CRLF
Header1: Value1 CRLF
Header2: Value2 CRLF
...
HeaderN: ValueN CRLF
CRLF
[Optional Message Body]
```

- **Method**: Indicates the action (GET, POST, PUT, etc.).  
- **Request-URI**: The path or resource identifier on the server.  
- **HTTP-Version**: Commonly HTTP/1.1 or HTTP/2.  

#### Example HTTP/1.1 GET Request  
```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Connection: keep-alive

```

In this request, the client is fetching `/index.html` from `www.example.com`, specifying that it prefers HTML, and requesting a persistent (keep-alive) connection.

### HTTP Response Structure  
A response includes a status line, headers, and an optional body. The status line has the HTTP version, a status code, and a textual reason phrase.

```
HTTP-Version SP Status-Code SP Reason-Phrase CRLF
Header1: Value1 CRLF
Header2: Value2 CRLF
...
HeaderN: ValueN CRLF
CRLF
[Optional Message Body]
```

#### Example HTTP/1.1 Response  
```
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

The server indicates a successful 200 status, includes the content type and length, and provides an HTML body. If the resource doesn’t exist, the server might respond with `HTTP/1.1 404 Not Found`.

### Common HTTP Methods  
These methods describe intended actions on the resource:

1. **GET**: Retrieve a resource. Typically has no request body.  
2. **POST**: Submit data to the server, often causing state changes (e.g., form submission).  
3. **PUT**: Replace a resource entirely with the request payload.  
4. **DELETE**: Remove the specified resource.  
5. **HEAD**: Identical to GET but returns no body. Useful for checking resource headers.  
6. **OPTIONS**: Inquires about communication options available on the server.  
7. **PATCH**: Partial modification of a resource.

```
   GET /resource        -> Requests resource
   POST /resource       -> Sends data to create or modify resource
   PUT /resource        -> Replaces resource
   PATCH /resource      -> Modifies partially
   DELETE /resource     -> Deletes resource
```

### HTTP Status Codes  
Status codes convey the outcome of the request. The first digit indicates the category:

- 1xx (Informational): The request was received; the process is continuing.  
- 2xx (Successful): The action was successfully received, understood, and accepted.  
- 3xx (Redirection): Further action must be taken to complete the request.  
- 4xx (Client Error): The client seems to have erred (e.g., 400 Bad Request, 404 Not Found).  
- 5xx (Server Error): The server failed to fulfill an apparently valid request (e.g., 500 Internal Server Error).

A sample table for commonly encountered codes:

| Code | Meaning               |
|------|-----------------------|
| 200  | OK                    |
| 201  | Created               |
| 301  | Moved Permanently     |
| 302  | Found                 |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 500  | Internal Server Error |
| 503  | Service Unavailable   |

### Headers and Caching  
HTTP headers convey additional information. They control caching, content negotiation, security, and more. Two major categories are request headers (e.g., `Accept`, `Authorization`) and response headers (e.g., `Content-Type`, `Cache-Control`).  

#### Example of Caching Control  
1. **Cache-Control**: `Cache-Control: max-age=3600` instructs clients and proxies to reuse this response for up to 3600 seconds.  
2. **ETag**: A unique identifier for a resource. Clients can use `If-None-Match` to perform conditional requests, retrieving the resource only if it has changed.  

Caching can greatly reduce latency and network load. A formula for effective load reduction might be:

```
Effective_Load = Original_Load * (1 - Cache_Hit_Rate)
```

where `Cache_Hit_Rate` is the fraction of requests served from the cache.

### Keep-Alive and Persistent Connections  
Before HTTP/1.1, each request required a separate TCP connection. HTTP/1.1 introduced persistent connections by default, meaning multiple requests/responses can share one TCP session. This lowers connection overhead and improves performance.

```
Client (HTTP/1.1)        Server
     |    (Open TCP Connection)  
     |---- GET /page1 ---------->  
     |<--- 200 OK  --------------  
     |---- GET /page2 ---------->  
     |<--- 200 OK  --------------  
     |    (Close TCP Connection)
```

In older or incompatible scenarios, the `Connection: close` header indicates the connection should drop after the current request/response.

### Chunked Transfer Encoding  
When a server cannot know the final content length in advance, it can send the response in chunks. The server sends the size of each chunk, followed by the chunk data:

```
HTTP/1.1 200 OK
Transfer-Encoding: chunked

4
Wiki
5
pedia
0

```

In this example, the response is broken into two chunks, "Wiki" (4 bytes) and "pedia" (5 bytes). A final size of `0` indicates the end of chunks.

### HTTP/2: Multiplexing and Performance  
HTTP/2 introduced a binary framing layer, allowing multiple request-response exchanges (streams) to occur simultaneously over a single TCP connection. This solves the head-of-line blocking problem in HTTP/1.1. Features include:

1. **Multiplexing**: Multiple streams of data interleave on one connection.  
2. **Header Compression**: Reduces overhead from verbose headers.  
3. **Server Push**: The server can proactively send resources it anticipates the client will need.

An outline of HTTP/2 multiplexing:

```
   HTTP/2 Connection (Single TCP)
   +----------+----------+----------+
   | Stream 1 | Stream 3 | Stream 5 |   -- streams can be interleaved
   |          |          |          |
   +----------+----------+----------+
   | Stream 2 | Stream 4 | Stream 6 |   -- data frames arrive in any order
   +----------+----------+----------+
```

### HTTP/3: QUIC Protocol  
HTTP/3 leverages QUIC, which uses UDP with built-in encryption and independent streams. It avoids TCP’s head-of-line blocking at the transport level and can recover more gracefully from packet loss. While still emerging, HTTP/3 aims to further reduce latency and connection setup times.

### Security with HTTPS and TLS  
Transport Layer Security (TLS) provides encryption, authentication, and data integrity for HTTP connections (known as HTTPS). The client and server perform a TLS handshake to negotiate cipher suites and exchange keys. This secures the data from eavesdropping or tampering.

```
Client                             Server
   |-- TCP 3-Way Handshake --------->|
   |<-------------------------------|
   |-- TLS Handshake (Key Exchange)->|
   |<-------------------------------|
   |-- HTTP Request (Encrypted) ---->|
   |<-- HTTP Response (Encrypted) --|
```

### HTTP Performance and Capacity  
A simplified concurrency formula for an HTTP server could be:

```
Max_Concurrent = (Threads or Connections) / (Avg_Request_Processing_Time)
```

If each request blocks one thread for the entire processing time, the maximum concurrency is limited. Non-blocking I/O or event-driven models can help scale better. Administrators often examine requests per second (RPS), throughput, and tail latencies (p95, p99) to gauge performance.

### Example Usage with curl  
Here are some basic commands demonstrating HTTP operations. Each example is followed by sample output and a short explanation.

### GET Request  
```bash
curl -X GET http://example.com
```
Example output:
```
<html>
  <head><title>Example Domain</title></head>
  <body>Example website content.</body>
</html>
```
Explanation: The server returns an HTML page; status code is typically 200 OK.

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
Explanation: The server processes JSON input. Response includes session details if the login succeeded.

#### HEAD Request  
```bash
curl -I http://example.com/index.html
```
Example output:
```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 128
```
Explanation: The server returns only headers (no body). This is useful for verifying resource existence or last-modified time.

### Best Practices and Modern Patterns  
1. Use **HTTPS** to secure data in transit.  
2. Employ **caching headers** (Cache-Control, ETag) to reduce bandwidth and latency.  
3. Prefer **HTTP/2** or **HTTP/3** in modern environments for multiplexing and better performance.  
4. Utilize **content negotiation** (Accept headers) for serving different resource representations.  
5. Monitor logs and metrics (status codes, latencies, error rates) to detect anomalies.  
6. Implement structured **rate limiting** or **throttling** to protect from excessive requests.  
7. Keep payloads minimal and use **gzip or Brotli** compression for large responses.
