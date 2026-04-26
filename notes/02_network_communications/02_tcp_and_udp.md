## TCP vs UDP

Transmission Control Protocol, or **TCP**, and User Datagram Protocol, or **UDP**, are foundational Internet protocols that operate on top of IP. IP is responsible for addressing and routing packets between devices, while TCP and UDP define how applications send and receive data through ports on those devices.

TCP prioritizes reliability, ordering, and correctness. It is designed for situations where missing or out-of-order data would cause problems. UDP focuses on speed, simplicity, and low overhead. It is useful when applications can tolerate some packet loss or when the application wants to manage reliability itself.

Both protocols are important, and neither is universally better. The right choice depends on the application’s requirements for latency, reliability, ordering, throughput, and network behavior.

### TCP — Transmission Control Protocol

TCP is a connection-oriented protocol. Before application data is sent, the client and server establish a connection using a handshake. Once connected, TCP provides a reliable stream of bytes between the two endpoints.

This reliability makes TCP ideal for scenarios where missing data is unacceptable. Examples include loading web pages, transferring files, sending emails, querying databases, or using APIs where the client expects a complete and correct response.

TCP uses acknowledgments, sequence numbers, retransmissions, flow control, and congestion control. These mechanisms make TCP more reliable, but they also add overhead compared with UDP.

#### How TCP Works

The TCP process begins with a three-way handshake. This handshake allows the client and server to agree that both sides are ready to communicate before sending payload data.

```text
Client                           Server
   |                                |
   |    1. SYN (Synchronize)        |
   |------------------------------->|
   |                                |
   |    2. SYN + ACK (Acknowledge)  |
   |<-------------------------------|
   |                                |
   |    3. ACK                      |
   |------------------------------->|
   |                                |
   |   Connection Established       |
   |<==============================>|
```

Example sequence:

```text
Client sends SYN
Server responds with SYN-ACK
Client sends ACK
Connection is ready for data
```

Example output:

```text
TCP connection established between client and server.
```

After the connection is established, TCP sends data in segments. Each segment includes sequence information so the receiver can reassemble data in the correct order. If a segment is lost, TCP can retransmit it. If segments arrive out of order, TCP can reorder them before delivering the data to the application.

This means the application usually receives a clean, ordered byte stream instead of having to manually manage packet loss or packet ordering.

#### Features of TCP

TCP provides several features that make it reliable and widely used in backend systems.

1. **Connection-oriented communication** TCP requires a handshake before data is exchanged. The connection also has a controlled shutdown process when communication ends.
2. **Ordered delivery** TCP tracks sequence numbers so data can be delivered to the application in the correct order, even if packets take different paths through the network.
3. **Reliability** Acknowledgments, timeouts, and retransmissions help ensure that lost data is resent.
4. **Flow and congestion control** TCP adjusts the sending rate based on receiver capacity and network conditions. This helps avoid overwhelming the receiver or congesting the network.

Example TCP behavior:

```text
Packet 1 sent → acknowledged
Packet 2 sent → lost
Packet 2 retransmitted → acknowledged
Packet 3 sent → acknowledged
```

Example output:

```json
{
  "protocol": "TCP",
  "delivery": "reliable",
  "ordering": "preserved",
  "lostPackets": "retransmitted"
}
```

The application does not usually need to know that Packet 2 was lost and retransmitted. TCP handles that at the transport layer.

#### Code Example: Simple TCP Server in Python

This example creates a basic TCP server using Python’s built-in `socket` module. The server listens on localhost port `5000`, accepts one connection, receives data, and sends a response.

```python
import socket

HOST = '127.0.0.1'
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("TCP server listening on port", PORT)
    
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        data = conn.recv(1024)
        print("Received:", data.decode())
        conn.sendall(b"Hello from TCP server!")
```

Example terminal output after starting the server:

```text
TCP server listening on port 5000
```

Example client command using netcat:

```bash
nc 127.0.0.1 5000
```

Example message typed by the client:

```text
Hello server
```

Example server output:

```text
Connected by ('127.0.0.1', 53422)
Received: Hello server
```

Example client output:

```text
Hello from TCP server!
```

In this example, the server accepts a TCP connection and receives data from the client. The `SOCK_STREAM` setting indicates that the socket uses TCP. The server then sends a response back over the same connection.

#### Typical TCP Use Cases

TCP is used when correctness and reliable delivery are more important than minimizing every bit of latency.

Common TCP use cases include:

1. **Web browsing** using HTTP/HTTPS.
2. **File transfers** using FTP, SFTP, or SCP.
3. **Email protocols** such as SMTP, IMAP, and POP3.
4. **Database connections** that require reliable delivery of queries and results.

Example HTTP-over-TCP request:

