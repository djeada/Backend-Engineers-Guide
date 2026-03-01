"""
Mini GraphQL-like query engine (interactive demo).

What this shows:
- Field selection: clients ask for exactly the fields they need.
- Nested selections: user -> posts -> author, etc.
- Aliases: query the same field multiple times with different names.
- Variables: pass values separately from the query text.
- Introspection (tiny subset): __schema / __type.
- Tracing + profiling: see which resolvers/"DB" lookups run (and when they DON'T).
- REST comparison: a fixed-shape endpoint vs a tailored GraphQL response.

No external dependencies required.

Usage:
    python graphql_demo.py            # interactive REPL
    python graphql_demo.py --demo 1   # run a built-in demo
    python graphql_demo.py --query '{ users { name } }'
    python graphql_demo.py --query '{ user(id:$id){name} }' --vars '{"id": 1}'
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# In-memory "DB"
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


def _ctx_inc(ctx: Dict[str, Any], key: str, n: int = 1) -> None:
    ctx.setdefault("stats", {}).setdefault(key, 0)
    ctx["stats"][key] += n


def db_get_user(ctx: Dict[str, Any], user_id: int) -> Optional[Dict[str, Any]]:
    """
    Simulate a DB lookup. If ctx["cache"] is True, cache users per request.
    Stats:
      - db_get_user_requests: how many times a resolver asked for a user
      - db_get_user_fetches: how many real "DB fetches" happened
      - db_get_user_cache_hits: how many were served from the per-request cache
    """
    _ctx_inc(ctx, "db_get_user_requests")
    if ctx.get("cache", True):
        cache = ctx.setdefault("user_cache", {})
        if user_id in cache:
            _ctx_inc(ctx, "db_get_user_cache_hits")
            return cache[user_id]

    _ctx_inc(ctx, "db_get_user_fetches")
    user = USERS.get(user_id)
    if ctx.get("cache", True):
        ctx["user_cache"][user_id] = user
    return user


def db_list_users(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    _ctx_inc(ctx, "db_list_users_fetches")
    return list(USERS.values())


def db_list_posts_for_author(ctx: Dict[str, Any], author_id: int) -> List[Dict[str, Any]]:
    _ctx_inc(ctx, "db_list_posts_for_author_fetches")
    return [p for p in POSTS if p["authorId"] == author_id]


# ---------------------------------------------------------------------------
# Schema (type -> fields -> definition)
# ---------------------------------------------------------------------------

Resolver = Callable[[Any, Dict[str, Any], Dict[str, Any]], Any]


@dataclass(frozen=True)
class FieldDef:
    type_: str
    resolver: Optional[Resolver] = None
    args: Optional[Dict[str, str]] = None
    description: str = ""


SCHEMA: Dict[str, Dict[str, FieldDef]] = {
    "Query": {
        "user": FieldDef(
            type_="User",
            resolver=lambda _p, a, ctx: db_get_user(ctx, int(a["id"])),
            args={"id": "ID!"},
            description="Fetch one user by id.",
        ),
        "users": FieldDef(
            type_="[User!]!",
            resolver=lambda _p, _a, ctx: db_list_users(ctx),
            description="List all users.",
        ),
        # Tiny introspection subset:
        "__schema": FieldDef(type_="__Schema!", resolver=lambda _p, _a, _ctx: build_schema_obj()),
        "__type": FieldDef(
            type_="__Type",
            resolver=lambda _p, a, _ctx: build_type_obj(a.get("name")),
            args={"name": "String!"},
        ),
    },
    "User": {
        "id": FieldDef(type_="ID!"),
        "name": FieldDef(type_="String!"),
        "email": FieldDef(type_="String!"),
        "age": FieldDef(type_="Int!"),
        "posts": FieldDef(
            type_="[Post!]!",
            resolver=lambda p, _a, ctx: db_list_posts_for_author(ctx, p["id"]),
            description="Posts written by this user.",
        ),
    },
    "Post": {
        "id": FieldDef(type_="ID!"),
        "title": FieldDef(type_="String!"),
        "body": FieldDef(type_="String!"),
        "author": FieldDef(
            type_="User!",
            resolver=lambda p, _a, ctx: db_get_user(ctx, p["authorId"]),
            description="Author of the post.",
        ),
    },
    # Introspection object shapes (simplified):
    "__Schema": {
        "types": FieldDef(type_="[__Type!]!"),
        "queryType": FieldDef(type_="__Type!"),
    },
    "__Type": {
        "name": FieldDef(type_="String!"),
        "fields": FieldDef(type_="[__Field!]!"),
    },
    "__Field": {
        "name": FieldDef(type_="String!"),
        "type": FieldDef(type_="String!"),
        "args": FieldDef(type_="[__Arg!]!"),
    },
    "__Arg": {
        "name": FieldDef(type_="String!"),
        "type": FieldDef(type_="String!"),
    },
}


def build_type_obj(type_name: Optional[str]) -> Optional[Dict[str, Any]]:
    if not type_name or type_name not in SCHEMA:
        return None
    fields = []
    for fname, fdef in SCHEMA[type_name].items():
        args = []
        if fdef.args:
            for aname, atype in fdef.args.items():
                args.append({"name": aname, "type": atype})
        fields.append({"name": fname, "type": fdef.type_, "args": args})
    return {"name": type_name, "fields": fields}


def build_schema_obj() -> Dict[str, Any]:
    # Build each type once (avoid re-building in list comprehension)
    types = []
    for t in sorted(SCHEMA.keys()):
        obj = build_type_obj(t)
        if obj is not None:
            types.append(obj)
    return {"queryType": build_type_obj("Query"), "types": types}


# ---------------------------------------------------------------------------
# Tokenizer + parser (subset)
# Supports: selection sets, args, aliases, variables ($x), comments (# ...), commas
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"""
    \s*(?:
        (?P<comment>\#.*) |
        (?P<var>\$[_A-Za-z]\w*) |
        (?P<name>[_A-Za-z]\w*) |
        (?P<int>-?\d+) |
        (?P<string>"([^"\\]|\\.)*") |
        (?P<punc>[(){}:,])
    )
    """,
    re.VERBOSE,
)


def tokenize(text: str) -> List[str]:
    tokens: List[str] = []
    for m in _TOKEN_RE.finditer(text):
        if m.group("comment"):
            continue
        tok = m.group(0).strip()
        if tok:
            tokens.append(tok)
    return tokens


FieldNode = Dict[str, Any]


def parse_query(query: str) -> List[FieldNode]:
    tokens = tokenize(query)
    # Ignore optional "query Foo($x:...)" header; just jump to first "{"
    try:
        start = tokens.index("{")
    except ValueError:
        raise ValueError("Expected '{' to start a selection set.")
    pos = start + 1
    fields, pos = _parse_fields(tokens, pos)
    if pos >= len(tokens) or tokens[pos] != "}":
        raise ValueError("Expected '}' to close the top-level selection set.")
    return fields


def _parse_fields(tokens: List[str], pos: int) -> Tuple[List[FieldNode], int]:
    fields: List[FieldNode] = []
    while pos < len(tokens) and tokens[pos] != "}":
        if tokens[pos] == ",":
            pos += 1
            continue

        # alias support: alias : name
        first = tokens[pos]
        pos += 1
        alias = None
        name = first
        if pos + 1 < len(tokens) and tokens[pos] == ":" and re.match(r"^[_A-Za-z]\w*$", tokens[pos + 1]):
            alias = first
            name = tokens[pos + 1]
            pos += 2

        args: Dict[str, Any] = {}
        children: List[FieldNode] = []

        if pos < len(tokens) and tokens[pos] == "(":
            pos += 1
            while pos < len(tokens) and tokens[pos] != ")":
                if tokens[pos] == ",":
                    pos += 1
                    continue
                key = tokens[pos]
                pos += 1
                if pos >= len(tokens) or tokens[pos] != ":":
                    raise ValueError("Expected ':' in argument list.")
                pos += 1
                if pos >= len(tokens):
                    raise ValueError("Expected argument value.")
                val_tok = tokens[pos]
                pos += 1
                args[key] = _coerce_literal(val_tok)
            if pos >= len(tokens) or tokens[pos] != ")":
                raise ValueError("Expected ')' to close argument list.")
            pos += 1

        if pos < len(tokens) and tokens[pos] == "{":
            pos += 1
            children, pos = _parse_fields(tokens, pos)
            if pos >= len(tokens) or tokens[pos] != "}":
                raise ValueError("Expected '}' to close a selection set.")
            pos += 1

        fields.append({"name": name, "alias": alias, "args": args, "children": children})
    return fields, pos


def _coerce_literal(tok: str) -> Any:
    if tok.startswith('"') and tok.endswith('"'):
        # basic unescape for \" and \\ (enough for demos)
        s = tok[1:-1]
        s = s.replace(r"\\", "\\").replace(r"\"", '"')
        return s
    if tok.startswith("$"):
        return {"$var": tok[1:]}
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    return tok  # identifier literal (rare in this demo)


def pretty_ast(fields: List[FieldNode], indent: int = 0) -> str:
    pad = " " * indent
    out: List[str] = []
    for f in fields:
        head = f'{f["alias"] + ": " if f["alias"] else ""}{f["name"]}'
        if f["args"]:
            head += "(" + ", ".join(
                f"{k}: {json.dumps(v)}" if not isinstance(v, dict) else f"{k}: ${v['$var']}"
                for k, v in f["args"].items()
            ) + ")"
        out.append(pad + head)
        if f["children"]:
            out.append(pad + "{")
            out.append(pretty_ast(f["children"], indent + 2))
            out.append(pad + "}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Executor (with tracing + basic validation)
# ---------------------------------------------------------------------------

def is_list_type(t: str) -> bool:
    return t.strip().startswith("[")


def inner_type(t: str) -> str:
    # "[User!]!" -> "User"
    t = t.strip()
    if t.startswith("["):
        t = t[1:]
        t = t.split("]")[0]
    return t.replace("!", "").strip()


def is_non_null(t: str) -> bool:
    return t.strip().endswith("!")


def base_type(t: str) -> str:
    return t.replace("!", "").strip()


def execute(
    query: str,
    *,
    variables: Optional[Dict[str, Any]] = None,
    trace: bool = False,
    profile: bool = False,
    cache: bool = True,
) -> Dict[str, Any]:
    variables = variables or {}
    ctx: Dict[str, Any] = {
        "errors": [],
        "variables": variables,
        "trace": trace,
        "profile": profile,
        "cache": cache,
        "stats": {},
        "timings_ms": {},
    }
    start = time.perf_counter()
    try:
        ast = parse_query(query)
        data: Dict[str, Any] = {}
        for field_node in ast:
            out_name = field_node["alias"] or field_node["name"]
            data[out_name] = _execute_field(parent=None, parent_type="Query", node=field_node, ctx=ctx, path=[out_name], depth=0)
        result: Dict[str, Any] = {"data": data}
    except Exception as e:
        ctx["errors"].append({"message": f"Parse/Execution error: {e}", "path": []})
        result = {"data": None}

    elapsed = (time.perf_counter() - start) * 1000.0
    if ctx["errors"]:
        result["errors"] = ctx["errors"]
    if profile:
        result.setdefault("extensions", {})
        result["extensions"]["stats"] = ctx.get("stats", {})
        result["extensions"]["timings_ms"] = ctx.get("timings_ms", {})
        result["extensions"]["total_ms"] = round(elapsed, 3)
    return result


def _trace(ctx: Dict[str, Any], depth: int, msg: str) -> None:
    if not ctx.get("trace"):
        return
    print("  " * depth + msg)


def _time_call(ctx: Dict[str, Any], key: str, fn: Callable[[], Any]) -> Any:
    if not ctx.get("profile"):
        return fn()
    t0 = time.perf_counter()
    try:
        return fn()
    finally:
        ms = (time.perf_counter() - t0) * 1000.0
        ctx["timings_ms"][key] = round(ctx["timings_ms"].get(key, 0.0) + ms, 3)


def _error(ctx: Dict[str, Any], message: str, path: List[Any]) -> None:
    ctx["errors"].append({"message": message, "path": path})


def _resolve_args(field_def: FieldDef, raw_args: Dict[str, Any], ctx: Dict[str, Any], path: List[Any]) -> Optional[Dict[str, Any]]:
    args_out: Dict[str, Any] = {}
    expected = field_def.args or {}
    # required args
    for name, typ in expected.items():
        if name not in raw_args:
            if is_non_null(typ):
                _error(ctx, f"Missing required argument '{name}' (type {typ}).", path)
                return None
            continue

        val = raw_args[name]
        if isinstance(val, dict) and "$var" in val:
            var_name = val["$var"]
            if var_name not in ctx["variables"]:
                _error(ctx, f"Variable '${var_name}' was not provided.", path)
                return None
            val = ctx["variables"][var_name]

        coerced = _coerce_arg_value(val, typ, ctx, path + [name])
        if coerced is None and is_non_null(typ):
            return None
        args_out[name] = coerced
    return args_out


def _coerce_arg_value(val: Any, typ: str, ctx: Dict[str, Any], path: List[Any]) -> Any:
    t = base_type(typ)
    if val is None:
        return None
    if t == "Int":
        if isinstance(val, int):
            return val
        _error(ctx, f"Expected Int for argument, got {type(val).__name__}.", path)
        return None
    if t == "String":
        if isinstance(val, str):
            return val
        _error(ctx, f"Expected String for argument, got {type(val).__name__}.", path)
        return None
    if t == "ID":
        if isinstance(val, (int, str)):
            return val
        _error(ctx, f"Expected ID for argument, got {type(val).__name__}.", path)
        return None
    return val


def _execute_field(parent: Any, parent_type: str, node: FieldNode, ctx: Dict[str, Any], path: List[Any], depth: int) -> Any:
    name = node["name"]

    # meta field: __typename (works on any object)
    if name == "__typename":
        return parent_type

    type_fields = SCHEMA.get(parent_type)
    if type_fields is None:
        _error(ctx, f"Unknown parent type '{parent_type}'.", path)
        return None

    field_def = type_fields.get(name)
    if field_def is None:
        _error(ctx, f"Cannot query field '{name}' on type '{parent_type}'.", path)
        return None

    # Enforce selection set for object/list types (GraphQL rule)
    if node["children"] == [] and (inner_type(field_def.type_) in SCHEMA or base_type(field_def.type_) in SCHEMA or is_list_type(field_def.type_)):
        if inner_type(field_def.type_) in SCHEMA or base_type(field_def.type_) in SCHEMA:
            # scalars don't need selection sets, objects do
            if inner_type(field_def.type_) not in ("String", "Int", "ID") and base_type(field_def.type_) not in ("String", "Int", "ID"):
                _error(ctx, f"Field '{name}' of type '{field_def.type_}' must have a selection of subfields.", path)
                return None

    # scalars
    if field_def.resolver is None:
        _trace(ctx, depth, f"• pick {parent_type}.{name}")
        if isinstance(parent, dict):
            return parent.get(name)
        return None

    # resolver fields
    resolved_args = _resolve_args(field_def, node["args"], ctx, path)
    if resolved_args is None:
        return None

    _ctx_inc(ctx, "resolver_calls")
    _trace(ctx, depth, f"↳ resolve {parent_type}.{name} args={resolved_args}")

    def _call():
        return field_def.resolver(parent, resolved_args, ctx)

    result = _time_call(ctx, f"{parent_type}.{name}", _call)

    # If no children, return raw result
    if not node["children"]:
        return result

    child_t = inner_type(field_def.type_)

    # list
    if is_list_type(field_def.type_):
        if result is None:
            return None
        if not isinstance(result, list):
            _error(ctx, f"Resolver for {parent_type}.{name} returned non-list for list type.", path)
            return None
        out = []
        for i, item in enumerate(result):
            obj: Dict[str, Any] = {}
            for c in node["children"]:
                out_name = c["alias"] or c["name"]
                obj[out_name] = _execute_field(item, child_t, c, ctx, path + [i, out_name], depth + 1)
            out.append(obj)
        return out

    # object
    if isinstance(result, dict):
        obj = {}
        for c in node["children"]:
            out_name = c["alias"] or c["name"]
            obj[out_name] = _execute_field(result, child_t, c, ctx, path + [out_name], depth + 1)
        return obj

    return result


# ---------------------------------------------------------------------------
# Demo queries + UI
# ---------------------------------------------------------------------------

DEMOS: List[Tuple[str, str, Optional[Dict[str, Any]]]] = [
    (
        "Field selection: only name + email",
        dedent(
            """\
            {
              user(id: 1) {
                name
                email
              }
            }
            """
        ),
        None,
    ),
    (
        "Nested: user -> posts (title only)",
        dedent(
            """\
            {
              user(id: 1) {
                name
                posts {
                  title
                }
              }
            }
            """
        ),
        None,
    ),
    (
        "Deep nesting: users -> posts -> author",
        dedent(
            """\
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
            }
            """
        ),
        None,
    ),
    (
        "Aliases: fetch two users in one round trip",
        dedent(
            """\
            {
              alice: user(id: 1) { name email }
              bob: user(id: 2) { name }
            }
            """
        ),
        None,
    ),
    (
        "Variables: provide id separately",
        dedent(
            """\
            query GetUser($id: ID!) {
              user(id: $id) { id name }
            }
            """
        ),
        {"id": 3},
    ),
    (
        "Introspection: ask the schema about User",
        dedent(
            """\
            {
              __type(name: "User") {
                name
                fields {
                  name
                  type
                  args { name type }
                }
              }
            }
            """
        ),
        None,
    ),
    (
        "Errors: unknown field + missing required arg",
        dedent(
            """\
            {
              user {
                name
                nope
              }
            }
            """
        ),
        None,
    ),
]


def indent(text: str, n: int) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in text.strip().splitlines())


def print_schema_compact() -> None:
    print("Schema (compact):")
    for tname in sorted(SCHEMA.keys()):
        print(f"  type {tname} {{")
        for fname, fdef in SCHEMA[tname].items():
            args = ""
            if fdef.args:
                args = "(" + ", ".join(f"{k}: {v}" for k, v in fdef.args.items()) + ")"
            print(f"    {fname}{args}: {fdef.type_}")
        print("  }")
    print()


def rest_like_user_payload(user_id: int) -> Dict[str, Any]:
    """A fixed-shape REST-ish endpoint: always returns user + all fields + posts + author for each post."""
    u = USERS.get(user_id)
    if not u:
        return {"error": "not found"}
    posts = [p for p in POSTS if p["authorId"] == user_id]
    full_posts = []
    for p in posts:
        full_posts.append({**p, "author": USERS.get(p["authorId"])})
    return {**u, "posts": full_posts}


def demo_rest_vs_graphql() -> None:
    gql = dedent(
        """\
        {
          user(id: 1) { name }
        }
        """
    )
    rest = rest_like_user_payload(1)
    gql_res = execute(gql)
    rest_json = json.dumps(rest, separators=(",", ":"), ensure_ascii=False)
    gql_json = json.dumps(gql_res["data"], separators=(",", ":"), ensure_ascii=False)

    print("=" * 72)
    print("REST vs GraphQL (payload size + over-fetching)")
    print("=" * 72)
    print("REST-like fixed endpoint (always returns a big blob):")
    print(indent(json.dumps(rest, indent=2), 2))
    print(f"  payload bytes: {len(rest_json.encode('utf-8'))}\n")
    print("GraphQL query (returns only what you asked for):")
    print(indent(gql, 2))
    print(indent(json.dumps(gql_res, indent=2), 2))
    print(f"  payload bytes: {len(gql_json.encode('utf-8'))}\n")
    saved = len(rest_json.encode("utf-8")) - len(gql_json.encode("utf-8"))
    print(f"Saved ~{saved} bytes in this tiny example.\n")


def run_demo(i: int, trace: bool, show_ast: bool, profile: bool, cache: bool) -> None:
    title, q, vars_ = DEMOS[i]
    print("=" * 72)
    print(f"Demo {i + 1}: {title}")
    print("=" * 72)
    print("Query:")
    print(indent(q, 2))
    if vars_:
        print(f"Variables: {json.dumps(vars_)}")
    if show_ast:
        ast = parse_query(q)
        print("\nAST:")
        print(indent(pretty_ast(ast), 2))
    print("\nResult:")
    res = execute(q, variables=vars_ or {}, trace=trace, profile=profile, cache=cache)
    print(indent(json.dumps(res, indent=2), 2))
    print()


def read_query_multiline(first_line: str = "") -> str:
    """
    Read a query from stdin:
    - Start with first_line (if provided).
    - Continue until braces are balanced AND the user enters a blank line.
    """
    lines: List[str] = []
    if first_line.strip():
        lines.append(first_line.rstrip("\n"))

    balance = first_line.count("{") - first_line.count("}")
    while True:
        try:
            line = input("... " if lines else "").rstrip("\n")
        except EOFError:
            break
        if not line.strip() and balance <= 0 and lines:
            break
        lines.append(line)
        balance += line.count("{") - line.count("}")
    return "\n".join(lines).strip()


def repl() -> None:
    print("Mini GraphQL-like demo REPL")
    print("Type :help for commands. Paste a query starting with '{' or 'query'.\n")

    settings = {
        "trace": False,
        "show_ast": False,
        "profile": False,
        "cache": True,
        "variables": {},
        "last_query": None,
    }

    def _show_settings() -> None:
        print(
            "Settings: "
            f"trace={settings['trace']}  ast={settings['show_ast']}  "
            f"profile={settings['profile']}  cache={settings['cache']}  "
            f"vars={json.dumps(settings['variables'])}"
        )

    def _toggle(key: str, arg: str) -> None:
        if arg in ("toggle", ""):
            settings[key] = not settings[key]
        elif arg in ("on", "true", "1"):
            settings[key] = True
        elif arg in ("off", "false", "0"):
            settings[key] = False
        else:
            raise ValueError("use on|off|toggle")

    while True:
        try:
            line = input("gql> ").strip()
        except EOFError:
            print()
            return

        if not line:
            continue

        if line.startswith(":"):
            cmd, *rest = line[1:].split(" ", 1)
            arg = rest[0].strip() if rest else ""

            if cmd in ("quit", "exit", "q"):
                return

            if cmd == "help":
                print(dedent("""\
                    Commands:
                      :help                  show this help
                      :examples              list demos
                      :demo N                run demo N (1-based)
                      :schema                print schema (compact)
                      :type NAME             introspection: show one type
                      :vars JSON             set variables (e.g. :vars {"id": 1})
                      :trace on|off|toggle   resolver trace
                      :ast on|off|toggle     print parsed AST before executing
                      :profile on|off|toggle include stats + timings in response
                      :cache on|off|toggle   per-request caching for db_get_user
                      :rest                  show REST-vs-GraphQL payload comparison
                      :run                   enter a multi-line query
                      :last                  rerun last query
                      :settings              show current settings
                      :quit                  exit
                    """))
                continue

            if cmd == "settings":
                _show_settings()
                continue

            if cmd == "examples":
                for i, (title, _q, _v) in enumerate(DEMOS, start=1):
                    print(f"  {i}. {title}")
                print("  (Run one with :demo N)\n")
                continue

            if cmd == "demo":
                if not arg.isdigit():
                    print("Usage: :demo N")
                    continue
                n = int(arg) - 1
                if not (0 <= n < len(DEMOS)):
                    print(f"N must be between 1 and {len(DEMOS)}")
                    continue
                run_demo(n, trace=settings["trace"], show_ast=settings["show_ast"], profile=settings["profile"], cache=settings["cache"])
                continue

            if cmd == "schema":
                print_schema_compact()
                continue

            if cmd == "type":
                name = arg or "User"
                q = dedent(
                    f"""\
                    {{
                      __type(name: "{name}") {{
                        name
                        fields {{ name type args {{ name type }} }}
                      }}
                    }}
                    """
                )
                settings["last_query"] = q
                if settings["show_ast"]:
                    print("AST:")
                    print(indent(pretty_ast(parse_query(q)), 2))
                res = execute(q, variables=settings["variables"], trace=settings["trace"], profile=settings["profile"], cache=settings["cache"])
                print(indent(json.dumps(res, indent=2), 2))
                print()
                continue

            if cmd == "vars":
                if not arg:
                    print(f"Current vars: {json.dumps(settings['variables'])}")
                    continue
                try:
                    obj = json.loads(arg)
                    if not isinstance(obj, dict):
                        raise ValueError("vars must be a JSON object")
                    settings["variables"] = obj
                    print("Variables updated.")
                except Exception as e:
                    print(f"Invalid vars: {e}")
                continue

            if cmd in ("trace", "ast", "profile", "cache"):
                key = {"trace": "trace", "ast": "show_ast", "profile": "profile", "cache": "cache"}[cmd]
                try:
                    _toggle(key, arg)
                    _show_settings()
                except ValueError:
                    print(f"Usage: :{cmd} on|off|toggle")
                continue

            if cmd == "rest":
                demo_rest_vs_graphql()
                continue

            if cmd == "run":
                print("Paste a query. End with a blank line.\n")
                q = read_query_multiline()
                if not q:
                    print("(empty)\n")
                    continue
                settings["last_query"] = q
                if settings["show_ast"]:
                    print("AST:")
                    print(indent(pretty_ast(parse_query(q)), 2))
                res = execute(q, variables=settings["variables"], trace=settings["trace"], profile=settings["profile"], cache=settings["cache"])
                print(indent(json.dumps(res, indent=2), 2))
                print()
                continue

            if cmd == "last":
                q = settings.get("last_query")
                if not q:
                    print("No previous query.\n")
                    continue
                if settings["show_ast"]:
                    print("AST:")
                    print(indent(pretty_ast(parse_query(q)), 2))
                res = execute(q, variables=settings["variables"], trace=settings["trace"], profile=settings["profile"], cache=settings["cache"])
                print(indent(json.dumps(res, indent=2), 2))
                print()
                continue

            print(f"Unknown command: :{cmd}. Try :help")
            continue

        # If they paste a query directly at the prompt:
        if line.startswith("{") or line.startswith("query"):
            q = read_query_multiline(first_line=line)
            settings["last_query"] = q
            if settings["show_ast"]:
                print("AST:")
                print(indent(pretty_ast(parse_query(q)), 2))
            res = execute(q, variables=settings["variables"], trace=settings["trace"], profile=settings["profile"], cache=settings["cache"])
            print(indent(json.dumps(res, indent=2), 2))
            print()
            continue

        print("Unrecognized input. Paste a query starting with '{' or type :help.\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Mini GraphQL-like query engine demo (interactive).")
    ap.add_argument("--demo", type=int, help="Run built-in demo N (1-based).")
    ap.add_argument("--query", type=str, help="Run a single query string.")
    ap.add_argument("--vars", type=str, default="{}", help="Variables as JSON (for $vars).")
    ap.add_argument("--trace", action="store_true", help="Trace resolver execution.")
    ap.add_argument("--ast", action="store_true", help="Print parsed AST.")
    ap.add_argument("--profile", action="store_true", help="Add timings/stats to output (extensions).")
    ap.add_argument("--no-cache", action="store_true", help="Disable per-request db_get_user caching.")
    ap.add_argument("--schema", action="store_true", help="Print schema and exit.")
    ap.add_argument("--rest", action="store_true", help="Run REST-vs-GraphQL comparison and exit.")
    args = ap.parse_args()

    if args.schema:
        print_schema_compact()
        return

    if args.rest:
        demo_rest_vs_graphql()
        return

    try:
        variables = json.loads(args.vars) if args.vars else {}
        if not isinstance(variables, dict):
            raise ValueError("vars must be a JSON object")
    except Exception as e:
        raise SystemExit(f"--vars must be JSON object: {e}")

    cache = not args.no_cache

    if args.demo:
        n = args.demo - 1
        if not (0 <= n < len(DEMOS)):
            raise SystemExit(f"--demo must be between 1 and {len(DEMOS)}")
        run_demo(n, trace=args.trace, show_ast=args.ast, profile=args.profile, cache=cache)
        return

    if args.query:
        if args.ast:
            print("AST:")
            print(indent(pretty_ast(parse_query(args.query)), 2))
        res = execute(args.query, variables=variables, trace=args.trace, profile=args.profile, cache=cache)
        print(json.dumps(res, indent=2))
        return

    repl()


if __name__ == "__main__":
    main()
