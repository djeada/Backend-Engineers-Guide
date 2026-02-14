"""
Rolling deployment simulation.

Simulates a cluster of server instances being upgraded one at a time
(rolling update strategy).  At each step the demo shows which instances
run the old version and which run the new version, demonstrating how
availability is maintained throughout the upgrade.

No external dependencies required.

Usage:
    python rolling_deploy_example.py
"""

import time


# ---------- Cluster model ----------

class Instance:
    """Represents a single server instance in the cluster."""

    def __init__(self, instance_id: str, version: str):
        self.instance_id = instance_id
        self.version = version
        self.status = "running"  # running | draining | deploying | starting

    def __repr__(self):
        return f"{self.instance_id}(v{self.version}, {self.status})"


class Cluster:
    """A simple model of a deployment cluster."""

    def __init__(self, size: int, initial_version: str):
        self.instances = [
            Instance(f"inst-{i+1:02d}", initial_version) for i in range(size)
        ]

    def running_count(self):
        return sum(1 for i in self.instances if i.status == "running")

    def version_summary(self):
        versions = {}
        for inst in self.instances:
            versions.setdefault(inst.version, 0)
            versions[inst.version] += 1
        return versions


# ---------- Visual helpers ----------

STATUS_ICONS = {
    "running": "●",
    "draining": "◐",
    "deploying": "↻",
    "starting": "◑",
}

VERSION_COLORS = {}  # version -> label


def render_cluster(cluster: Cluster, step: str):
    """Print a visual representation of the cluster state."""
    print(f"  [{step}]")
    row = "  "
    for inst in cluster.instances:
        icon = STATUS_ICONS.get(inst.status, "?")
        row += f" {icon} v{inst.version:<4} |"
    print(row)
    summary = cluster.version_summary()
    parts = [f"v{v}: {c}" for v, c in sorted(summary.items())]
    running = cluster.running_count()
    total = len(cluster.instances)
    print(f"  Versions: {', '.join(parts)}  |  "
          f"Healthy: {running}/{total}  "
          f"({running/total*100:.0f}% available)")
    print()


# ---------- Rolling deploy logic ----------

def rolling_deploy(cluster: Cluster, new_version: str, max_unavailable: int = 1):
    """
    Perform a rolling deployment across the cluster.

    Upgrades *max_unavailable* instances at a time, ensuring the rest
    remain available to serve traffic.
    """
    print(f"  Strategy     : Rolling update")
    print(f"  New version  : v{new_version}")
    print(f"  Max unavail. : {max_unavailable}")
    print()

    render_cluster(cluster, "initial state")

    step = 0
    idx = 0
    while idx < len(cluster.instances):
        batch = cluster.instances[idx : idx + max_unavailable]
        step += 1

        # Phase 1 – Drain connections
        for inst in batch:
            inst.status = "draining"
        render_cluster(cluster, f"step {step}a – drain {[b.instance_id for b in batch]}")

        # Phase 2 – Deploy new version
        for inst in batch:
            inst.status = "deploying"
            inst.version = new_version
        render_cluster(cluster, f"step {step}b – deploy v{new_version}")

        # Phase 3 – Start and health-check
        for inst in batch:
            inst.status = "starting"
        render_cluster(cluster, f"step {step}c – starting")

        # Phase 4 – Instance is healthy
        for inst in batch:
            inst.status = "running"
        render_cluster(cluster, f"step {step}d – healthy ✓")

        idx += max_unavailable


# ---------- Main ----------

def main():
    print("=" * 62)
    print("Rolling Deployment Simulation")
    print("=" * 62)
    print()

    # --- Scenario 1: one-at-a-time ---
    print("-" * 62)
    print("Scenario 1: 6-instance cluster, one at a time")
    print("-" * 62)
    print()

    cluster = Cluster(size=6, initial_version="1.0")
    rolling_deploy(cluster, new_version="2.0", max_unavailable=1)

    # --- Scenario 2: two-at-a-time ---
    print("-" * 62)
    print("Scenario 2: 6-instance cluster, two at a time")
    print("-" * 62)
    print()

    cluster2 = Cluster(size=6, initial_version="2.0")
    rolling_deploy(cluster2, new_version="3.0", max_unavailable=2)

    # --- Comparison ---
    print("=" * 62)
    print("Rolling vs other deployment strategies")
    print("=" * 62)
    print()
    print("  Rolling update:")
    print("    + Zero-downtime (some instances always healthy)")
    print("    + Easy rollback (stop and redeploy previous version)")
    print("    - Mixed versions during deploy (must be backward-compatible)")
    print()
    print("  Blue-Green deploy:")
    print("    + Instant switch-over, no mixed versions")
    print("    - Requires 2× infrastructure capacity")
    print()
    print("  Canary deploy:")
    print("    + Gradual traffic shift; observe errors early")
    print("    - More complex routing and monitoring setup")
    print()

    print("Key takeaway: Rolling deployments upgrade instances incrementally,")
    print("keeping the cluster available throughout — but require backward-")
    print("compatible changes since old and new versions coexist briefly.")


if __name__ == "__main__":
    main()