```http
GET /posts/1 HTTP/1.1
Host: api.example.com
```

Example output:

```json
{
  "id": 1,
  "title": "TCP is reliable",
  "status": "delivered in order"
}
```

The API response must arrive complete and in order. TCP is well suited for this because the client expects the full response body to be correct before processing it.

### UDP — User Datagram Protocol

UDP is a connectionless protocol. It sends packets, called datagrams, without first establishing a formal connection. UDP does not guarantee delivery, ordering, or retransmission.

This makes UDP lightweight and fast. It is often used when low latency matters more than perfect reliability, or when the application protocol handles reliability itself.

UDP is common in real-time communication, gaming, streaming, DNS, service discovery, and newer protocols such as QUIC. In these situations, waiting for retransmissions may be worse than simply dropping outdated data and continuing with newer data.

#### How UDP Works

UDP communication takes place by sending datagrams to a target IP address and port. There is no three-way handshake, and each datagram is handled independently.

```text
Client                               Server
   |                                    |
   |   1. UDP Datagram (Data)           |
   |----------------------------------->|
   |                                    |
   |   2. UDP Datagram (Response)       |
   |<-----------------------------------|
   |                                    |
   |   No handshake or guaranteed       |
   |   arrival order                    |
```

Example sequence:

```text
Client sends datagram 1
Client sends datagram 2
Client sends datagram 3
```

Example possible result:

```text
Server receives datagram 1
Server receives datagram 3
Datagram 2 is lost
```

Example output:

```json
{
  "protocol": "UDP",
  "delivery": "best effort",
  "ordering": "not guaranteed",
  "retransmission": "not built in"
}
```

UDP does not automatically fix missing or out-of-order packets. If the application cares about those issues, it must implement its own handling at a higher layer.

#### Features of UDP

UDP provides a simpler transport model than TCP. This simplicity is what makes it useful in low-latency systems.

1. **Connectionless communication** UDP does not require a handshake or session setup before sending data.
2. **No guaranteed delivery** Datagrams can be lost, duplicated, or arrive out of order.
3. **Low overhead** UDP has fewer built-in control mechanisms than TCP, which can reduce latency and processing overhead.
4. **Suitable for broadcast or multicast** UDP is commonly used in local network discovery and one-to-many communication patterns.

Example UDP behavior:

```text
Datagram 1 sent → received
Datagram 2 sent → lost
Datagram 3 sent → received
```

Example output:

```json
{
  "receivedDatagrams": [1, 3],
  "missingDatagrams": [2],
  "action": "application decides whether this matters"
}
```

For a live video stream, losing one datagram may cause a small visual glitch but the stream can continue. For a bank transfer, losing data would be unacceptable, so raw UDP would not be appropriate.

#### Code Example: Simple UDP Server in Python

This example creates a basic UDP server using Python’s built-in `socket` module. The server listens on localhost port `5001`, receives datagrams, and sends a response to the sender.

```python
import socket

HOST = '127.0.0.1'
PORT = 5001

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print("UDP server listening on port", PORT)
    
    while True:
        data, addr = s.recvfrom(1024)
        print("Received from", addr, ":", data.decode())
        s.sendto(b"Hello from UDP server!", addr)
```

Example terminal output after starting the server:

```text
UDP server listening on port 5001
```

Example client command using netcat:

```bash
nc -u 127.0.0.1 5001
```

Example message typed by the client:

```text
Hello UDP server
```

Example server output:

```text
Received from ('127.0.0.1', 54022) : Hello UDP server
```

Example client output:

```text
Hello from UDP server!
```

In this example, the server does not call `listen()` or `accept()` because UDP does not establish a connection. Instead, it waits for datagrams using `recvfrom()` and replies to the address that sent the message.

#### Typical UDP Use Cases

UDP is useful when low latency, simplicity, or one-to-many communication matters more than guaranteed delivery.

Common UDP use cases include:

1. **Live video or audio streaming**, where some packet loss is tolerable.
2. **Online gaming**, especially for real-time position updates.
3. **DNS lookups**, especially small request-response exchanges.
4. **Internal network broadcast or multicast services**.

Example DNS-style request:

```text
Client asks: What is the IP address for example.com?
Server replies: 93.184.216.34
```

Example output:

```json
{
  "query": "example.com",
  "address": "93.184.216.34",
  "transport": "UDP"
}
```

UDP is only the transport layer. Higher-level protocols can add reliability, encryption, stream management, or retransmission behavior on top of it. For example, QUIC runs over UDP and implements its own recovery, congestion control, multiplexing, and secure session establishment.

### Comparing TCP and UDP

TCP and UDP make different trade-offs. TCP is more reliable and easier for many application developers because it handles ordering and retransmission automatically. UDP is lighter and gives application designers more control, but it requires additional logic if reliability matters.

