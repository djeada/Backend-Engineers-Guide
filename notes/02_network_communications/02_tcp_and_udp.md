## TCP vs UDP

Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) are fundamental transport protocols that enable different types of applications to communicate over networks. They each address data delivery in different ways, making it helpful to understand their characteristics before deciding which one to use in a given scenario. In essence, TCP acts like a registered letter that requires proof of delivery, while UDP behaves more like a simple letter that may not be guaranteed to arrive.

### TCP (Transmission Control Protocol)

```
Client                                      Server
  |                                           |
  | ------ SYN (Sequence Number x) ------>    |
  |                                           |
  | <----- SYN-ACK (Sequence Number y,        |
  |         Acknowledgment Number x+1) ----   |
  |                                           |
  | ------ ACK (Acknowledgment Number y+1) -> |
  |                                           |
```

- It uses a **three-way** handshake to establish a connection, ensuring both sides are synchronized for data exchange.  
- It includes **acknowledgments** for every data segment sent, leading to reliable and ordered delivery.  
- It applies a **sliding** window mechanism to control data flow, preventing receivers from being overwhelmed.  
- It relies on **congestion** control algorithms to adapt its sending rate based on network conditions.  
- It implements a **four-way** handshake procedure for closing a connection once data transfer is complete.  

### UDP (User Datagram Protocol)

```
Client                                      Server
  |                                           |
  | ------- UDP Data Packet (Data) ------->   |
  |                                           |
  (no acknowledgment from the server)
  |                                           |
  | <------ UDP Data Packet (Response) ------ |
  |                                           |
```

- It does not require a **connection** to be established before sending data, making it lightweight.  
- It sends **datagrams** without waiting for acknowledgments, which can be faster but less reliable.  
- It can deliver packets **out-of-order** or lose them entirely if network conditions deteriorate.  
- It offers an optional **checksum** for basic data integrity, allowing the application layer to handle errors.  
- It is frequently **useful** for real-time applications like streaming media and online gaming.  

### Comparison

TCP and UDP each serve different needs. TCP is helpful for scenarios where data integrity and reliable delivery matter more than speed. UDP is often used when low latency is desired and occasional packet loss is acceptable. Some applications even combine both protocols by leveraging TCP for configuration data and UDP for time-sensitive transmissions.

| Feature                  | TCP                                     | UDP                                        |
|--------------------------|-----------------------------------------|--------------------------------------------|
| Connection               | Connection-oriented (uses handshake)    | Connectionless (no handshake)              |
| Reliability              | Guarantees delivery of data             | Does not guarantee delivery of data        |
| Data Ordering            | Maintains sequence of data              | May arrive out of sequence                 |
| Speed                    | Slower due to additional overhead       | Faster in many cases due to low overhead   |
| Flow Control             | Uses a sliding window mechanism         | No native mechanism for flow control       |
| Error Checking           | Uses acknowledgments and retransmission | Uses basic checksums without retransmission |
| Congestion Control       | Adapts sending rate based on network    | Leaves congestion handling to the application |
| Header Size (Minimum)    | 20 bytes                                | 8 bytes                                    |
| Typical Use Cases        | Web browsing, file transfers, email     | Video/audio streaming, VoIP, DNS, gaming   |

