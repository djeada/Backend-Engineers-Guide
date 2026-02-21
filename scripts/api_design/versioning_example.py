"""
API versioning strategy demonstration.

Shows three common approaches to versioning a REST API — URL path
versioning, custom header versioning, and query-parameter versioning —
and how a backend router dispatches to the correct handler based on the
version indicator.

No external dependencies required.

Usage:
    python versioning_example.py
"""


# ---------- Version-specific handlers ----------

def users_v1():
    return [{"name": "Alice"}, {"name": "Bob"}]


def users_v2():
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]


def users_v3():
    return {
        "data": [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "viewer"},
        ],
        "meta": {"total": 2, "page": 1},
    }


HANDLERS = {"v1": users_v1, "v2": users_v2, "v3": users_v3}


# ---------- Strategy 1: URL path versioning ----------

def resolve_url_version(path: str):
    """Extract version from URL path like /v2/users."""
    parts = path.strip("/").split("/")
    if parts and parts[0] in HANDLERS:
        return parts[0]
    return None


# ---------- Strategy 2: Header versioning ----------

def resolve_header_version(headers: dict):
    """Extract version from a custom Accept-Version header."""
    return headers.get("Accept-Version")


# ---------- Strategy 3: Query param versioning ----------

def resolve_query_version(query_params: dict):
    """Extract version from ?version=v2 query parameter."""
    return query_params.get("version")


# ---------- Router ----------

def route(path: str, headers: dict | None = None,
          query_params: dict | None = None, default_version: str = "v1"):
    headers = headers or {}
    query_params = query_params or {}

    version = (
        resolve_url_version(path)
        or resolve_header_version(headers)
        or resolve_query_version(query_params)
        or default_version
    )

    handler = HANDLERS.get(version)
    if handler is None:
        return {"error": f"unsupported version '{version}'"}, 400
    return handler(), 200


def main():
    print("=" * 60)
    print("API Versioning Strategies Demo")
    print("=" * 60)
    print()

    print("--- Strategy 1: URL path versioning ---")
    for path in ["/v1/users", "/v2/users", "/v3/users"]:
        body, status = route(path)
        print(f"  {path}  => {status} {body}")
    print()

    print("--- Strategy 2: Custom header versioning ---")
    for ver in ["v1", "v2", "v3"]:
        body, status = route("/users", headers={"Accept-Version": ver})
        print(f"  Accept-Version: {ver}  => {status} {body}")
    print()

    print("--- Strategy 3: Query parameter versioning ---")
    for ver in ["v1", "v2", "v3"]:
        body, status = route("/users", query_params={"version": ver})
        print(f"  ?version={ver}  => {status} {body}")
    print()

    print("--- Fallback to default version ---")
    body, status = route("/users")
    print(f"  /users (no version)  => {status} {body}")
    print()

    print("--- Unknown version ---")
    body, status = route("/users", query_params={"version": "v99"})
    print(f"  ?version=v99  => {status} {body}")
    print()

    print("Comparison:")
    print("  URL path   (/v2/users)         — simple, cache-friendly, most common")
    print("  Header     (Accept-Version: v2) — clean URLs, less discoverable")
    print("  Query param (?version=v2)       — easy to test, pollutes cache keys")
    print()
    print("Key takeaway: pick one versioning strategy and apply it consistently;")
    print("URL path versioning is the most widely adopted approach.")


if __name__ == "__main__":
    main()
