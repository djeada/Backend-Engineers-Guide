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

### Long Polling

```
+-----------+                       +-----------+
|           |  1. Request           |           |
|  Client   | --------------------> |  Server   |
|           |                       |  (holds)  |
|           |  2. Response when     |           |
|           | <---- data ready ---- |           |
+-----------+                       +-----------+
     |                                    |
     | 3. Immediately send new request    |
     | ---------------------------------> |
     |          (cycle repeats)           |
```

- It serves as a **bridge** between plain HTTP polling and full real-time protocols, keeping a request open until the server has something to send.  
- It reduces **wasted** requests compared to short polling, where the client repeatedly asks for updates at fixed intervals.  
- It is **compatible** with standard HTTP infrastructure, so no special protocol upgrades or server features are needed.  
- It can increase **server load** when many clients hold open connections simultaneously, requiring careful resource management.  
- It may suffer from **timeout** issues, since proxies and load balancers sometimes close idle connections, forcing the client to reconnect.  
- It is often used as a **fallback** for environments where WebSockets or SSE are not supported.  

### Webhooks

```
+-----------+   1. Register callback URL   +-----------+
|           | ---------------------------> |           |
| Consumer  |                              | Provider  |
|           |   2. Event occurs, POST to   |           |
|           | <--------------------------- |           |
+-----------+       callback URL           +-----------+
```

- They use an **inversion** of the typical request-response model, where the server pushes data to the client when an event occurs rather than the client polling for changes.  
- They require the consumer to expose an **endpoint** that the provider can call, which means the consumer must be reachable over the network.  
- They are well **suited** for event-driven integrations such as payment confirmations, repository push notifications, or CI/CD triggers.  
- They typically transmit **JSON** payloads over HTTPS POST requests, often including a signature header so the consumer can verify authenticity.  
- They can introduce **reliability** challenges because the consumer must acknowledge receipt; providers often implement retry logic for failed deliveries.  
- They work best when events are **infrequent** and the consumer does not need a continuous stream of data.  

### Choosing the Right Protocol

Selecting a protocol depends on the specific requirements of the system being built. The following decision factors help narrow down the choices:

- **Latency requirements** determine whether a persistent connection (WebSockets, gRPC streaming) is necessary or whether request-response patterns (REST, GraphQL) suffice.  
- **Data shape flexibility** matters when clients vary widely in what they need; GraphQL excels here, while REST works well when resources are well-defined.  
- **Interoperability** is important for public-facing APIs where broad client support is required; REST and webhooks are nearly universal.  
- **Throughput and efficiency** favor binary protocols like gRPC when services communicate internally at high volume.  
- **Team expertise** can influence adoption speed; REST has the lowest barrier to entry, while gRPC and GraphQL have steeper learning curves.  
- **Direction of data flow** separates unidirectional patterns (SSE, webhooks) from bidirectional ones (WebSockets, gRPC streaming).  

### Comparison Table

| Protocol/Style | Transport         | Data Format      | Interaction Style             | Benefits                                              | Drawbacks                                                 | Ideal Use Cases                                                                        |
|----------------|-------------------|------------------|------------------------------|-------------------------------------------------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------|
| **gRPC**       | HTTP/2           | Protocol Buffers | Unary & streaming            | High **performance**, code generation                | Requires learning curve with Protocol Buffers            | Low-latency microservices and multi-language ecosystems                                 |
| **REST**       | HTTP             | JSON, XML, etc.  | Stateless request-response    | Widely **common**, simple tooling                     | Over-fetching/under-fetching issues                      | Web APIs with broad client support                                                     |
| **GraphQL**    | HTTP             | JSON (response)  | Query language & runtime     | **Flexible** field selection, single endpoint         | Resolver complexity in large schemas                     | Complex client data requirements with multiple linked resources                         |
| **SOAP**       | HTTP, SMTP, etc. | XML              | RPC-style or document style   | **Useful** for enterprise standards (WS-Security)     | Verbose payloads, more complex to implement              | Strictly regulated or legacy systems needing formal service definitions                |
| **WebSockets** | TCP (Upgraded)   | Text or Binary   | Bidirectional, real-time     | **Helpful** for interactive applications             | Requires persistent connections, specialized scaling      | Chat, live dashboards, gaming, collaborative editing                                    |
| **SSE**        | HTTP (One-way)   | text/event-stream| Server-to-client streaming    | **Straightforward** setup for continuous updates      | Only supports unidirectional communication               | Live feeds, notifications, real-time event distribution where client rarely sends data |
| **Long Polling** | HTTP           | JSON, XML, etc.  | Held request-response         | **Compatible** with standard HTTP infrastructure      | Higher server resource usage from held connections        | Near-real-time updates when WebSockets or SSE are unavailable                          |
| **Webhooks**   | HTTP (Callback)  | JSON (typically) | Event-driven push             | **Efficient** for infrequent events, no polling       | Consumer must be reachable; delivery reliability concerns | Payment notifications, CI/CD triggers, third-party integrations                        |