| Aspect            | TCP                                                               | UDP                                                              |
| ----------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------- |
| Connection Model  | Connection-oriented with a three-way handshake                    | Connectionless                                                   |
| Reliability       | Guaranteed delivery with retransmissions                          | Best-effort delivery with no guarantee                           |
| Ordering          | Data is delivered in order                                        | Datagrams can arrive in any order                                |
| Overhead          | Higher due to handshakes, acknowledgments, and control mechanisms | Lower due to lightweight headers and no built-in retransmissions |
| Speed             | Often slower because of reliability mechanisms                    | Often faster but less reliable                                   |
| Typical Use Cases | Web requests, file transfers, email, database access              | Streaming media, online games, DNS, QUIC/HTTP/3                  |

Example decision output:

```json
{
  "useTCPWhen": "The application needs reliable, ordered delivery.",
  "useUDPWhen": "The application needs low latency or custom transport behavior."
}
```

A practical way to think about the choice is this: TCP gives reliability by default, while UDP gives flexibility by default.

### Performance and Throughput

TCP throughput is affected by round-trip time, congestion control, packet loss, and window size. A simplified throughput equation can illustrate the relationship:

```text
Throughput_tcp ≈ Window_size / RTT
```

`Window_size` is how much data can be sent before waiting for acknowledgments. `RTT`, or round-trip time, is the time it takes for data to reach the receiver and for an acknowledgment to return.

Example calculation:

```text
Window_size = 1,000,000 bytes
RTT = 0.1 seconds

Throughput_tcp ≈ 1,000,000 / 0.1
Throughput_tcp ≈ 10,000,000 bytes per second
```

Example output:

```text
Estimated TCP throughput: 10 MB/s
```

This is simplified, but it shows why latency matters. Higher RTT reduces throughput unless the window size increases. Packet loss can also reduce TCP throughput because TCP interprets loss as a signal of congestion and may slow down.

UDP does not have a built-in window mechanism. UDP throughput depends on application behavior, network capacity, packet size, and whether the application implements its own congestion control or retransmission strategy.

Example UDP output:

```json
{
  "protocol": "UDP",
  "throughputControl": "application-defined",
  "risk": "sending too fast can cause packet loss or network congestion"
}
```

UDP can be fast, but responsible applications still need to avoid overwhelming the network.

### Security Considerations

Both TCP and UDP can be used with secure protocols. The security layer depends on the application protocol and transport behavior.

For TCP-based web traffic, TLS is commonly used. HTTPS is HTTP over TLS, which protects data from eavesdropping and tampering.

For UDP-based traffic, DTLS can provide security for datagram-based communication. QUIC also includes encryption as part of its design.

1. **TCP over TLS** Commonly used for HTTPS, secure APIs, and many encrypted application protocols.
2. **UDP over DTLS** Used when datagram-based traffic needs encryption, such as some VoIP or real-time systems.

Example HTTPS request:

```http
GET /account HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Example protected output:

```json
{
  "accountId": "acct-123",
  "status": "active"
}
```

The application sees normal HTTP data, but TLS encrypts it while it travels across the network.

Example DTLS-style use case output:

```json
{
  "transport": "UDP",
  "security": "DTLS",
  "useCase": "secure real-time communication"
}
```

Security should be considered regardless of whether TCP or UDP is used. Sensitive data should not be transmitted in clear text.

### Choosing Between TCP and UDP in Practice

The choice is rarely just “reliable versus unreliable.” A better question is where the complexity should live.

Choose **TCP** when the application expects ordered bytes, built-in retransmission, and straightforward interoperability with existing tooling. TCP is usually the right choice for REST APIs, GraphQL APIs, traditional web apps, file transfer, email, and database connections.

Choose **UDP** when low latency, multicast, broadcast, or custom transport behavior matters more than in-order delivery. UDP is common in real-time audio/video, games, discovery protocols, and systems where stale data is less useful than fresh data.

Choose a **UDP-based higher-level protocol** such as QUIC when you want low-latency connection setup and stream multiplexing, but still need reliability and encryption above raw UDP.

Example final decision guide:

```json
{
  "webApi": "TCP",
  "fileTransfer": "TCP",
  "databaseConnection": "TCP",
  "liveGamePositions": "UDP",
  "videoCallMedia": "UDP or UDP-based protocol",
  "modernHTTP3Traffic": "QUIC over UDP"
}
```

TCP is best when correctness and ordering are essential. UDP is best when speed, flexibility, or real-time behavior matters more. Modern protocols such as QUIC show that UDP can also be used as a foundation for more advanced reliable transports when the application needs finer control than TCP provides.
