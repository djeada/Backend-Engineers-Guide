"""
Connection pool behavior demonstration.

Shows acquiring/releasing fixed-size pooled connections and what happens when
capacity is exhausted.

Usage:
    python connection_pool_example.py
"""

from queue import Queue, Empty


def main():
    pool = Queue(maxsize=2)
    pool.put("conn-1")
    pool.put("conn-2")

    c1 = pool.get_nowait()
    c2 = pool.get_nowait()
    print("Acquired:", c1, c2)

    try:
        pool.get_nowait()
    except Empty:
        print("Pool exhausted: no free connections")

    pool.put(c1)
    print("Released:", c1)
    print("Acquired again:", pool.get_nowait())
    print("Key takeaway: pooling caps concurrent DB connection usage.")


if __name__ == "__main__":
    main()
