"""
Middleware / request pipeline demonstration.

Builds a chain of middleware functions that wrap an HTTP-like request/response
cycle.  Each middleware can inspect or modify the request before passing it
to the next handler, and modify the response on the way back — the same
pattern used in Express.js, Django, and other web frameworks.

No external dependencies required.

Usage:
    python middleware_chain_example.py
"""

import time
import uuid


class Request:
    def __init__(self, method: str, path: str, headers: dict | None = None,
                 body: str = ""):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.context: dict = {}

    def __repr__(self):
        return f"{self.method} {self.path}"


class Response:
    def __init__(self, status: int = 200, body: str = "", headers: dict | None = None):
        self.status = status
        self.body = body
        self.headers = headers or {}

    def __repr__(self):
        return f"Response({self.status}, {self.body[:40]})"


def logging_middleware(request, next_handler):
    """Log every request and response."""
    start = time.perf_counter()
    print(f"    [LOG] --> {request}")
    response = next_handler(request)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"    [LOG] <-- {response.status} ({elapsed:.1f} ms)")
    return response


def request_id_middleware(request, next_handler):
    """Attach a unique request ID for tracing."""
    rid = uuid.uuid4().hex[:8]
    request.context["request_id"] = rid
    request.headers["X-Request-Id"] = rid
    response = next_handler(request)
    response.headers["X-Request-Id"] = rid
    return response


def auth_middleware(request, next_handler):
    """Reject requests without a valid Authorization header."""
    token = request.headers.get("Authorization", "")
    if not token.startswith("Bearer "):
        print(f"    [AUTH] rejected — missing or invalid token")
        return Response(status=401, body="Unauthorized")
    request.context["user"] = "authenticated-user"
    return next_handler(request)


def cors_middleware(request, next_handler):
    """Add CORS headers to every response."""
    response = next_handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    return response


class MiddlewareChain:
    """Compose a list of middleware around a final handler."""

    def __init__(self, handler):
        self.handler = handler
        self.middlewares: list = []

    def use(self, middleware):
        self.middlewares.append(middleware)

    def handle(self, request: Request) -> Response:
        chain = self.handler
        for mw in reversed(self.middlewares):
            prev = chain
            def make_next(m, nxt):
                return lambda req: m(req, nxt)
            chain = make_next(mw, prev)
        return chain(request)


def app_handler(request: Request) -> Response:
    """Application-level route handler."""
    if request.path == "/api/users":
        return Response(200, body='[{"id":1,"name":"Alice"}]')
    if request.path == "/api/health":
        return Response(200, body='{"status":"ok"}')
    return Response(404, body="Not Found")


def main():
    print("=" * 60)
    print("Middleware Chain Demo")
    print("=" * 60)
    print()

    chain = MiddlewareChain(app_handler)
    chain.use(logging_middleware)
    chain.use(request_id_middleware)
    chain.use(cors_middleware)
    chain.use(auth_middleware)

    print("--- Request 1: authenticated GET /api/users ---")
    req1 = Request("GET", "/api/users", headers={"Authorization": "Bearer tok123"})
    resp1 = chain.handle(req1)
    print(f"  Status: {resp1.status}")
    print(f"  Body:   {resp1.body}")
    print(f"  Headers: {resp1.headers}")
    print()

    print("--- Request 2: unauthenticated GET /api/users ---")
    req2 = Request("GET", "/api/users")
    resp2 = chain.handle(req2)
    print(f"  Status: {resp2.status}")
    print(f"  Body:   {resp2.body}")
    print()

    print("--- Request 3: authenticated GET /api/health ---")
    req3 = Request("GET", "/api/health", headers={"Authorization": "Bearer tok456"})
    resp3 = chain.handle(req3)
    print(f"  Status: {resp3.status}")
    print(f"  Body:   {resp3.body}")
    print()

    print("--- Request 4: authenticated GET /unknown ---")
    req4 = Request("GET", "/unknown", headers={"Authorization": "Bearer tok789"})
    resp4 = chain.handle(req4)
    print(f"  Status: {resp4.status}")
    print(f"  Body:   {resp4.body}")
    print()

    print("Key takeaway: middleware chains let you compose cross-cutting")
    print("concerns (logging, auth, CORS, tracing) as reusable layers")
    print("around your core request handler.")


if __name__ == "__main__":
    main()
