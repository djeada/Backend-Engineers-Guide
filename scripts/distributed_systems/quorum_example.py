"""
Read/write quorum calculation demonstration.

Shows how quorum settings (R + W > N) can guarantee overlapping replicas for
stronger consistency in distributed stores.

Usage:
    python quorum_example.py
"""


def has_quorum_overlap(n: int, r: int, w: int) -> bool:
    return r + w > n


def main():
    configs = [(3, 1, 1), (3, 2, 2), (5, 2, 3), (5, 3, 3)]
    for n, r, w in configs:
        overlap = has_quorum_overlap(n, r, w)
        print(f"N={n}, R={r}, W={w} -> overlap={overlap}")
    print("Key takeaway: choose R/W so reads and writes intersect.")


if __name__ == "__main__":
    main()
