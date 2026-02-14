"""
Reverse proxy simulation.

Demonstrates how a reverse proxy routes client requests to different
backend servers based on the URL path prefix.  Three lightweight HTTP
servers are spun up in threads:

  * Backend A — handles /api/* requests
  * Backend B — handles /static/* requests
  * Proxy     — the public-facing entry point that forwards requests

After the self-test completes, all servers are shut down automatically.

No external dependencies required.

Usage:
    python reverse_proxy_example.py
"""

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# Backend servers
# ---------------------------------------------------------------------------

class BackendAHandler(BaseHTTPRequestHandler):
    """Simulates an API backend."""

    def do_GET(self):
        payload = json.dumps({
            "backend": "A (API)",
            "path": self.path,
            "data": {"users": ["alice", "bob"]},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Backend", "A")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass


class BackendBHandler(BaseHTTPRequestHandler):
    """Simulates a static-file backend."""

    def do_GET(self):
        payload = json.dumps({
            "backend": "B (Static)",
            "path": self.path,
            "file": "index.html (simulated)",
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Backend", "B")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass


# ---------------------------------------------------------------------------
# Reverse proxy
# ---------------------------------------------------------------------------

class ReverseProxyHandler(BaseHTTPRequestHandler):
    """Routes requests to the appropriate backend by path prefix."""

    # Populated at runtime before the server starts
    routes = {}  # prefix -> backend base URL

    def do_GET(self):
        target = self._resolve_backend()
        if target is None:
            self._send_error(502, "No backend matched the request path")
            return
        self._forward(target)

    def _resolve_backend(self):
        for prefix, backend_url in self.routes.items():
            if self.path.startswith(prefix):
                return backend_url
        return None

    def _forward(self, backend_url):
        # Strip nothing — forward the full original path to the backend
        url = f"{backend_url}{self.path}"
        try:
            with urlopen(Request(url)) as resp:
                body = resp.read()
                status = resp.status
                headers = resp.getheaders()
        except Exception as exc:
            self._send_error(502, str(exc))
            return

        self.send_response(status)
        for name, value in headers:
            if name.lower() not in ("server", "date"):
                self.send_header(name, value)
        self.send_header("X-Proxied-By", "DemoReverseProxy")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code, message):
        payload = json.dumps({"error": message}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def start_server(handler_class, label):
    """Start an HTTP server on an ephemeral port and return (server, port)."""
    server = HTTPServer(("127.0.0.1", 0), handler_class)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"  {label} listening on 127.0.0.1:{port}")
    return server, port


def fetch(url):
    """GET a URL and return (status, headers_dict, body_str)."""
    with urlopen(Request(url)) as resp:
        return resp.status, dict(resp.getheaders()), resp.read().decode()


def print_response(label, status, headers, body):
    print(f"  <- Status: {status}")
    print(f"     X-Backend:   {headers.get('X-Backend', 'N/A')}")
    print(f"     X-Proxied-By: {headers.get('X-Proxied-By', 'N/A')}")
    print(f"     Body: {body.strip()}")
    print()


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def demo_api_route(proxy_base):
    print("=" * 60)
    print("1) Route /api/* → Backend A")
    print("=" * 60)
    url = f"{proxy_base}/api/users"
    print(f"  -> GET {url}")
    status, headers, body = fetch(url)
    print_response("API route", status, headers, body)


def demo_static_route(proxy_base):
    print("=" * 60)
    print("2) Route /static/* → Backend B")
    print("=" * 60)
    url = f"{proxy_base}/static/index.html"
    print(f"  -> GET {url}")
    status, headers, body = fetch(url)
    print_response("Static route", status, headers, body)


def demo_unknown_route(proxy_base):
    print("=" * 60)
    print("3) Unknown Path → 502 (no backend)")
    print("=" * 60)
    url = f"{proxy_base}/unknown/page"
    print(f"  -> GET {url}")
    try:
        status, headers, body = fetch(url)
    except Exception as exc:
        print(f"  <- Exception (expected): {exc}")
        print()
        return
    print_response("Unknown route", status, headers, body)


def main():
    print("Starting backend servers …\n")
    backend_a, port_a = start_server(BackendAHandler, "Backend A (API)")
    backend_b, port_b = start_server(BackendBHandler, "Backend B (Static)")

    # Configure proxy routing table
    ReverseProxyHandler.routes = {
        "/api": f"http://127.0.0.1:{port_a}",
        "/static": f"http://127.0.0.1:{port_b}",
    }

    proxy_server, proxy_port = start_server(ReverseProxyHandler, "Reverse Proxy")
    proxy_base = f"http://127.0.0.1:{proxy_port}"
    print()

    time.sleep(0.1)  # let servers settle

    demo_api_route(proxy_base)
    demo_static_route(proxy_base)
    demo_unknown_route(proxy_base)

    # Clean up
    proxy_server.shutdown()
    backend_a.shutdown()
    backend_b.shutdown()
    print("All servers shut down.")
    print()
    print("Key takeaway: A reverse proxy sits in front of backend servers,")
    print("routing requests by path (or host, headers, etc.) so clients see")
    print("a single entry point while traffic is distributed behind the scenes.")


if __name__ == "__main__":
    main()
