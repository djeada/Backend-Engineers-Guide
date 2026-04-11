# Cluster Membership Lab

This mini-project uses a gossip simulation to study **membership propagation** and **eventual consistency** inside a distributed cluster.

## What you will practice

1. How gossip spreads state across a cluster without a central coordinator
2. Why fanout influences propagation speed
3. How versioned updates keep newer information from being overwritten

## Quick start

Run the demo:

```bash
cd projects/cluster_membership_lab
./run.sh
```

Or run directly from the repository root:

```bash
python scripts/distributed_systems/gossip_protocol_example.py
```

## Suggested walkthrough

### 1. Watch information spread round by round

```bash
python scripts/distributed_systems/gossip_protocol_example.py
```

Focus on:

- how one seeded update reaches the rest of the cluster
- why random peer selection still converges quickly
- how eventual consistency differs from immediate coordination

Read next:

- [`scripts/distributed_systems/gossip_protocol_example.py`](../../scripts/distributed_systems/gossip_protocol_example.py)
- [`notes/10_distributed_systems/02_gossip_protocol.md`](../../notes/10_distributed_systems/02_gossip_protocol.md)

## Extension ideas

- Increase cluster size and compare how many rounds convergence takes
- Reduce gossip fanout and measure the trade-off between network cost and propagation speed
- Add a second, newer update mid-simulation and verify the higher version wins
