## gRPC  
gRPC is a high-performance open-source framework that was developed at Google for remote procedure calls. It uses the Protocol Buffers (protobuf) serialization format by default and runs over HTTP/2 to support features like full-duplex streaming and efficient compression. Many microservices architectures choose gRPC for its speed and type safety, enabling strong contracts between service providers and consumers.  

### Architecture Overview  
gRPC builds on the concept that a client can directly call methods on a server application as if it were a local object, with the communication details handled under the hood. It relies on protocol buffers to define data schemas (messages) and service endpoints (RPC methods). When a client calls a method, gRPC handles the transport details over HTTP/2, manages efficient binary serialization, and returns a strongly typed response.

```
+---------------------------+               +---------------------------+
|                           |               |                           |
|         gRPC Client       |               |         gRPC Server       |
|  (Desktop, Mobile, etc.)  |               | (Implements gRPC methods) |
+---------------------------+               +------------+--------------+
          |                                  ^           |
          | 1. Client calls gRPC method      |           |
          | (Unary, Streaming, etc.)         |           |
          v                                  |           |
+---------------------------+                |           |
|  HTTP/2 request with      |--------------->            |
|  protobuf-encoded data    |                            |
+---------------------------+                            |
                                                         |
        (Server processes request, prepares response)    |
                                                         |
+---------------------------+                            |
|  HTTP/2 response with     |<---------------------------|
|  protobuf-encoded data    |
+---------------------------+
          |
          | 2. Client decodes
          |    protobuf message
          v
+---------------------------+
|  Uses strong-typed data   |
|  in the application logic |
+---------------------------+
```

This diagram shows how the client calls a remote procedure, sends serialized data over HTTP/2, and receives a response in the same serialized format. The strong typing provided by protobuf ensures that both client and server agree on data structures before runtime.

### Core Concepts

gRPC is a framework for building APIs where clients call functions on a server as if they were local methods. Instead of designing many REST endpoints around resources, gRPC defines services and methods in a contract file. This contract describes the messages that clients and servers exchange and the operations that are available.

The foundation of gRPC is **Protocol Buffers**, often shortened to **Protobuf**. Protobuf defines the structure of the data and allows that data to be serialized into a compact binary format. This makes gRPC efficient for service-to-service communication, especially in systems where performance and strong contracts are important.

### Protocol Buffers (Protobuf)

Protocol Buffers is a language-neutral, platform-neutral, extensible mechanism for serializing structured data. This means the same `.proto` file can be used to generate code for different programming languages, such as Go, Java, Python, C#, JavaScript, or Kotlin.

In a `.proto` file, developers define **message types** and **services**. Message types describe the shape of the data being sent between client and server. Services describe the RPC methods that can be called. Code generation tools then produce client and server stubs in multiple languages based on these definitions.

A major benefit of Protobuf is that it creates a clear contract between systems. Both the client and server know exactly what fields are expected, what types those fields should have, and which methods are available. This reduces ambiguity and helps teams build APIs that are easier to maintain over time.

#### Service Definition

A service definition describes the RPC methods that can be invoked by a client. Each method specifies the request message type and the response message type. It also shows whether the method uses a single request and response or one of gRPC’s streaming patterns.

Here is a sample `.proto` file:

```proto
syntax = "proto3";

package bookstore;

// Message definitions
message Book {
  string id = 1;
  string title = 2;
  string author = 3;
}

message GetBookRequest {
  string id = 1;
}

message BookList {
  repeated Book books = 1;
}

// Service definition
service Bookstore {
  // Unary request/response
  rpc GetBook(GetBookRequest) returns (Book);

  // Server streaming
  rpc ListBooks(google.protobuf.Empty) returns (stream Book);

  // Client streaming
  rpc AddBooks(stream Book) returns (BookList);

  // Bidirectional streaming
  rpc Chat(stream Book) returns (stream Book);
}
```

Example unary request:

```json
{
  "id": "1"
}
```

Example unary response:

```json
{
  "id": "1",
  "title": "gRPC Fundamentals",
  "author": "Jane Smith"
}
```

This definition includes a `Bookstore` service with four RPC methods. The `GetBook` method is a unary RPC, meaning the client sends one request and receives one response. The `ListBooks` method is server streaming, meaning the server can return multiple `Book` messages over time. The `AddBooks` method is client streaming, where the client sends multiple books and receives one final response. The `Chat` method is bidirectional streaming, where both sides can send messages during the same connection.

