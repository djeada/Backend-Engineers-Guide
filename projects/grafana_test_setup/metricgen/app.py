#!/usr/bin/env python3
"""
Metric Generator — a fake service that exposes Prometheus metrics.

WHAT THIS DOES:
  Runs a tiny HTTP server with two endpoints:
    /metrics — Prometheus scrapes this to collect metric values
    /set     — You call this to simulate failures (set metric to 1) or recovery (0)

KEY CONCEPTS:
  • Prometheus Gauge: a metric type whose value can go up AND down (unlike a
    Counter which only goes up). Perfect for representing "is this service
    currently broken?" as 0 or 1.

  • Labels: key-value pairs attached to a metric that create separate time
    series per combination. For example, demo_parent_failure{env="uat",
    service="checkout", dependency_group="payments"} is a different series
    than demo_parent_failure{env="prod", ...}.

  • /metrics format: Prometheus expects a specific text format. The
    prometheus_client library handles this — we just define Gauges and
    set values, and generate_latest() produces the correct output.

DATA FLOW:
  1. You call /set?parent=1&child=0 to simulate a parent failure
  2. Prometheus scrapes /metrics every 15 seconds and stores the values
  3. Grafana queries Prometheus and evaluates alert rules against these values
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingTCPServer
from urllib.parse import parse_qs, urlparse

from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest


# ── Prometheus Gauges ────────────────────────────────────────────────
# Each Gauge creates a metric family. The labels list defines which
# dimensions are available — every unique combination of label values
# becomes a separate time series in Prometheus.

PARENT_FAILURE = Gauge(
    "demo_parent_failure",
    "Top-level dependency failure used for Grafana alert tests",
    ["env", "service", "dependency_group"],  # Label dimensions
)

CHILD_FAILURE = Gauge(
    "demo_child_failure",
    "Downstream service failure used for Grafana alert tests",
    ["env", "service", "dependency_group"],
)


def set_metric_values(env: str, service: str, dependency_group: str, parent: float, child: float) -> None:
    """Set both gauge values for a specific label combination."""
    PARENT_FAILURE.labels(
        env=env,
        service=service,
        dependency_group=dependency_group,
    ).set(parent)
    CHILD_FAILURE.labels(
        env=env,
        service=service,
        dependency_group=dependency_group,
    ).set(child)


def seed_defaults() -> None:
    """Initialize metrics to 0 so Prometheus sees them immediately.

    Without seeding, the metrics don't exist until someone calls /set,
    which means Grafana alert rules would see "no data" instead of a
    healthy 0 value.
    """
    set_metric_values("uat", "checkout", "payments", 0.0, 0.0)
    set_metric_values("prod", "checkout", "payments", 0.0, 0.0)


class Handler(BaseHTTPRequestHandler):
    def _write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._write_json(
                {
                    "ok": True,
                    "endpoints": [
                        "/metrics",
                        "/set?env=uat&service=checkout&dependency_group=payments&parent=1&child=1",
                    ],
                }
            )
            return

        # /metrics — the endpoint Prometheus scrapes
        # generate_latest() returns the Prometheus text exposition format
        if parsed.path == "/metrics":
            payload = generate_latest()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # /set — control plane to simulate failures
        # parent=1 means "top-level dependency is broken"
        # child=1  means "downstream service is broken"
        if parsed.path == "/set":
            params = parse_qs(parsed.query)
            env = params.get("env", ["uat"])[0]
            service = params.get("service", ["checkout"])[0]
            dependency_group = params.get("dependency_group", ["payments"])[0]
            parent = float(params.get("parent", ["0"])[0])
            child = float(params.get("child", ["0"])[0])

            set_metric_values(env, service, dependency_group, parent, child)
            self._write_json(
                {
                    "ok": True,
                    "env": env,
                    "service": service,
                    "dependency_group": dependency_group,
                    "parent": parent,
                    "child": child,
                }
            )
            return

        self._write_json({"ok": False, "error": "not found"}, HTTPStatus.NOT_FOUND)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"metricgen: {self.address_string()} - {fmt % args}", flush=True)


class ReusableTCPServer(ThreadingTCPServer):
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    seed_defaults()

    with ReusableTCPServer((args.host, args.port), Handler) as server:
        print(f"metricgen listening on http://{args.host}:{args.port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
