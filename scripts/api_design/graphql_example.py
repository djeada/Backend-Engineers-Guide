"""
GraphQL-like query engine demonstration.

Builds a small in-memory schema with types, fields, and resolver
functions, then shows how a client query selects only the fields it
needs — the core idea behind GraphQL.  Nested object queries and
field selection are both demonstrated.

No external dependencies required.

Usage:
    python graphql_example.py
"""

import json
import re
from textwrap import dedent


# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------

USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
}

POSTS = [
    {"id": 101, "authorId": 1, "title": "Intro to GraphQL", "body": "GraphQL is a query language..."},
    {"id": 102, "authorId": 1, "title": "Advanced Resolvers", "body": "Resolvers are functions..."},
    {"id": 103, "authorId": 2, "title": "REST vs GraphQL", "body": "Both approaches have merits..."},
]


# ---------------------------------------------------------------------------
# Resolvers — functions that know how to fetch each field / type
# ---------------------------------------------------------------------------

def resolve_user(_parent, args):
    """Return a single user by id."""
    uid = args.get("id")
    return USERS.get(uid)


def resolve_users(_parent, _args):
    """Return all users."""
    return list(USERS.values())


def resolve_posts_for_user(parent, _args):
    """Given a user dict, return their posts."""
    return [p for p in POSTS if p["authorId"] == parent["id"]]


def resolve_author_for_post(parent, _args):
    """Given a post dict, return its author."""
    return USERS.get(parent["authorId"])


# ---------------------------------------------------------------------------
# Schema definition (type → field → resolver mapping)
# ---------------------------------------------------------------------------

SCHEMA = {
    "Query": {
        "user": {"resolver": resolve_user, "type": "User"},
        "users": {"resolver": resolve_users, "type": "[User]"},
    },
    "User": {
        "id": {"resolver": None},
        "name": {"resolver": None},
        "email": {"resolver": None},
        "age": {"resolver": None},
        "posts": {"resolver": resolve_posts_for_user, "type": "[Post]"},
    },
    "Post": {
        "id": {"resolver": None},
        "title": {"resolver": None},
        "body": {"resolver": None},
        "author": {"resolver": resolve_author_for_post, "type": "User"},
    },
}


# ---------------------------------------------------------------------------
# Tiny query parser  (supports: field, field(arg:val), field { sub })
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"""
    (\w+)          |   # identifier
    (\()           |   # open paren
    (\))           |   # close paren
    (\{)           |   # open brace
    (\})           |   # close brace
    (:)            |   # colon
    (\d+)          |   # integer literal
    ("(?:[^"]*)")  |   # string literal
    (,)                # comma (ignored)
    """,
    re.VERBOSE,
)


def _tokenize(text):
    tokens = []
    for m in _TOKEN_RE.finditer(text):
        tok = m.group().strip()
        if tok and tok != ",":
            tokens.append(tok)
    return tokens


def _parse_fields(tokens, pos):
    """Parse a brace-delimited set of field selections.

    Returns (list_of_field_nodes, new_pos).
    Each node: {"name": str, "args": dict, "children": list}
    """
    fields = []
    while pos < len(tokens) and tokens[pos] != "}":
        name = tokens[pos]
        pos += 1
        args = {}
        children = []

        # optional arguments  e.g. (id: 1)
        if pos < len(tokens) and tokens[pos] == "(":
            pos += 1  # skip '('
            while tokens[pos] != ")":
                key = tokens[pos]
                pos += 1  # skip key
                pos += 1  # skip ':'
                val = tokens[pos]
                pos += 1
                # coerce integers and strip quotes
                if val.isdigit():
                    val = int(val)
                elif val.startswith('"'):
                    val = val.strip('"')
                args[key] = val
            pos += 1  # skip ')'

        # optional sub-selection  e.g. { name email }
        if pos < len(tokens) and tokens[pos] == "{":
            pos += 1  # skip '{'
            children, pos = _parse_fields(tokens, pos)
            pos += 1  # skip '}'

        fields.append({"name": name, "args": args, "children": children})
    return fields, pos


