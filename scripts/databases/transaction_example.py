"""
SQLite transaction demonstration.

Shows ACID properties (Atomicity, Consistency, Isolation, Durability)
using Python's built-in sqlite3 module with an in-memory database.

No external dependencies required.

Usage:
    python transaction_example.py
"""

import sqlite3


def setup(conn):
    """Create a simple accounts table with seed data."""
    conn.execute(
        "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT, balance REAL)"
    )
    conn.execute("INSERT INTO accounts VALUES (1, 'Alice', 1000.00)")
    conn.execute("INSERT INTO accounts VALUES (2, 'Bob',    500.00)")
    conn.commit()


def show_balances(conn, label=""):
    """Print current balances."""
    if label:
        print(f"  [{label}]")
    for row in conn.execute("SELECT name, balance FROM accounts ORDER BY id"):
        print(f"    {row[0]}: ${row[1]:.2f}")
    print()


def demo_successful_transaction(conn):
    """Transfer money between accounts inside a transaction."""
    print("1) Successful transaction – transfer $200 from Alice to Bob")
    show_balances(conn, "Before")

    try:
        conn.execute("BEGIN")
        conn.execute("UPDATE accounts SET balance = balance - 200 WHERE id = 1")
        conn.execute("UPDATE accounts SET balance = balance + 200 WHERE id = 2")
        conn.commit()
        print("  Transaction committed.")
    except Exception:
        conn.rollback()
        print("  Transaction rolled back.")
    show_balances(conn, "After")


def demo_rollback(conn):
    """Demonstrate atomicity: if any part fails, the whole transaction rolls back."""
    print("2) Failed transaction – illustrating rollback (atomicity)")
    show_balances(conn, "Before")

    try:
        conn.execute("BEGIN")
        conn.execute("UPDATE accounts SET balance = balance - 5000 WHERE id = 1")
        # Simulate a business-rule check
        row = conn.execute("SELECT balance FROM accounts WHERE id = 1").fetchone()
        if row[0] < 0:
            raise ValueError("Insufficient funds")
        conn.commit()
        print("  Transaction committed.")
    except Exception as exc:
        conn.rollback()
        print(f"  Transaction rolled back: {exc}")
    show_balances(conn, "After (unchanged)")


def demo_isolation(db_path):
    """Show that uncommitted changes are invisible to other connections."""
    print("3) Isolation – uncommitted writes are invisible to other readers")

    conn_writer = sqlite3.connect(db_path, isolation_level="DEFERRED")
    conn_reader = sqlite3.connect(db_path, isolation_level="DEFERRED")

    setup(conn_writer)

    print("  Writer starts a transaction and updates Alice's balance...")
    conn_writer.execute("BEGIN")
    conn_writer.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")

    row = conn_reader.execute("SELECT balance FROM accounts WHERE id = 1").fetchone()
    print(f"  Reader sees Alice's balance as ${row[0]:.2f} (unchanged)")

    conn_writer.commit()
    row = conn_reader.execute("SELECT balance FROM accounts WHERE id = 1").fetchone()
    print(f"  After commit, reader sees Alice's balance as ${row[0]:.2f}")
    print()

    conn_writer.close()
    conn_reader.close()


def main():
    print("=" * 55)
    print("SQLite Transaction Demo – ACID Properties")
    print("=" * 55)
    print()

    conn = sqlite3.connect(":memory:")
    setup(conn)

    demo_successful_transaction(conn)
    demo_rollback(conn)
    conn.close()

    import tempfile
    import os

    tmp = os.path.join(tempfile.gettempdir(), "tx_demo.db")
    try:
        demo_isolation(tmp)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    print("Key takeaway: Transactions group operations into atomic units;")
    print("if anything fails the database remains consistent.")


if __name__ == "__main__":
    main()
