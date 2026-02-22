"""
Schema migration versioning demonstration.

Shows how an application can track and apply sequential database schema
migrations using a simple version table in SQLite.  Each migration is a
small function that runs DDL statements and bumps the schema version.

No external dependencies required.

Usage:
    python migration_example.py
"""

import sqlite3


MIGRATIONS = []


def migration(version: int, description: str):
    """Decorator that registers a migration function."""
    def decorator(fn):
        MIGRATIONS.append((version, description, fn))
        return fn
    return decorator


@migration(1, "create users table")
def migration_v1(cur):
    cur.execute(
        "CREATE TABLE users ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  name TEXT NOT NULL"
        ")"
    )


@migration(2, "add email column to users")
def migration_v2(cur):
    cur.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")


@migration(3, "create orders table")
def migration_v3(cur):
    cur.execute(
        "CREATE TABLE orders ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  user_id INTEGER REFERENCES users(id),"
        "  total REAL NOT NULL DEFAULT 0.0"
        ")"
    )


@migration(4, "add created_at to orders")
def migration_v4(cur):
    cur.execute(
        "ALTER TABLE orders ADD COLUMN created_at TEXT"
        " DEFAULT (datetime('now'))"
    )


def current_version(cur) -> int:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    )
    if cur.fetchone() is None:
        cur.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
        cur.execute("INSERT INTO schema_version (version) VALUES (0)")
        return 0
    cur.execute("SELECT version FROM schema_version")
    row = cur.fetchone()
    return row[0] if row else 0


def apply_migrations(conn):
    cur = conn.cursor()
    ver = current_version(cur)
    conn.commit()
    print(f"  Current schema version: {ver}")

    pending = sorted((v, d, fn) for v, d, fn in MIGRATIONS if v > ver)
    if not pending:
        print("  No pending migrations.")
        return

    for version, description, fn in pending:
        print(f"  Applying v{version}: {description} …", end=" ")
        fn(cur)
        cur.execute("UPDATE schema_version SET version = ?", (version,))
        conn.commit()
        print("OK")

    print(f"  Schema version is now {current_version(cur)}")


def show_tables(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()]
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = [(r[1], r[2]) for r in cur.fetchall()]
        print(f"  {table}: {cols}")


def main():
    print("=" * 60)
    print("Schema Migration Demo")
    print("=" * 60)
    print()

    conn = sqlite3.connect(":memory:")

    print("--- First run: apply all migrations ---")
    apply_migrations(conn)
    print()

    print("--- Tables after migrations ---")
    show_tables(conn)
    print()

    print("--- Second run: no pending migrations ---")
    apply_migrations(conn)
    print()

    print("Key takeaway: versioned migrations let you evolve a database")
    print("schema incrementally and reproducibly across environments.")


if __name__ == "__main__":
    main()
