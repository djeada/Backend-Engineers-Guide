# Distributed Coordination Lab

This mini-project groups the distributed-systems demos into a lab for **leadership**, **causality**, **replica overlap**, and **partitioning**.

## What you will practice

1. How a cluster elects a leader after failures and recoveries
2. How vector clocks capture causal ordering between distributed events
3. How read/write quorums improve consistency guarantees
4. How consistent hashing minimizes key movement when nodes change

## Quick start

Run these commands from the repository root:

```bash
python scripts/distributed_systems/leader_election_example.py
python scripts/distributed_systems/vector_clock_example.py
python scripts/distributed_systems/quorum_example.py
python scripts/distributed_systems/consistent_hashing_example.py
```

## Suggested walkthrough

### 1. Leader election

```bash
python scripts/distributed_systems/leader_election_example.py
```

Focus on:

- how the highest live process becomes leader
- how the cluster reacts when a leader crashes
- why recovered nodes may reclaim leadership

Read next:

- [`scripts/distributed_systems/leader_election_example.py`](../../scripts/distributed_systems/leader_election_example.py)
- [`notes/10_distributed_systems/01_coordination_services.md`](../../notes/10_distributed_systems/01_coordination_services.md)

### 2. Vector clocks and causality

```bash
python scripts/distributed_systems/vector_clock_example.py
```

Focus on:

- how send and receive events update logical clocks
- when two events are concurrent instead of causally ordered
- why causal metadata is useful in collaborative or replicated systems

Read next:

- [`scripts/distributed_systems/vector_clock_example.py`](../../scripts/distributed_systems/vector_clock_example.py)
- [`notes/10_distributed_systems/04_concurrent_writes.md`](../../notes/10_distributed_systems/04_concurrent_writes.md)

### 3. Quorum overlap

```bash
python scripts/distributed_systems/quorum_example.py
```

Focus on:

- why `R + W > N` matters
- how overlapping replicas improve read freshness
- where quorum trades stronger consistency for extra latency

Read next:

- [`scripts/distributed_systems/quorum_example.py`](../../scripts/distributed_systems/quorum_example.py)
- [`notes/10_distributed_systems/03_linearizability.md`](../../notes/10_distributed_systems/03_linearizability.md)

### 4. Consistent hashing

```bash
python scripts/distributed_systems/consistent_hashing_example.py
```

Focus on:

- how keys map to a ring of nodes
- why adding a node remaps only part of the keyspace
- where this pattern appears in caches and partitioned databases

Read next:

- [`scripts/distributed_systems/consistent_hashing_example.py`](../../scripts/distributed_systems/consistent_hashing_example.py)
- [`notes/10_distributed_systems/06_algorithms_summary.md`](../../notes/10_distributed_systems/06_algorithms_summary.md)

## Extension ideas

- Add a split-brain scenario to the leader-election demo
- Compare multiple quorum settings for the same replica count
- Reduce the number of virtual nodes and see how consistent-hash balance changes