The numbers assigned to each field, such as `string id = 1`, are field tags. These tags are used in the binary encoding and should be treated carefully once the API is in use. Changing or reusing field numbers can break compatibility between clients and servers.

#### Communication Modes

gRPC supports four primary communication patterns. These patterns make it flexible enough for simple request-response APIs as well as more advanced real-time or batch-style workflows.

A **unary RPC** is the simplest pattern. The client sends a single request, and the server sends a single response. This is useful for operations like fetching one book, creating one user, or checking the status of an order.

Example unary call:

```text
Client sends: GetBookRequest { id: "1" }
Server returns: Book { id: "1", title: "gRPC Fundamentals", author: "Jane Smith" }
```

A **server streaming RPC** starts with one request from the client, but the server responds with a stream of messages. This is useful when the server needs to send many results or send updates over time.

Example server streaming call:

```text
Client sends: ListBooksRequest
Server streams:
Book { id: "1", title: "gRPC Fundamentals", author: "Jane Smith" }
Book { id: "2", title: "Protobuf in Practice", author: "Alex Johnson" }
Book { id: "3", title: "Streaming APIs", author: "Mia Chen" }
```

A **client streaming RPC** allows the client to send multiple messages to the server. After the client finishes sending messages, the server returns a single response. This is useful for uploads, batch inserts, or collecting data before processing it.

Example client streaming call:

```text
Client streams:
Book { id: "1", title: "gRPC Fundamentals", author: "Jane Smith" }
Book { id: "2", title: "Protobuf in Practice", author: "Alex Johnson" }

Server returns:
BookList {
  books: [
    Book { id: "1", title: "gRPC Fundamentals", author: "Jane Smith" },
    Book { id: "2", title: "Protobuf in Practice", author: "Alex Johnson" }
  ]
}
```

A **bidirectional streaming RPC** allows both client and server to send messages independently over the same connection. The client and server can read and write at the same time until both sides are finished. This is useful for chat systems, live collaboration, multiplayer games, or real-time monitoring.

Example bidirectional streaming call:

```text
Client sends: Book { id: "1", title: "Draft Book", author: "Jane Smith" }
Server sends: Book { id: "1", title: "Draft Book - Received", author: "Jane Smith" }

Client sends: Book { id: "2", title: "Another Draft", author: "Alex Johnson" }
Server sends: Book { id: "2", title: "Another Draft - Received", author: "Alex Johnson" }
```

These communication modes are one reason gRPC is useful for internal microservices and real-time systems. Instead of forcing every interaction into a simple request-response pattern, gRPC supports both single-message and streaming workflows.

#### Code Generation

After defining a `.proto` file, developers use the Protocol Buffers compiler, usually called `protoc`, together with language-specific gRPC plugins. These tools generate source code from the schema so developers do not need to manually write low-level serialization code or networking stubs.

The generated code usually includes message classes or structs, client stubs, and server interfaces. On the client side, the generated stub provides methods that can be called like normal functions. On the server side, the generated interface defines the methods that the server must implement.

The following table summarizes some common `protoc` flags:

| Flag                     | Description                                                                |
| ------------------------ | -------------------------------------------------------------------------- |
| `--proto_path`           | Specifies directories in which to search for imports.                      |
| `--go_out`, `--java_out` | Generates language-specific source files, such as Go or Java message code. |
| `--go-grpc_out`          | Generates gRPC service interfaces in Go.                                   |
| `--grpc-java_out`        | Generates gRPC service stubs for Java.                                     |
| `--plugin`               | Allows specifying the path to the gRPC plugin for `protoc`.                |

As an example, running `protoc` for Go might look like this:

```bash
protoc --proto_path=. --go_out=. --go-grpc_out=. bookstore.proto
```

Example generated files:

```text
bookstore.pb.go
bookstore_grpc.pb.go
```

The `bookstore.pb.go` file usually contains the generated Protobuf message types, such as `Book`, `GetBookRequest`, and `BookList`. The `bookstore_grpc.pb.go` file usually contains the generated gRPC client and server interfaces for the `Bookstore` service.

After generation, a Go server would implement the generated service interface, while a Go client would use the generated client stub to call methods such as `GetBook`, `ListBooks`, `AddBooks`, or `Chat`.

