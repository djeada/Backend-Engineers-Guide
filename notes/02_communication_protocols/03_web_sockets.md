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


```
Client                            Server
  |                                  |
  |----- HTTP Request (Upgrade) ---->|
  |                                  |
  |<---- HTTP Response (101) --------|
  |                                  |
  |====== WebSocket Connection =====>|
  |                                  |
  |<==== Bi-directional Data Flow ===|
  |                                  |
```

## Use Cases for WebSockets

- Real-time applications: chat apps, multiplayer games, real-time trading systems, etc.
- Collaborative editing/coding applications: Google Docs, VS Code Live Share, etc.

## WebSockets vs HTTP

| Feature              | HTTP (Hypertext Transfer Protocol)               | WebSocket Protocol                        |
|----------------------|--------------------------------------------------|------------------------------------------|
| Connection Type      | Connectionless (each request/response is separate) | Persistent, full-duplex communication   |
| Communication        | Unidirectional (client to server)                | Bidirectional (client and server)        |
| Overhead             | Higher (headers for each request/response)       | Lower (overhead only at the beginning)   |
| Use Cases            | Web page loading, RESTful services               | Real-time applications, chat applications |
| Data Format          | Primarily text (HTML, JSON, XML)                 | Flexible (text or binary data)           |
| Statefulness         | Stateless (each request is independent)          | Stateful (connection stays open)         |
| Default Port         | 80 (HTTP), 443 (HTTPS)                           | Varies, often 80 or 443 with HTTP/HTTPS  |
| Protocol Upgrade     | Not applicable                                   | Upgraded from HTTP                        |
| Latency              | Higher (due to new connection for each request)  | Lower (continuous connection)            |

## Creating a WebSocket Server

Creating a simple "Hello World" WebSocket server in Python is quite straightforward. You can use the `websockets` library, which provides easy-to-use methods to handle WebSocket connections. Here's an example to get you started:

First, ensure you have the `websockets` library installed. You can install it using pip:

```
bash
pip install websockets
```

Then, you can create a WebSocket server with the following Python script:

```python
import asyncio
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

start_server = websockets.serve(hello, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

In this script:

- The hello function is an asynchronous handler for WebSocket connections. It receives a message from the client (in this case, a name), prints it, sends back a greeting, and then prints the greeting.
- The `websockets.serve()` function starts a WebSocket server on localhost with the port 8765.
- The `asyncio.get_event_loop()` lines are used to start and run the server indefinitely.

To test this server:

- Run the Python script to start the server.
- Connect to the server using a WebSocket client (you can use various tools or libraries in different programming languages for this, or even browser-based tools).
- Send a message (like "World") from your client.
- The server will respond with "Hello World!"
    
## Best Practices for WebSocket Design

- Use WebSocket libraries or frameworks: Don't implement the protocol from scratch, use existing libraries.
- Handle connection failures and reconnections.
- Consider security implications: Encrypt data with wss:// (WebSocket secure protocol), validate and sanitize all received data, etc.