def parse_query(query_string):
    """Parse a simplified GraphQL query string into an AST."""
    tokens = _tokenize(query_string)
    # expect leading '{' … '}'
    if tokens[0] == "{":
        tokens = tokens[1:]
    if tokens[-1] == "}":
        tokens = tokens[:-1]
    fields, _ = _parse_fields(tokens, 0)
    return fields


# ---------------------------------------------------------------------------
# Executor — walks the AST and calls resolvers
# ---------------------------------------------------------------------------

def execute_field(parent, field_node, parent_type):
    """Resolve a single field, possibly with children."""
    name = field_node["name"]
    schema_field = SCHEMA.get(parent_type, {}).get(name)
    if schema_field is None:
        return parent.get(name) if isinstance(parent, dict) else None

    resolver = schema_field["resolver"]
    if resolver is None:
        # scalar — just pick from parent dict
        return parent.get(name) if isinstance(parent, dict) else None

    result = resolver(parent, field_node["args"])

    child_type = schema_field.get("type", "")
    is_list = child_type.startswith("[")
    inner_type = child_type.strip("[]")

    if field_node["children"]:
        if is_list and isinstance(result, list):
            return [
                {c["name"]: execute_field(item, c, inner_type) for c in field_node["children"]}
                for item in result
            ]
        if isinstance(result, dict):
            return {c["name"]: execute_field(result, c, inner_type) for c in field_node["children"]}

    return result


def execute(query_string):
    """Parse and execute a GraphQL-like query, returning JSON-ready data."""
    ast = parse_query(query_string)
    data = {}
    for field_node in ast:
        data[field_node["name"]] = execute_field({}, field_node, "Query")
    return {"data": data}


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------

def run_query(label, query):
    print(f"--- {label} ---")
    print(f"  Query:\n{indent(query, 4)}")
    result = execute(query)
    print(f"  Result:\n{indent(json.dumps(result, indent=2), 4)}")
    print()


def indent(text, n):
    pad = " " * n
    return "\n".join(pad + line for line in text.strip().splitlines())


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------

def demo_field_selection():
    """Show that the client picks only the fields it wants."""
    print("=" * 60)
    print("1) Field Selection — ask for only name and email")
    print("=" * 60)
    run_query(
        "Select specific fields",
        dedent("""\
        {
            user(id: 1) {
                name
                email
            }
        }"""),
    )


def demo_all_fields():
    """Show fetching all scalar fields of a type."""
    print("=" * 60)
    print("2) All Scalar Fields")
    print("=" * 60)
    run_query(
        "All user fields",
        dedent("""\
        {
            user(id: 2) {
                id
                name
                email
                age
            }
        }"""),
    )


def demo_nested_query():
    """Show a nested query — user → posts."""
    print("=" * 60)
    print("3) Nested Query — user with their posts")
    print("=" * 60)
    run_query(
        "Nested: user.posts",
        dedent("""\
        {
            user(id: 1) {
                name
                posts {
                    title
                }
            }
        }"""),
    )


def demo_deep_nested():
    """Show deeper nesting — users → posts → author (back-reference)."""
    print("=" * 60)
    print("4) Deep Nesting — users → posts → author")
    print("=" * 60)
    run_query(
        "Deep nesting",
        dedent("""\
        {
            users {
                name
                posts {
                    title
                    author {
                        email
                    }
                }
            }
        }"""),
    )


def main():
    demo_field_selection()
    demo_all_fields()
    demo_nested_query()
    demo_deep_nested()
    print("Key takeaway: GraphQL lets clients request exactly the fields they")
    print("need in a single query, reducing over-fetching and under-fetching")
    print("compared to fixed REST endpoints.")


if __name__ == "__main__":
    main()
