## API communication protocols

API communication protocols describe how different software components exchange data and invoke functionality across networks. They define the transport mechanisms, data formats, interaction styles, and often how developers should structure their requests and responses. These protocols are often chosen based on specific project needs, such as required data formats, real-time communication, or existing infrastructure. Below is a comprehensive overview of several common protocols and approaches, complete with diagrams and bullet-point notes for easier reference.

```
+-------------+       Request       +-------------+
|             | ------------------> |             |
|   Client    |                     |   Server    |
|             | <------------------ |             |
+-------------+       Response      +-------------+
```

This basic diagram shows a client making a request to a server and the server sending a response. Different protocols can change how data is structured, the method of transport, and the overall interaction pattern (e.g., streaming vs. single request).

### gRPC

```
+---------+       Proto   +---------+
|         | <---- Buffer -|         |
| Client  |               | Server  |
|         | -----> defs ->|         |
+---------+               +---------+
```

- It is widely **useful** in microservices architectures due to its efficient binary serialization with Protocol Buffers.  
- It often leverages **HTTP/2** features such as multiplexing and flow control to optimize network usage.  
- It supports **streaming** communication in multiple directions, including client-to-server, server-to-client, or both simultaneously.  
- It can generate **boilerplate** code automatically from .proto files, reducing manual work in client and server implementations.  
- It requires some **learning** for teams that are new to Protocol Buffers and RPC-based communication.  
- It can offer strong **performance** benefits when handling high-throughput or low-latency operations.  

### REST

```
+-----------+        GET/POST/PUT/DELETE        +-----------+
|           | ------------------------------->  |           |
|  Client   |                                   |   Server  |
|           | <-------------------------------  |           |
+-----------+             JSON/XML/etc.         +-----------+
```

- It is often **simple** to adopt because it builds on standard HTTP methods like GET, POST, PUT, and DELETE.  
- It relies on **resources** identified by URLs, making it straightforward to map endpoints to data entities.  
- It is frequently **common** for web-facing APIs, due to wide tool support and developer familiarity.  
- It typically uses **JSON** as the data format, although XML, YAML, or other formats can also be used.  
- It can experience **over-fetching** or under-fetching issues if clients need more flexible queries.  
- It is normally **stateless**, meaning requests contain all necessary information without storing sessions on the server.  

### GraphQL

```
+------------+      query { ... } / mutation { ... }      +------------+
|            | -----------------------------------------> |            |
|  Client    |                                            |  GraphQL   |
|            | <----------------------------------------- |  Server    |
+------------+                JSON response               +------------+
```

- It is especially **helpful** when clients need precise data fetching, as it allows specifying exactly which fields to retrieve.  
- It uses a **single** endpoint that handles queries, mutations, and subscriptions, simplifying API routing.  
- It requires a **schema** that defines types, which is used to validate and guide incoming requests.  
- It helps reduce **network** overhead in scenarios where multiple resources are needed in a single request.  
- It can introduce **complexity** in server-side resolvers and schema design, especially for large applications.  
- It often employs **JSON** for responses, though the actual request body is a text-based query string.  

### SOAP

```
+-----------+      <soap:Envelope>               +-----------+
|           | <--------------------------------> |           |
|   Client  |        XML-based messages          |   Server  |
|           | <--------------------------------> |           |
+-----------+                                    +-----------+
```

- It is often **useful** in enterprise environments where strict standards and formal contracts are required.  
- It relies on **XML** for message structure, using envelopes, headers, and bodies to encapsulate data.  
- It commonly uses **WSDL** documents for describing service interfaces, data types, and operations.  
- It can integrate **WS-Security** for message-level encryption, signing, and authentication.  
- It can feel more **verbose** than other protocols due to extensive XML and additional layers of abstraction.  
- It often proves **reliable** for legacy or heavily regulated industries that value formal web service contracts.  

### WebSockets

```
   +-----------+  <----------------->  +-----------+
   |           |     persistent        |           |
   |  Client   | <-------------------> |  Server   |
   |           |     bidirectional     |           |
   +-----------+  <----------------->  +-----------+
```

- It can be **helpful** for real-time communication, enabling client and server to send messages at any time.  
- It uses an **upgrade** mechanism that starts over HTTP, switching the connection to a persistent WebSocket protocol.  
- It supports **text** or binary frames for data, allowing flexible message formats such as JSON or custom binaries.  
- It can reduce **latency** compared to repeatedly opening and closing connections for frequent updates.  
- It is often combined with **client-side** JavaScript libraries to manage open connections for chat, notifications, or live feeds.  
- It can require specialized **infrastructure** or load-balancing solutions for scaling high-traffic real-time applications.  

### Server-Sent Events (SSE)

```
+-----------+  text/event-stream    +-----------+
|           | <-------------------  |           |
|  Client   |    continuous feed    |   Server  |
|           | <-------------------  |           |
+-----------+                       +-----------+
```

- It is **useful** when a unidirectional, server-to-client streaming pattern is needed, such as live updates.  
- It sends **text/event-stream** formatted data over a single HTTP connection, staying open for continuous events.  
- It can handle **reconnection** automatically by specifying retry intervals, making it straightforward for many browser-based clients.  
- It typically works best for **lightweight** push scenarios like notifications or real-time dashboards.  
- It lacks **bidirectional** communication, so any client-to-server updates must use separate endpoints.  
- It is often simpler than WebSockets if client feedback to the server is minimal or infrequent.  

### Comparison Table

| Protocol/Style | Transport         | Data Format      | Interaction Style             | Benefits                                              | Drawbacks                                                 | Ideal Use Cases                                                                        |
|----------------|-------------------|------------------|------------------------------|-------------------------------------------------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------|
| **gRPC**       | HTTP/2           | Protocol Buffers | Unary & streaming            | High **performance**, code generation                | Requires learning curve with Protocol Buffers            | Low-latency microservices and multi-language ecosystems                                 |
| **REST**       | HTTP             | JSON, XML, etc.  | Stateless request-response    | Widely **common**, simple tooling                     | Over-fetching/under-fetching issues                      | Web APIs with broad client support                                                     |
| **GraphQL**    | HTTP             | JSON (response)  | Query language & runtime     | **Flexible** field selection, single endpoint         | Resolver complexity in large schemas                     | Complex client data requirements with multiple linked resources                         |
| **SOAP**       | HTTP, SMTP, etc. | XML              | RPC-style or document style   | **Useful** for enterprise standards (WS-Security)     | Verbose payloads, more complex to implement              | Strictly regulated or legacy systems needing formal service definitions                |
| **WebSockets** | TCP (Upgraded)   | Text or Binary   | Bidirectional, real-time     | **Helpful** for interactive applications             | Requires persistent connections, specialized scaling      | Chat, live dashboards, gaming, collaborative editing                                    |
| **SSE**        | HTTP (One-way)   | text/event-stream| Server-to-client streaming    | **Straightforward** setup for continuous updates      | Only supports unidirectional communication               | Live feeds, notifications, real-time event distribution where client rarely sends data |
