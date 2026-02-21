"""
Consistent hashing ring for data partitioning.

Demonstrates how consistent hashing distributes keys across nodes using a
virtual-node ring, and shows that adding or removing a node only remaps a
small fraction of keys — unlike naive modulo hashing.

No external dependencies required.

Usage:
    python consistent_hashing_example.py
"""

import hashlib


class ConsistentHashRing:
    """Hash ring with configurable virtual nodes per physical node."""

    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: dict[int, str] = {}
        self.sorted_hashes: list[int] = []

    @staticmethod
    def _hash(key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        for i in range(self.virtual_nodes):
            h = self._hash(f"{node}#{i}")
            self.ring[h] = node
        self.sorted_hashes = sorted(self.ring)

    def remove_node(self, node: str):
        for i in range(self.virtual_nodes):
            h = self._hash(f"{node}#{i}")
            self.ring.pop(h, None)
        self.sorted_hashes = sorted(self.ring)

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise RuntimeError("hash ring is empty")
        h = self._hash(key)
        for node_hash in self.sorted_hashes:
            if h <= node_hash:
                return self.ring[node_hash]
        return self.ring[self.sorted_hashes[0]]


def distribute_keys(ring, keys):
    mapping: dict[str, list[str]] = {}
    for key in keys:
        node = ring.get_node(key)
        mapping.setdefault(node, []).append(key)
    return mapping


def find_node(dist, key):
    """Return the node that owns *key* in the given distribution."""
    for node, items in dist.items():
        if key in items:
            return node
    return None


def main():
    print("=" * 60)
    print("Consistent Hashing Ring Demo")
    print("=" * 60)
    print()

    keys = [f"user:{i}" for i in range(200)]

    ring = ConsistentHashRing(virtual_nodes=150)
    for node in ["node-A", "node-B", "node-C"]:
        ring.add_node(node)

    dist1 = distribute_keys(ring, keys)
    print("Initial distribution (3 nodes):")
    for node, items in sorted(dist1.items()):
        print(f"  {node}: {len(items)} keys")
    print()

    ring.add_node("node-D")
    dist2 = distribute_keys(ring, keys)
    print("After adding node-D (4 nodes):")
    for node, items in sorted(dist2.items()):
        print(f"  {node}: {len(items)} keys")

    moved = sum(1 for k in keys if find_node(dist1, k) != ring.get_node(k))
    print(f"\n  Keys remapped: {moved}/{len(keys)} ({moved/len(keys)*100:.1f}%)")
    print()

    ring.remove_node("node-B")
    dist3 = distribute_keys(ring, keys)
    print("After removing node-B (3 nodes):")
    for node, items in sorted(dist3.items()):
        print(f"  {node}: {len(items)} keys")
    print()

    print("Key takeaway: consistent hashing minimizes key movement when")
    print("nodes join or leave, making it ideal for distributed caches")
    print("and partitioned databases.")


if __name__ == "__main__":
    main()