This workflow keeps the API contract centralized in the `.proto` file. When the contract changes, developers regenerate the stubs and update the client or server code accordingly.

### Example Implementation in Go

A gRPC service implementation usually starts with the code generated from the `.proto` file. The generated code defines the service interface, request and response message types, and helper functions for registering the service with a gRPC server.

In this example, the `Bookstore` service is implemented in Go. The server exposes a `GetBook` method that accepts a `GetBookRequest` and returns a `Book`. To keep the example simple, the server does not connect to a real database. Instead, it returns a static book response using the ID provided in the request.

```go
package main

import (
    "context"
    "fmt"
    "net"

    "google.golang.org/grpc"
    pb "path/to/generated/bookstore"
)

type bookstoreServer struct {
    pb.UnimplementedBookstoreServer
}

func (s *bookstoreServer) GetBook(ctx context.Context, req *pb.GetBookRequest) (*pb.Book, error) {
    // For demonstration, returns a static book.
    return &pb.Book{
        Id:     req.GetId(),
        Title:  "A Sample Book",
        Author: "An Author",
    }, nil
}

func main() {
    listener, err := net.Listen("tcp", ":50051")
    if err != nil {
        fmt.Println("Failed to listen:", err)
        return
    }

    grpcServer := grpc.NewServer()
    pb.RegisterBookstoreServer(grpcServer, &bookstoreServer{})

    fmt.Println("gRPC server listening on port 50051...")
    if err := grpcServer.Serve(listener); err != nil {
        fmt.Println("Failed to serve:", err)
    }
}
```

Example terminal output when the server starts:

```text
gRPC server listening on port 50051...
```

In this example, `bookstoreServer` provides a `GetBook` method that satisfies the interface generated from the `.proto` file. The method receives a context and a request object. The request contains the book ID, which is accessed using `req.GetId()`.

The `main` function creates a TCP listener on port `50051`, creates a new gRPC server, and registers the `Bookstore` service implementation. Once `grpcServer.Serve(listener)` is called, the server begins listening for incoming gRPC requests.

If a client sends a request with the ID `"123"`, the server returns a `Book` response using that same ID:

```json
{
  "id": "123",
  "title": "A Sample Book",
  "author": "An Author"
}
```

This response matches the `Book` message defined in the `.proto` file. In a production system, the `GetBook` method would usually look up the book in a database, check permissions, handle missing records, and return an appropriate error if the book could not be found.

### Working with gRPC on the Command Line

Clients usually connect to a gRPC service using generated stubs in the same programming language as the application. For example, a Go client would use generated Go code, while a Java client would use generated Java code.

However, during development and testing, it is often useful to call a gRPC service directly from the command line. A popular tool for this is `grpcurl`. It works like `curl`, but for gRPC services. It lets developers send requests, inspect responses, and test methods without writing a full client application.

The following command calls the `GetBook` method on the local `Bookstore` service:

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

The response shows the book data returned by the server. The JSON output corresponds to the `Book` message defined in the `.proto` file. Although gRPC uses Protobuf internally, `grpcurl` allows the request and response to be written and displayed as JSON, which makes testing easier for humans.

The `-plaintext` option tells `grpcurl` to use an unencrypted connection. This is common for local testing, but production services usually use TLS. The `-d` flag provides the request body. In this example, the request body contains the book ID:

```json
{
  "id": "123"
}
```

The final part of the command identifies the service and method being called:

```text
bookstore.Bookstore/GetBook
```

Here, `bookstore` refers to the package name from the `.proto` file, `Bookstore` is the service name, and `GetBook` is the RPC method.

If the request is successful, the server returns the matching response message. If the method does not exist, the server is unavailable, or the request body does not match the expected schema, `grpcurl` will return an error message instead.

Example error output for an unavailable server:

```text
Failed to dial target host "localhost:50051": connection refused
```

This means no gRPC server is currently listening at `localhost:50051`, or the server failed to start.

### Performance Characteristics

A major reason teams choose gRPC is performance. gRPC uses HTTP/2, which supports multiplexing, streaming, header compression, and long-lived connections. These features can make gRPC efficient for service-to-service communication, especially in backend systems where many small requests happen frequently.

HTTP/2 multiplexing allows multiple requests and responses to share the same connection at the same time. This reduces the overhead of repeatedly opening new connections. Streaming also helps when large datasets need to be transferred gradually instead of all at once.

