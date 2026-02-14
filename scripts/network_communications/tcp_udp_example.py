"""
TCP vs UDP socket demonstration.

Shows the difference between connection-oriented TCP and connectionless UDP
by running a simple echo server and client for each protocol.

No external dependencies required.

Usage:
    python tcp_udp_example.py
"""

import socket
import threading
import time


# --------------- TCP ---------------

def tcp_server(host, port, ready_event):
    """A simple TCP echo server that handles one connection."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(1)
        ready_event.set()
        conn, addr = srv.accept()
        with conn:
            data = conn.recv(1024)
            conn.sendall(data)


def tcp_client(host, port):
    """Send a message over TCP and receive the echo."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        message = b"Hello via TCP"
        s.sendall(message)
        response = s.recv(1024)
        return response


# --------------- UDP ---------------

def udp_server(host, port, ready_event, stop_event):
    """A simple UDP echo server."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as srv:
        srv.settimeout(1.0)
        srv.bind((host, port))
        ready_event.set()
        while not stop_event.is_set():
            try:
                data, addr = srv.recvfrom(1024)
                srv.sendto(data, addr)
            except socket.timeout:
                continue


def udp_client(host, port):
    """Send a message over UDP and receive the echo."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2.0)
        message = b"Hello via UDP"
        s.sendto(message, (host, port))
        response, _ = s.recvfrom(1024)
        return response


# --------------- Main ---------------

def main():
    host = "127.0.0.1"

    # --- TCP demonstration ---
    print("=" * 50)
    print("TCP (Transmission Control Protocol)")
    print("=" * 50)
    print("- Connection-oriented (three-way handshake)")
    print("- Reliable, ordered delivery")
    print("- Flow and congestion control")
    print()

    tcp_ready = threading.Event()
    tcp_port = 9001
    t = threading.Thread(target=tcp_server, args=(host, tcp_port, tcp_ready))
    t.start()
    tcp_ready.wait()

    response = tcp_client(host, tcp_port)
    print(f"  Sent:     b'Hello via TCP'")
    print(f"  Received: {response}")
    t.join()

    # --- UDP demonstration ---
    print()
    print("=" * 50)
    print("UDP (User Datagram Protocol)")
    print("=" * 50)
    print("- Connectionless (no handshake)")
    print("- No delivery guarantee or ordering")
    print("- Lower latency, less overhead")
    print()

    udp_ready = threading.Event()
    udp_stop = threading.Event()
    udp_port = 9002
    t = threading.Thread(target=udp_server, args=(host, udp_port, udp_ready, udp_stop))
    t.start()
    udp_ready.wait()

    response = udp_client(host, udp_port)
    print(f"  Sent:     b'Hello via UDP'")
    print(f"  Received: {response}")
    udp_stop.set()
    t.join()

    print()
    print("Key takeaway: TCP guarantees delivery at the cost of overhead;")
    print("UDP trades reliability for speed.")


if __name__ == "__main__":
    main()
