"""
Minimal REST API server using Python's built-in http.server module.

Demonstrates basic CRUD operations for a simple in-memory resource (items).
No external dependencies required.

Usage:
    python rest_api_example.py

Then test with curl:
    curl http://localhost:8000/items
    curl -X POST -d '{"name":"widget","price":9.99}' http://localhost:8000/items
    curl http://localhost:8000/items/1
    curl -X PUT -d '{"name":"widget","price":12.99}' http://localhost:8000/items/1
    curl -X DELETE http://localhost:8000/items/1
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# In-memory data store
items = {}
next_id = 1


class RESTHandler(BaseHTTPRequestHandler):
    """Simple handler implementing REST semantics for an items resource."""

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    # ---------- GET ----------
    def do_GET(self):
        if self.path == "/items":
            self._send_json(200, list(items.values()))
        elif self.path.startswith("/items/"):
            item_id = int(self.path.split("/")[-1])
            if item_id in items:
                self._send_json(200, items[item_id])
            else:
                self._send_json(404, {"error": "Item not found"})
        else:
            self._send_json(404, {"error": "Not found"})

    # ---------- POST ----------
    def do_POST(self):
        global next_id
        if self.path == "/items":
            body = self._read_body()
            item = {"id": next_id, **body}
            items[next_id] = item
            next_id += 1
            self._send_json(201, item)
        else:
            self._send_json(404, {"error": "Not found"})

    # ---------- PUT ----------
    def do_PUT(self):
        if self.path.startswith("/items/"):
            item_id = int(self.path.split("/")[-1])
            if item_id in items:
                body = self._read_body()
                items[item_id] = {"id": item_id, **body}
                self._send_json(200, items[item_id])
            else:
                self._send_json(404, {"error": "Item not found"})
        else:
            self._send_json(404, {"error": "Not found"})

    # ---------- DELETE ----------
    def do_DELETE(self):
        if self.path.startswith("/items/"):
            item_id = int(self.path.split("/")[-1])
            if item_id in items:
                del items[item_id]
                self._send_json(204, {})
            else:
                self._send_json(404, {"error": "Item not found"})
        else:
            self._send_json(404, {"error": "Not found"})


def main():
    server = HTTPServer(("localhost", 8000), RESTHandler)
    print("REST API server running on http://localhost:8000")
    print("Endpoints:")
    print("  GET    /items      - list all items")
    print("  POST   /items      - create an item")
    print("  GET    /items/<id> - get one item")
    print("  PUT    /items/<id> - update an item")
    print("  DELETE /items/<id> - delete an item")
    print("\nPress Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