A simple way to think about server capacity is:

```text
Server capacity = total_threads / average_call_duration
```

Example calculation:

```text
total_threads = 100
average_call_duration = 0.05 seconds

Server capacity = 100 / 0.05
Server capacity = 2,000 calls per second
```

Example output:

```text
Estimated server capacity: 2,000 calls per second
```

This is only a simplified model, but it shows the basic relationship between concurrency and call duration. If each request finishes quickly, the server can handle more calls over time. If requests take longer, fewer calls can be processed with the same resources.

In practice, real server capacity depends on many factors, including CPU usage, memory, database performance, network latency, serialization cost, connection limits, and how much work each RPC method performs. A fast gRPC server can still become slow if each resolver or service method makes expensive database calls.

Streaming can improve performance when large responses are involved. Instead of waiting for the server to build one large response, the server can send data in smaller chunks.

Example server streaming output:

```json
{ "id": "1", "title": "gRPC Fundamentals", "author": "Jane Smith" }
{ "id": "2", "title": "Protobuf in Practice", "author": "Alex Johnson" }
{ "id": "3", "title": "Streaming APIs", "author": "Mia Chen" }
```

In this example, the client can begin processing books as they arrive instead of waiting for the entire list to be prepared. This is useful for large datasets, logs, notifications, live updates, and long-running operations.

gRPC is often a strong choice for internal microservices because it provides fast communication, strict contracts through `.proto` files, and support for multiple programming languages. However, it may require extra tooling when exposed directly to browsers or public clients, because standard browser APIs do not support all gRPC features as directly as backend clients do.

### Best Practices

Designing and operating gRPC services requires attention to structure, reliability, security, and observability. Because gRPC is often used for internal microservices, small design decisions can have a large impact when many services depend on one another.

A good gRPC service should have clear `.proto` definitions, predictable error handling, secure connections, reasonable timeouts, and strong monitoring. These practices help teams build services that are easier to maintain and safer to run in production.

Consider a few approaches when designing and operating gRPC services:

* Keep `.proto` definitions organized, preferably with smaller files that each handle a logical domain.
* Employ secure connections by using TLS in production environments to encrypt traffic on HTTP/2.
* Use deadlines or timeouts to prevent client calls from hanging indefinitely.
* Rely on load balancing strategies that are compatible with HTTP/2 and maintain persistent connections.
* Monitor service performance by collecting metrics on request latencies, error rates, and resource usage.

Example project structure:

```text
proto/
  bookstore/
    book.proto
    author.proto
    bookstore_service.proto
  users/
    user.proto
    user_service.proto
```

Example output from a monitoring dashboard:

```text
Bookstore/GetBook latency p95: 42ms
Bookstore/GetBook error rate: 0.3%
Bookstore/ListBooks active streams: 18
CPU usage: 61%
Memory usage: 512MB
```

This example shows how service definitions can be organized by domain. Instead of placing every message and service in one large `.proto` file, the API is split into smaller files for books, authors, users, and services. The monitoring output shows the type of operational data teams should collect to understand how the service behaves in production.

### Error Handling and Status Codes

gRPC uses its own standard status codes instead of relying only on HTTP status codes. Every RPC call finishes with a status. If the call succeeds, the status is `OK`. If the call fails, the status explains the general reason for failure.

These status codes help clients respond appropriately. For example, a client might retry a request when the service returns `UNAVAILABLE`, but it should not retry the same request when the server returns `INVALID_ARGUMENT`, because the request itself is wrong.

| Code               | Number | Description                                                  |
| ------------------ | -----: | ------------------------------------------------------------ |
| OK                 |      0 | The call succeeded                                           |
| CANCELLED          |      1 | The call was cancelled by the caller                         |
| UNKNOWN            |      2 | An unknown error occurred                                    |
| INVALID_ARGUMENT   |      3 | The client sent an invalid argument                          |
| DEADLINE_EXCEEDED  |      4 | The operation did not complete before the deadline           |
| NOT_FOUND          |      5 | The requested resource was not found                         |
| ALREADY_EXISTS     |      6 | The resource the client tried to create already exists       |
| PERMISSION_DENIED  |      7 | The caller does not have permission for this operation       |
| RESOURCE_EXHAUSTED |      8 | A resource limit has been reached, such as a rate limit      |
| UNIMPLEMENTED      |     12 | The method is not implemented on the server                  |
| INTERNAL           |     13 | An internal server error occurred                            |
| UNAVAILABLE        |     14 | The service is temporarily unavailable                       |
| UNAUTHENTICATED    |     16 | The caller has not provided valid authentication credentials |

