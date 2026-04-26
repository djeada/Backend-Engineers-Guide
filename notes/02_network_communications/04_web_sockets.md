## WebSockets

WebSockets introduce an event-driven, two-way communication channel between clients and servers over a single TCP connection. Unlike traditional HTTP request-response systems, where the client sends a request and waits for the server to reply, WebSockets allow both sides to send messages whenever they need to.

This makes WebSockets useful for real-time applications. Instead of repeatedly asking the server, “Has anything changed?” the client can keep one connection open and receive updates immediately when something happens. This reduces the need for polling or long-polling and can lower network overhead in applications with frequent updates.

WebSockets are widely used in chat applications, collaborative editing tools, live dashboards, multiplayer games, financial tickers, notifications, and IoT monitoring systems. Any application that benefits from fast, continuous, bidirectional updates may be a good candidate for WebSockets.

A WebSocket connection begins as an HTTP request. The client asks the server to upgrade the connection from HTTP to WebSocket. If the server accepts, the connection switches protocols. After that, the connection remains open, and both client and server can exchange messages freely until one side closes it.

### The WebSocket Protocol and Handshake

WebSockets rely on an HTTP-based handshake to begin communication. This handshake is important because it allows WebSockets to start through the same infrastructure used by normal web traffic, such as browsers, proxies, and servers.

The connection starts as a normal HTTP request, but the client includes special headers asking the server to upgrade the protocol. If the server supports WebSockets and accepts the request, it responds with `101 Switching Protocols`. After this response, the connection is no longer treated as a normal HTTP request-response exchange.

#### HTTP Upgrade Flow

The upgrade flow moves a connection from HTTP into the WebSocket protocol.

1. A client initiates an HTTP request containing headers that request an upgrade to WebSockets.
2. The server verifies these headers, including a `Sec-WebSocket-Key` that helps confirm a legitimate request.
3. The server responds with an HTTP `101 Switching Protocols` status code and includes a `Sec-WebSocket-Accept` header.
4. Once the handshake completes, communication transitions into WebSocket messages.

```text
Client (Browser/App)                              Server
       |                                             |
       |   1. GET /chat HTTP/1.1                     |
       |   Host: example.com                         |
       |   Upgrade: websocket                        |
       |   Connection: Upgrade                       |
       |   Sec-WebSocket-Key: <key>                  |
       |-------------------------------------------->|
       |                                             |
       |       2. HTTP/1.1 101 Switching Protocols   |
       |          Upgrade: websocket                 |
       |          Connection: Upgrade                |
       |          Sec-WebSocket-Accept: <serverKey>  |
       |<--------------------------------------------|
       |                                             |
       | 3. WebSocket Connection Established         |
       |<=================  Messages  ==============>|
```

Example handshake request:

```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Example handshake response:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Example output:

```text
WebSocket connection established.
Client and server can now exchange messages in both directions.
```

Once the `101 Switching Protocols` response arrives, the protocol moves from HTTP to WebSockets. Communication then continues as WebSocket frames rather than normal HTTP requests and responses.

#### Handshake Headers

The WebSocket handshake depends on specific HTTP headers. These headers tell the server that the client wants to upgrade the connection and help verify that the request is valid.

* **Upgrade**: Must include `websocket`.
* **Connection**: Usually set to `Upgrade`.
* **Sec-WebSocket-Key**: A random base64-encoded key sent by the client.
* **Sec-WebSocket-Accept**: A server-generated value based on the client key and a standard GUID.

Example request headers:

```http
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Example response headers:

