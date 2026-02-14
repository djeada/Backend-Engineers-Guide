"""
HTTP protocol request/response demonstration.

Starts a lightweight HTTP server in a background thread, then uses
urllib.request to make GET and POST requests.  Inspects status codes,
headers, and response bodies to illustrate how the HTTP protocol works
at the application layer.

No external dependencies required.

Usage:
    python http_request_example.py
"""

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.parse import parse_qs


# ---------------------------------------------------------------------------
# Simple HTTP request handler
# ---------------------------------------------------------------------------

class DemoHandler(BaseHTTPRequestHandler):
    """Handles GET and POST requests for demonstration purposes."""

    def do_GET(self):
        if self.path == "/":
            self._respond(200, {"message": "Hello from the demo server!", "method": "GET"})
        elif self.path == "/json":
            self._respond(200, {"items": [1, 2, 3], "type": "application/json"})
        elif self.path == "/headers":
            # Echo back the request headers the client sent
            headers_dict = {k: v for k, v in self.headers.items()}
            self._respond(200, {"your_headers": headers_dict})
        else:
            self._respond(404, {"error": "Not Found", "path": self.path})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()

        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = body
        elif "application/x-www-form-urlencoded" in content_type:
            parsed = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(body).items()}
        else:
            parsed = body

        self._respond(201, {"received": parsed, "method": "POST"})

    def _respond(self, status, data):
        payload = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Demo-Header", "backend-guide")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        """Suppress default stderr logging to keep demo output clean."""
        pass


# ---------------------------------------------------------------------------
# Helper: make a request and print the details
# ---------------------------------------------------------------------------

def make_request(label, url, method="GET", data=None, headers=None):
    print(f"--- {label} ---")
    print(f"  -> {method} {url}")

    req = Request(url, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
            print(f"     Header: {k}: {v}")

    body = None
    if data is not None:
        if isinstance(data, str):
            body = data.encode()
        else:
            body = json.dumps(data).encode()
            req.add_header("Content-Type", "application/json")

    with urlopen(req, body) as resp:
        status = resp.status
        resp_headers = dict(resp.getheaders())
        resp_body = resp.read().decode()

    print(f"  <- Status: {status}")
    print(f"     Content-Type: {resp_headers.get('Content-Type', 'N/A')}")
    print(f"     X-Demo-Header: {resp_headers.get('X-Demo-Header', 'N/A')}")
    print(f"     Body: {resp_body.strip()}")
    print()


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def demo_get_request(base):
    print("=" * 60)
    print("1) Simple GET Request")
    print("=" * 60)
    make_request("GET /", f"{base}/")


def demo_get_json(base):
    print("=" * 60)
    print("2) GET JSON Endpoint")
    print("=" * 60)
    make_request("GET /json", f"{base}/json")


def demo_custom_headers(base):
    print("=" * 60)
    print("3) GET with Custom Headers (echoed back)")
    print("=" * 60)
    make_request(
        "GET /headers with custom header",
        f"{base}/headers",
        headers={"X-Custom-Token": "my-secret-123"},
    )


def demo_post_json(base):
    print("=" * 60)
    print("4) POST with JSON Body")
    print("=" * 60)
    make_request(
        "POST /submit (JSON)",
        f"{base}/submit",
        method="POST",
        data={"username": "alice", "action": "login"},
    )


def demo_post_form(base):
    print("=" * 60)
    print("5) POST with Form-Encoded Body")
    print("=" * 60)
    make_request(
        "POST /submit (form)",
        f"{base}/submit",
        method="POST",
        data="username=bob&action=signup",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def demo_not_found(base):
    print("=" * 60)
    print("6) 404 Not Found")
    print("=" * 60)
    print(f"--- GET /nonexistent ---")
    print(f"  -> GET {base}/nonexistent")
    req = Request(f"{base}/nonexistent")
    try:
        urlopen(req)
    except Exception as exc:
        print(f"  <- Exception: {exc}")
    print()


def main():
    # Start the server on an ephemeral port
    server = HTTPServer(("127.0.0.1", 0), DemoHandler)
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Demo HTTP server listening on {base}\n")

    # Small pause to let the server settle
    time.sleep(0.1)

    demo_get_request(base)
    demo_get_json(base)
    demo_custom_headers(base)
    demo_post_json(base)
    demo_post_form(base)
    demo_not_found(base)

    server.shutdown()
    print("Server shut down.")
    print()
    print("Key takeaway: HTTP is a request/response protocol; clients specify")
    print("methods (GET, POST, …), headers, and bodies, while servers reply")
    print("with status codes, headers, and a response body.")


if __name__ == "__main__":
    main()