Example Go error response:

```go
return nil, status.Error(codes.NotFound, "book not found")
```

Example client-side output:

```text
rpc error: code = NotFound desc = book not found
```

In this example, the server returns a `NOT_FOUND` status because the requested book does not exist. The client receives both a machine-readable status code and a human-readable message.

Servers attach a status code and an optional message to every response. Clients should handle these codes explicitly to provide meaningful error messages, decide whether to retry, or show the correct feedback to users.

For example, `UNAUTHENTICATED` usually means the client needs to provide valid credentials. `PERMISSION_DENIED` means the client may be authenticated but does not have permission to perform the operation. `DEADLINE_EXCEEDED` means the request took too long and was cancelled after the configured deadline.

### Deadlines and Timeouts

Every gRPC call should include a deadline or timeout. A deadline defines the point in time by which the call must complete. If the server does not respond before that deadline, the call fails with `DEADLINE_EXCEEDED`.

Deadlines are important because they prevent client calls from hanging indefinitely. Without deadlines, a slow or unavailable downstream service could cause requests to pile up, consume resources, and eventually affect other parts of the system.

Deadlines can also propagate across service boundaries. If a client calls Service A with a 5-second deadline, and Service A then calls Service B, the remaining time is passed along. This helps the entire request chain respect the original time budget.

```text
Client (deadline: 5s) → Service A (remaining: 4.8s) → Service B (remaining: 4.5s)
```

Example Go client with timeout:

```go
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

response, err := client.GetBook(ctx, &pb.GetBookRequest{Id: "1"})
```

Example output when the deadline is exceeded:

```text
rpc error: code = DeadlineExceeded desc = context deadline exceeded
```

In this example, the client gives the request two seconds to complete. If the server does not return a response within that time, the context is cancelled and the call fails with `DEADLINE_EXCEEDED`.

Setting appropriate deadlines prevents cascading failures and ensures that no single slow downstream service can block the entire request pipeline indefinitely. Deadlines should be long enough for normal operations to complete, but short enough to protect the system when something goes wrong.

### Metadata and Interceptors

gRPC metadata is similar to HTTP headers. Clients and servers can attach key-value pairs to RPC calls for purposes such as authentication, tracing, request identification, locale settings, or feature flags.

Metadata is commonly used to pass tokens or correlation IDs. For example, a client might send an authorization token so the server can verify the caller’s identity. It might also send a request ID so logs across multiple services can be connected.

```go
md := metadata.Pairs("authorization", "Bearer my-token")
ctx := metadata.NewOutgoingContext(context.Background(), md)
response, err := client.GetBook(ctx, &pb.GetBookRequest{Id: "1"})
```

Example metadata sent with the request:

```text
authorization: Bearer my-token
```

Example response:

```json
{
  "id": "1",
  "title": "A Sample Book",
  "author": "An Author"
}
```

In this example, the client adds an `authorization` value to the outgoing context. When the request reaches the server, server-side logic can read the metadata and validate the token before allowing the `GetBook` method to run.

Interceptors, also called middleware in some frameworks, are functions that run before or after RPC calls. They are useful for cross-cutting concerns such as logging, authentication, metrics collection, tracing, error handling, and request validation.

Both unary and streaming calls support interceptors. A unary interceptor for logging might look like this:

```go
func loggingInterceptor(
    ctx context.Context,
    req interface{},
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (interface{}, error) {
    log.Printf("Method: %s", info.FullMethod)
    resp, err := handler(ctx, req)
    log.Printf("Response error: %v", err)
    return resp, err
}
```

Example log output:

```text
Method: /bookstore.Bookstore/GetBook
Response error: <nil>
```

In this example, the interceptor logs the full method name before the RPC is handled. It then calls `handler(ctx, req)` to continue processing the request. After the handler returns, it logs whether an error occurred.

Interceptors keep repeated logic out of individual service methods. Instead of adding authentication or logging code to every RPC method, developers can place that logic in one interceptor and apply it consistently across the server.

### Health Checking

Health checking allows infrastructure to determine whether a gRPC service is ready to accept traffic. This is especially important in containerized environments where load balancers, orchestrators, and readiness probes need a reliable way to know whether a service is healthy.