```http
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Example interpretation:

```json
{
  "upgradeRequested": true,
  "protocol": "websocket",
  "status": "accepted"
}
```

The `Sec-WebSocket-Key` and `Sec-WebSocket-Accept` headers help prove that the server understood the WebSocket handshake. They are not used as authentication credentials. Real authentication still needs cookies, tokens, sessions, or another authorization mechanism.

### Frame-Based Communication

After the handshake completes, WebSocket communication uses frames. A frame is a structured unit of data that carries part or all of a WebSocket message. This is different from HTTP, which is organized around full requests and responses.

Frames allow WebSockets to send text, binary data, and control messages efficiently. A single message may fit in one frame, or it may be split across multiple frames. This makes WebSockets flexible for both small messages and larger payloads.

Client-to-server frames are masked for security reasons. Server-to-client frames are usually not masked. WebSocket frames also include metadata such as whether the frame is final, what type of data it contains, and how long the payload is.

#### Types of Frames

WebSocket frames can carry different kinds of data.

* **Text frames** carry UTF-8 encoded string data. These are common for JSON messages.
* **Binary frames** carry raw bytes. These are useful for images, audio, video, or compact custom formats.
* **Control frames** manage the connection. Common control frames include `ping`, `pong`, and `close`.

Example text message:

```json
{
  "type": "chat.message",
  "room": "general",
  "text": "Hello everyone!"
}
```

Example server output:

```json
{
  "type": "chat.message",
  "room": "general",
  "user": "Alice",
  "text": "Hello everyone!",
  "timestamp": "2026-04-25T12:00:00Z"
}
```

In this example, the client sends a chat message as structured JSON text. The server can then broadcast the message to other connected clients in the same chat room.

Example binary use case:

```text
Binary frame contains compressed audio data for a live voice stream.
```

Example control output:

```text
Ping sent by server.
Pong received from client.
Connection is still healthy.
```

Control frames help keep the connection stable and allow both sides to detect when the other side has disconnected or stopped responding.


#### Example Frame Layout

A WebSocket frame contains fields that describe the payload and how it should be interpreted.

```text
  0               1               2               3  
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7
 +-+-+-+-+-------+-------------------------------+------------+
 |F|R|R|R| Opcode|   Payload Length  | Mask Bit   |  Mask/Key |
 |I|S|S|S|  (4)  |      (7+)         | (1 bit)    |   (0/4B)  |
 +-+-+-+-+-------+-------------------------------+------------+
 |                  Extended Payload Length (if needed)       |
 +------------------------------------------------------------+
 |                     Payload Data (if masked, XORed)        |
 +------------------------------------------------------------+
```

Example frame interpretation:

```json
{
  "finalFrame": true,
  "opcode": "text",
  "masked": true,
  "payload": "Hello server"
}
```

In the diagram, `FIN` indicates whether this is the final frame in a message. The `Opcode` identifies the frame type, such as text, binary, close, ping, or pong. The `Mask Bit` indicates whether the payload is masked.

This structure allows WebSockets to support fragmented messages, compact control signals, and efficient transmission of different data types.

### Full-Duplex Communication

One of the biggest advantages of WebSockets is full-duplex communication. Full-duplex means both the client and server can send messages independently over the same connection.

In traditional HTTP, the client usually initiates every exchange. The server responds only after receiving a request. With WebSockets, the server can push updates whenever something changes, without waiting for the client to ask.

```text
+------------------+
| Client           |  
| (WebSocket)      |  
| (Browser/App)    | <--------------------\
+------------------+                      \
        ^                                  \
        |  Bi-Directional,                 \
        |  Full-Duplex Channel             \
        v                                  /
+------------------+                       /
| Server           | <--------------------/
| (WebSocket Host) |
+------------------+
```

Example client message:

```json
{
  "type": "typing.started",
  "room": "general",
  "user": "Alice"
}
```

Example server message sent immediately to other clients:

```json
{
  "type": "user.typing",
  "room": "general",
  "user": "Alice"
}
```

This event-driven approach improves real-time functionality. A chat room can broadcast messages immediately. A collaborative editor can push document changes to all connected users. A dashboard can update charts as new data arrives.

Because the connection stays open, WebSockets avoid the overhead of repeatedly creating new HTTP requests for every small update.

### Example: Simple WebSocket in JavaScript and Node.js

The following example shows a simple WebSocket echo server. The client sends a message, and the server sends a response containing that same message.

This kind of example is useful for understanding the basic WebSocket lifecycle: connect, send a message, receive a message, and close.

#### Server-Side — Node.js

Using the `ws` library, developers can create a basic WebSocket server.

```js
// server.js
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected.');
  
  ws.on('message', (message) => {
    console.log('Received:', message);
    // Echo the message back to the client
    ws.send(`Server received: ${message}`);
  });
  
  ws.on('close', () => {
    console.log('Client disconnected.');
  });
});

console.log('WebSocket server running on ws://localhost:8080');
```

Example server startup output:

```text
WebSocket server running on ws://localhost:8080
```

Example output when a client connects:

```text
Client connected.
```

Example output when the client sends a message:

```text
Received: Hello WebSocket server
```

In this example, a WebSocket server is created on port `8080`. When a new client connects, the `connection` event fires. When the server receives a message, it logs the message and sends an echo response back to the same client.

If the client disconnects, the `close` event fires. This lets the server clean up connection-specific resources if needed.

#### Client-Side — Browser

In a browser-based application, the built-in `WebSocket` object can be used to connect to the server.

```html
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket Example</title>
</head>
<body>
  <textarea id="log" rows="10" cols="50" readonly></textarea><br>
  <input type="text" id="msg" />
  <button id="sendBtn">Send</button>

  <script>
    const socket = new WebSocket('ws://localhost:8080');
    const logArea = document.getElementById('log');
    const input = document.getElementById('msg');
    const sendBtn = document.getElementById('sendBtn');

    socket.addEventListener('open', () => {
      logArea.value += 'Connected to server\n';
    });

    socket.addEventListener('message', (event) => {
      logArea.value += 'Server says: ' + event.data + '\n';
    });

    sendBtn.addEventListener('click', () => {
      socket.send(input.value);
      logArea.value += 'You sent: ' + input.value + '\n';
      input.value = '';
    });
  </script>
