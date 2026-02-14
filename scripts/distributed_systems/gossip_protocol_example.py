"""
Gossip protocol simulation.

Simulates a cluster of nodes that spread information using the gossip
(epidemic) protocol – the same approach used by Cassandra, Consul, and
other distributed systems for membership and failure detection.

No external dependencies required.

Usage:
    python gossip_protocol_example.py
"""

import random
import time


class Node:
    """A node in the gossip cluster."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data: dict[str, str] = {}
        self.peers: list["Node"] = []

    def receive(self, key: str, value: str, version: int):
        """Accept a key-value pair if its version is newer."""
        current = self.data.get(key)
        if current is None or current[1] < version:
            self.data[key] = (value, version)
            return True
        return False

    def gossip_round(self, fanout: int = 2):
        """Pick random peers and share all known data."""
        targets = random.sample(self.peers, min(fanout, len(self.peers)))
        spread_count = 0
        for peer in targets:
            for key, (value, version) in self.data.items():
                if peer.receive(key, value, version):
                    spread_count += 1
        return spread_count


def build_cluster(size: int) -> list[Node]:
    """Create a fully-connected cluster of nodes."""
    nodes = [Node(f"node-{i}") for i in range(size)]
    for node in nodes:
        node.peers = [n for n in nodes if n is not node]
    return nodes


def main():
    random.seed(42)
    cluster_size = 10
    fanout = 3

    print("=" * 55)
    print("Gossip Protocol Simulation")
    print("=" * 55)
    print(f"  Cluster size : {cluster_size}")
    print(f"  Fanout       : {fanout}")
    print()

    nodes = build_cluster(cluster_size)

    # Seed a piece of information on one node
    origin = nodes[0]
    origin.data["leader"] = ("node-0", 1)
    print(f"Round 0: '{origin.node_id}' knows leader=node-0")
    print(f"  Nodes with info: 1/{cluster_size}")
    print()

    # Run gossip rounds until everyone knows
    for round_num in range(1, 20):
        total_spread = 0
        for node in nodes:
            total_spread += node.gossip_round(fanout=fanout)

        informed = sum(1 for n in nodes if "leader" in n.data)
        print(f"Round {round_num}: {informed}/{cluster_size} nodes informed  "
              f"(new spreads this round: {total_spread})")

        if informed == cluster_size:
            print(f"\nAll nodes informed after {round_num} round(s)!")
            break
    else:
        informed = sum(1 for n in nodes if "leader" in n.data)
        print(f"\nAfter 20 rounds: {informed}/{cluster_size} nodes informed.")

    # Show final state
    print()
    print("Final cluster state:")
    for node in nodes:
        val = node.data.get("leader", ("unknown", 0))
        print(f"  {node.node_id}: leader={val[0]} (v{val[1]})")

    print()
    print("Key takeaway: Gossip spreads information in O(log N) rounds,")
    print("providing eventual consistency with high fault tolerance.")


if __name__ == "__main__":
    main()
