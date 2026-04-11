#!/usr/bin/env python3
"""
Webhook Receiver — catches and displays Grafana alert notifications.

WHAT THIS DOES:
  Listens for HTTP POST requests from Grafana's webhook contact point.
  When an alert fires or resolves, Grafana sends a JSON payload here.
  This script prints a human-readable summary so you can see exactly
  what Grafana is notifying about.

WHY THIS IS USEFUL:
  In production, this would be Slack, PagerDuty, or email. Here, we
  intercept the notification locally so students can:
    • See the exact JSON structure Grafana sends
    • Verify which alerts fire (and which are suppressed)
    • Understand the alert lifecycle: firing → resolved

GRAFANA ALERT PAYLOAD STRUCTURE:
  {
    "status": "firing" or "resolved",
    "alerts": [
      {
        "status": "firing",
        "labels": { "alertname": "...", "env": "uat", "tier": "parent", ... },
        "annotations": { "summary": "..." },
        "startsAt": "...",
        "endsAt": "..."
      }
    ]
  }

TIP: Run ./scripts/watch-alerts.sh to tail this receiver's log in real time.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingTCPServer


def timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def print_event(title: str, payload: dict | None = None) -> None:
    print(f"[{timestamp()}] {title}", flush=True)
    if payload is not None:
        print(json.dumps(payload, indent=2), flush=True)


def summarize_alerts(payload: dict) -> list[str]:
    """Extract a one-line summary per alert from the Grafana webhook payload."""
    alerts = payload.get("alerts") or []
    lines: list[str] = []
    for alert in alerts:
        labels = alert.get("labels") or {}
        annotations = alert.get("annotations") or {}
        lines.append(
            " | ".join(
                [
                    f"status={alert.get('status', 'unknown')}",
                    f"alertname={labels.get('alertname', '-')}",
                    f"env={labels.get('env', '-')}",
                    f"service={labels.get('service', '-')}",
                    f"dependency_group={labels.get('dependency_group', '-')}",
                    f"severity={labels.get('severity', '-')}",
                    f"tier={labels.get('tier', '-')}",
                    f"summary={annotations.get('summary', '-')}",
                ]
            )
        )
    return lines


class Handler(BaseHTTPRequestHandler):
    def _write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._write_json({"ok": True})
            return

        self._write_json({"ok": True, "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b""
        body_text = raw_body.decode("utf-8", errors="replace")
        parsed_body: dict | None = None

        try:
            parsed_body = json.loads(body_text) if body_text else {}
        except json.JSONDecodeError:
            parsed_body = None

        print_event(f"webhook notification received on {self.path}")
        if parsed_body is not None:
            for line in summarize_alerts(parsed_body):
                print(f"[{timestamp()}]   {line}", flush=True)
            print(json.dumps(parsed_body, indent=2), flush=True)
        else:
            print(body_text, flush=True)

        self._write_json({"ok": True})

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{timestamp()}] webhook: {self.address_string()} - {fmt % args}", flush=True)


class ReusableTCPServer(ThreadingTCPServer):
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    with ReusableTCPServer((args.host, args.port), Handler) as server:
        print_event(f"webhook receiver listening on http://{args.host}:{args.port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