</body>
</html>
```

Example browser log after connecting:

```text
Connected to server
```

Example browser log after sending a message:

```text
You sent: Hello WebSocket server
Server says: Server received: Hello WebSocket server
```

The client establishes a connection to `ws://localhost:8080`. The `open` event runs when the connection is ready. The `message` event runs whenever the server sends data. The button sends the text input to the server using `socket.send()`.

This example uses `ws://`, which is unencrypted. In production, WebSockets should generally use `wss://`, which runs over TLS.

### Subprotocols and Extensions

The WebSocket specification allows clients and servers to agree on subprotocols during the handshake. A subprotocol defines the message format or application-level rules used over the WebSocket connection.

For example, a WebSocket connection might use STOMP for messaging, GraphQL subscriptions, or a custom protocol designed for a specific application. This helps both sides understand how messages should be structured and interpreted.

Example client request with subprotocols:

```http
GET /socket HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: abc123==
Sec-WebSocket-Protocol: chat.v1, chat.v2
```

Example server response:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Protocol: chat.v2
```

Example output:

```json
{
  "selectedSubprotocol": "chat.v2",
  "status": "connection upgraded"
}
```

Extensions can also modify WebSocket behavior. A common extension is `permessage-deflate`, which compresses messages to reduce bandwidth usage.

Example extension header:

```http
Sec-WebSocket-Extensions: permessage-deflate
```

Compression can help when messages are large or frequent, but it also adds CPU overhead. Teams should test whether compression improves performance for their specific workload.

### Load Balancing and Horizontal Scaling

Large-scale WebSocket deployments often place a load balancer or reverse proxy in front of multiple WebSocket server instances. This allows traffic to be distributed across several servers instead of relying on one machine.

However, WebSockets are different from short HTTP requests because connections stay open for a long time. A server may need to remember which users are connected and which rooms or topics they have subscribed to. This can complicate scaling.

```text
        Clients
           |
           v
+---------------------+
|   Load Balancer     |
+----------+----------+
           |
  +--------+--------+
  |        |        |
  v        v        v
Server 1 Server 2 Server 3
```

Example connection distribution:

```json
{
  "server1Connections": 12000,
  "server2Connections": 11850,
  "server3Connections": 12110
}
```

Sticky sessions or consistent hashing may be needed so messages from the same client continue reaching the correct server. Another approach is to use a shared message broker, such as Redis Pub/Sub, Kafka, or NATS, so any server can publish events to clients connected elsewhere.

One simple concurrency formula is:

```text
Max_Connections = (Memory_Per_Server / Connection_Overhead) * Number_of_Servers
```

Example calculation:

```text
Memory_Per_Server = 8 GB
Connection_Overhead = 64 KB
Number_of_Servers = 4

Max_Connections = (8 GB / 64 KB) * 4
Max_Connections ≈ 524,288 connections
```

Example output:

```text
Estimated maximum connections: about 524,288 across 4 servers
```

This is only a simplified estimate. Real limits also depend on CPU usage, network bandwidth, operating system limits, TLS overhead, message frequency, garbage collection, and application memory usage.

### Common Use Cases

WebSockets are useful when applications need low-latency updates or continuous communication. They are especially helpful when both the client and server need to send messages independently.

Common use cases include:

* Collaborative editing, such as live documents or shared code editors.
* Gaming dashboards and multiplayer game updates.
* Financial tickers and dashboards with rapidly changing data.
* Chat and messaging applications that need immediate message delivery.
* IoT monitoring or remote control systems where devices push events to a central console.

Example chat event:

```json
{
  "type": "chat.message",
  "roomId": "room-123",
  "from": "Alice",
  "message": "Are we ready to start?"
}
```

Example dashboard event:

```json
{
  "type": "metric.update",
  "metric": "cpu_usage",
  "value": 72.4,
  "unit": "%"
}
```

Example IoT event:

```json
{
  "type": "sensor.reading",
  "deviceId": "sensor-9",
  "temperature": 21.8,
  "humidity": 44
}
```

These examples show why WebSockets are useful for real-time systems. The server can push the latest data as soon as it becomes available.

### Security Considerations

WebSockets should generally use `wss://` in production. `wss://` means WebSocket Secure, which uses TLS in the same way HTTPS protects HTTP traffic. This protects messages from being read or modified in transit.

