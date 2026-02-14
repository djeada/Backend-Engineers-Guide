"""
Health-check endpoint demonstration.

Implements a tiny HTTP server that exposes /health and /ready endpoints,
following the same patterns used in production deployments with
Kubernetes liveness/readiness probes and traditional monitoring systems.

No external dependencies required.

Usage:
    python health_check_example.py

The script runs a built-in self-test. You can also test manually with curl
while the server is running:
    curl http://localhost:8100/health
    curl http://localhost:8100/ready
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


# ---------- Simulated dependency checks ----------


def check_database() -> dict:
    """Simulate a database connectivity check."""
    return {"database": "ok", "latency_ms": 4}


def check_cache() -> dict:
    """Simulate a cache connectivity check."""
    return {"cache": "ok", "latency_ms": 1}


# ---------- Health-check handler ----------


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler that exposes health and readiness endpoints."""

    # Shared flag toggled by the startup simulation
    _ready = False

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/ready":
            self._handle_ready()
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_health(self):
        """Liveness probe – confirms the process is running."""
        self._send_json(200, {
            "status": "healthy",
            "uptime_seconds": round(time.monotonic() - _start_time, 1),
        })

    def _handle_ready(self):
        """Readiness probe – confirms the service can accept traffic."""
        if not HealthHandler._ready:
            self._send_json(503, {
                "status": "not ready",
                "reason": "service is still starting up",
            })
            return

        checks = {}
        checks.update(check_database())
        checks.update(check_cache())

        self._send_json(200, {
            "status": "ready",
            "checks": checks,
        })

    def log_message(self, fmt, *args):
        """Suppress default request logging to keep output clean."""
        pass


# ---------- Startup simulation ----------

_start_time = time.monotonic()


def _simulate_startup(delay: float):
    """Pretend the service needs time to warm up before it is ready."""
    time.sleep(delay)
    HealthHandler._ready = True
    print(f"  Service became ready after {delay}s warm-up.")


# ---------- Self-test ----------


def _self_test(port: int):
    """Hit both endpoints from within the process to show example output."""
    import urllib.request

    base = f"http://localhost:{port}"

    # Test /health
    print("\n  GET /health")
    with urllib.request.urlopen(f"{base}/health") as resp:
        body = json.loads(resp.read())
        print(f"    {resp.status} -> {json.dumps(body)}")

    # /ready should be 503 before warm-up finishes
    print("\n  GET /ready  (before warm-up)")
    try:
        urllib.request.urlopen(f"{base}/ready")
    except urllib.error.HTTPError as exc:
        body = json.loads(exc.read())
        print(f"    {exc.code} -> {json.dumps(body)}")

    # Wait for warm-up
    time.sleep(1.5)

    # /ready should be 200 after warm-up finishes
    print("\n  GET /ready  (after warm-up)")
    with urllib.request.urlopen(f"{base}/ready") as resp:
        body = json.loads(resp.read())
        print(f"    {resp.status} -> {json.dumps(body)}")


# ---------- Main ----------


def main():
    port = 8100

    print("=" * 55)
    print("Health-Check Endpoint Demo")
    print("=" * 55)
    print(f"  Listening on http://localhost:{port}")
    print("  Endpoints:  /health  (liveness)  /ready  (readiness)")
    print()

    server = HTTPServer(("localhost", port), HealthHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Simulate a 1-second warm-up before the service is ready
    startup_thread = threading.Thread(target=_simulate_startup, args=(1.0,))
    startup_thread.start()

    # Run the self-test so the script produces output without manual curl
    _self_test(port)

    server.shutdown()

    print()
    print("Key takeaway: Health and readiness endpoints let orchestrators")
    print("distinguish between a process that is alive and one that can serve traffic.")


if __name__ == "__main__":
    main()