gRPC provides a standardized health checking protocol defined in `grpc.health.v1`. Services can implement a `Health` service that exposes methods for checking current status or watching status changes over time.

```proto
service Health {
  rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
  rpc Watch(HealthCheckRequest) returns (stream HealthCheckResponse);
}

message HealthCheckResponse {
  enum ServingStatus {
    UNKNOWN = 0;
    SERVING = 1;
    NOT_SERVING = 2;
  }
  ServingStatus status = 1;
}
```

Example health check request:

```text
grpc.health.v1.Health/Check
```

Example output:

```json
{
  "status": "SERVING"
}
```

The `Check` method returns the current serving status. If the service returns `SERVING`, a load balancer or orchestrator can send traffic to it. If it returns `NOT_SERVING`, the service should usually be removed from active traffic until it recovers.

The `Watch` method streams status changes. This allows clients or infrastructure components to monitor health continuously instead of repeatedly polling the service.

Example status stream:

```text
SERVING
NOT_SERVING
SERVING
```

This means the service started healthy, became unavailable, and later recovered. In Kubernetes or similar environments, health checks help determine whether a container should receive traffic, be restarted, or be temporarily removed from service discovery.

Health checking is a small part of the API surface, but it is critical for reliable operations. A service that exposes a clear health status is easier to deploy, monitor, and recover when failures happen.

### gRPC vs REST

Choosing between gRPC and REST depends on the use case, the clients that will consume the API, and the performance requirements of the system. Both approaches allow services to communicate over a network, but they use different conventions and are often better suited to different environments.

REST is commonly used for public-facing APIs because it works naturally with browsers, HTTP tools, and JSON-based clients. It is easy to test with standard tools like `curl`, and its text-based payloads are simple for developers to inspect and debug.

gRPC is commonly used for internal service-to-service communication, especially in microservice architectures. It provides strong contracts through `.proto` files, efficient binary serialization with Protocol Buffers, and native support for streaming. These features make it a strong choice when performance, type safety, and consistent contracts are important.

| Aspect            | gRPC                                                      | REST                                                 |
| ----------------- | --------------------------------------------------------- | ---------------------------------------------------- |
| Transport         | HTTP/2                                                    | HTTP/1.1 or HTTP/2                                   |
| Data format       | Protocol Buffers, usually binary                          | JSON, XML, or other text-based formats               |
| Contract          | Strict `.proto` file                                      | Informal documentation or OpenAPI specification      |
| Streaming         | Native bidirectional streaming                            | Usually requires WebSockets or Server-Sent Events    |
| Browser support   | Limited without grpc-web or a proxy                       | Universal browser support                            |
| Code generation   | Built in from `.proto` definitions                        | Optional through OpenAPI generators                  |
| Performance       | Generally faster due to binary format and HTTP/2 features | Often slower due to text parsing and larger payloads |
| Human readability | Low because payloads are binary on the wire               | High because JSON is human-readable                  |
| Typical use case  | Internal microservices                                    | Public-facing APIs                                   |

Example gRPC-style operation:

```proto
service Bookstore {
  rpc GetBook(GetBookRequest) returns (Book);
}
```

Example request data:

```json
{
  "id": "1"
}
```

Example output:

```json
{
  "id": "1",
  "title": "A Sample Book",
  "author": "An Author"
}
```

In gRPC, the method is defined in the `.proto` contract. The client calls `GetBook` using generated code, and the request and response are serialized using Protocol Buffers. This gives both the client and server a shared understanding of the expected message types.

Example REST-style operation:

```http
GET /books/1
```

Example output:

```json
{
  "id": "1",
  "title": "A Sample Book",
  "author": "An Author"
}
```

In REST, the client uses an HTTP method and URL to request the resource. The response is commonly returned as JSON, which is easy to read, inspect, and debug using standard browser or command-line tools.

The choice often depends on who the API is for. If the API is mainly used by backend services controlled by the same organization, gRPC can be a strong option because of its speed, strict contracts, and streaming support. If the API is intended for browsers, third-party developers, mobile apps, or public integrations, REST is often easier to adopt because of its broad compatibility.

gRPC excels for internal service-to-service communication where performance matters and both ends share the `.proto` contract. REST remains a better choice for public APIs that need broad client compatibility, simple debugging, and human-readable payloads.