Authentication and authorization are also important. The server should verify who is connecting and what that client is allowed to access. This can be done with cookies, session IDs, bearer tokens, or signed connection parameters.

Important security practices include:

* Authenticating the handshake with existing cookies or tokens.
* Validating the `Origin` header to reduce cross-site abuse.
* Checking authorization before subscribing users to rooms or channels.
* Handling abrupt disconnections and cleaning up connection state.
* Limiting message size and message rate to prevent abuse.

Example authenticated connection message:

```json
{
  "type": "authenticate",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

Example success output:

```json
{
  "type": "auth.success",
  "userId": "user-123"
}
```

Example failed authentication output:

```json
{
  "type": "auth.error",
  "message": "Invalid or expired token"
}
```

Authentication should happen before the server allows access to private channels or sensitive data. A connected socket should not automatically mean the user is authorized to receive all messages.

### Heartbeats, Ping/Pong, and Connection Stability

WebSocket connections can remain open for long periods, but networks are not always stable. A user might close a laptop, lose mobile connectivity, move between networks, or disconnect unexpectedly. Servers need a way to detect stale or dead connections.

The WebSocket protocol includes `ping` and `pong` control frames. One endpoint can send a ping, and the other endpoint should reply with a pong. If no pong is received within a configured time, the connection may be considered unhealthy and closed.

Example heartbeat flow:

```text
Server → Client: ping
Client → Server: pong
Server: connection is healthy
```

Example failed heartbeat:

```text
Server → Client: ping
No pong received within timeout
Server closes connection
```

Example output:

```json
{
  "connectionId": "conn-123",
  "heartbeat": "failed",
  "action": "connection_closed"
}
```

Heartbeats help servers avoid keeping dead connections in memory. They also help clients detect when they need to reconnect.

Client applications should usually handle reconnects gracefully. For example, a chat app might reconnect automatically and resubscribe to the current room after the connection is restored.

### Best Practices

WebSockets can scale well, but they require careful operational design because each connection consumes server resources. Unlike short HTTP requests, WebSocket connections may stay open for minutes, hours, or longer.

Useful practices include:

* Gracefully handle dropped connections by listening for the `close` event and reconnecting when appropriate.
* Use subprotocols or custom message formats so both sides clearly understand message structure.
* Implement rate limiting and message-size limits to reduce flooding attacks.
* Monitor connection counts, memory usage, CPU usage, message throughput, and disconnect rates.
* Ensure load balancers and reverse proxies support the `Upgrade` header correctly.
* Use `wss://` in production to protect traffic with TLS.

Example structured message format:

```json
{
  "type": "order.updated",
  "requestId": "req-123",
  "payload": {
    "orderId": "order-789",
    "status": "shipped"
  }
}
```

Example monitoring output:

```json
{
  "activeConnections": 48250,
  "messagesPerSecond": 9200,
  "averageMessageSizeBytes": 340,
  "disconnectRatePerMinute": 120,
  "memoryUsage": "68%"
}
```

Structured messages make client and server code easier to maintain. Monitoring helps teams detect overload, connection leaks, message floods, or unstable network behavior.

### Comparison with Other Real-Time Techniques

Before WebSockets became common, developers often used short-polling or long-polling to simulate real-time behavior. These techniques still work, but they can create extra overhead because they rely on repeated HTTP requests.

Server-Sent Events, or SSE, provide another option. SSE allows the server to push updates to the browser over a long-lived HTTP connection. However, SSE is one-way: the server can send data to the client, but the client must use normal HTTP requests to send data back.

| Technique          | Direction                         | Connection Style            | Typical Use Case                         |
| ------------------ | --------------------------------- | --------------------------- | ---------------------------------------- |
| Short polling      | Client repeatedly asks server     | Many HTTP requests          | Simple periodic updates                  |
| Long polling       | Client waits for server response  | Repeated long HTTP requests | Basic near-real-time updates             |
| Server-Sent Events | Server to client                  | Long-lived HTTP connection  | Notifications, feeds, dashboards         |
| WebSockets         | Client and server both directions | Long-lived TCP connection   | Chat, games, collaboration, live systems |

Example short-polling flow:

```text
Client: Any updates?
Server: No
Client: Any updates?
Server: Yes, here is one update
```

Example WebSocket flow:

```text
Connection stays open
Server sends update immediately when it happens
Client can also send messages at any time
```

WebSockets stand out because they provide bidirectional, full-duplex communication. This makes them flexible and efficient for real-time interactions where both client and server need to send messages frequently.
