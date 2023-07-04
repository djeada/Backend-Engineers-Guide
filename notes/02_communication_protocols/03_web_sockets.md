# WebSockets

WebSockets provide a persistent connection between a client and server that both parties can use to send data at any time. This is in contrast to the typical web response paradigm, where the client requests and the server responds.

## Basics of WebSockets

- **Persistent Connection**: Unlike HTTP, the WebSocket protocol allows for a long-held single TCP socket connection.

- **Full-Duplex Communication**: Data can be sent and received simultaneously, unlike HTTP where data is only transferred in one direction at a time.

- **Lower Latency**: WebSockets keep the connection open, which reduces latency for real-time apps.

## How WebSockets Work

- The client initiates the WebSocket connection over HTTP.
- The server responds and an upgrade request is made from HTTP to WebSocket protocol.
- Once both parties agree on the protocol upgrade, a persistent, full-duplex WebSocket connection is established.

## Use Cases for WebSockets

- Real-time applications: chat apps, multiplayer games, real-time trading systems, etc.
- Collaborative editing/coding applications: Google Docs, VS Code Live Share, etc.

## Comparison: WebSockets vs HTTP

- HTTP is a request-response protocol, whereas WebSockets provide full-duplex communication.
- HTTP connections are not persistent, whereas WebSockets connections are.

## Creating a WebSocket Server

- Steps to create a simple WebSocket server (possibly with example code).

## Best Practices for WebSocket Design

- Use WebSocket libraries or frameworks: Don't implement the protocol from scratch, use existing libraries.
- Handle connection failures and reconnections.
- Consider security implications: Encrypt data with wss:// (WebSocket secure protocol), validate and sanitize all received data, etc.

