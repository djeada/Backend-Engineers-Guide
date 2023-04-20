
## TCP and UDP

TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) are two common transport layer protocols used for communication between servers and clients. Understanding their differences and use cases is essential for backend engineers.

### TCP

- Connection-oriented protocol
- Ensures reliable, in-order delivery of data
- Uses error checking and retransmission to prevent data loss
- Slower than UDP due to its overhead and error-checking mechanisms
- Suitable for applications requiring high reliability, such as HTTP, FTP, and email

Key TCP features:
  - Three-way handshake: Establishes a connection before data transfer
  - Flow control: Prevents sender from overwhelming the receiver
  - Congestion control: Adjusts data transmission rates to avoid network congestion
  - Acknowledgements: Confirms data has been received

### UDP

- Connectionless protocol
- Faster and lightweight compared to TCP
- No guarantee of data delivery or in-order arrival
- No error checking or retransmission, so data loss can occur
- Suitable for applications where speed is more important than reliability, such as video streaming, online gaming, and Voice over IP (VoIP)

Key UDP features:
  - No connection setup or teardown
  - No flow or congestion control
  - Minimal header overhead

As a backend engineer, choose the appropriate protocol based on the application's requirements. Use TCP for reliable and ordered data transfer, and UDP for faster and lightweight communication with acceptable data loss.
