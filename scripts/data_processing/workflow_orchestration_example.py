"""
Workflow orchestration demonstration.

Implements a minimal DAG-based orchestrator that:
  - Defines tasks and their upstream dependencies
  - Builds a Directed Acyclic Graph (DAG)
  - Performs a topological sort to determine execution order
  - Runs tasks in topological order, respecting dependencies
  - Supports parallel execution of independent tasks
  - Handles task failures with configurable retries and exponential backoff
  - Simulates backfill execution across multiple date partitions

No external dependencies required.

Usage:
    python workflow_orchestration_example.py
"""

import time
import random
import threading
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


# ---------------------------------------------------------------------------
# Task state
# ---------------------------------------------------------------------------

class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()
    UPSTREAM_FAILED = auto()


# ---------------------------------------------------------------------------
# Task definition
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: str
    fn: Callable[[dict], None]
    upstream: list[str] = field(default_factory=list)
    retries: int = 2
    retry_delay: float = 0.1   # seconds (kept short for demo)

    # Runtime state (populated by the scheduler)
    state: TaskState = field(default=TaskState.PENDING, init=False)
    attempts: int = field(default=0, init=False)
    duration: float = field(default=0.0, init=False)
    error: str | None = field(default=None, init=False)


# ---------------------------------------------------------------------------
# DAG
# ---------------------------------------------------------------------------

class DAG:
    """A Directed Acyclic Graph of Task objects."""

    def __init__(self, dag_id: str):
        self.dag_id = dag_id
        self._tasks: dict[str, Task] = {}

    def add_task(self, task: Task) -> "DAG":
        self._tasks[task.task_id] = task
        return self

    def _validate(self) -> None:
        """Check that all upstream references exist and the graph is acyclic."""
        for task in self._tasks.values():
            for up in task.upstream:
                if up not in self._tasks:
                    raise ValueError(f"Task '{task.task_id}' references unknown upstream '{up}'")
        # Cycle detection via DFS
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            in_stack.add(node)
            for up in self._tasks[node].upstream:
                if up not in visited:
                    dfs(up)
                elif up in in_stack:
                    raise ValueError(f"Cycle detected involving task '{up}'")
            in_stack.remove(node)

        for tid in self._tasks:
            if tid not in visited:
                dfs(tid)

    def topological_sort(self) -> list[list[str]]:
        """
        Return tasks grouped into execution waves using Kahn's algorithm.
        All tasks within a wave have no mutual dependencies and can run in parallel.
        """
        self._validate()
        in_degree: dict[str, int] = {tid: 0 for tid in self._tasks}
        dependents: dict[str, list[str]] = defaultdict(list)

        for task in self._tasks.values():
            for up in task.upstream:
                in_degree[task.task_id] += 1
                dependents[up].append(task.task_id)

        queue: deque[str] = deque(tid for tid, deg in in_degree.items() if deg == 0)
        waves: list[list[str]] = []

        while queue:
            wave = list(queue)
            queue.clear()
            waves.append(wave)
            for tid in wave:
                for dep in dependents[tid]:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        return waves

    @property
    def tasks(self) -> dict[str, Task]:
        return self._tasks


# ---------------------------------------------------------------------------
# Scheduler / runner
# ---------------------------------------------------------------------------

class Scheduler:
    """Executes a DAG respecting dependencies, with retries and parallel waves."""

    def __init__(self, dag: DAG, context: dict | None = None, max_workers: int = 4):
        self._dag = dag
        self._context = context or {}
        self._max_workers = max_workers
        self._lock = threading.Lock()

    def _run_task(self, task: Task) -> None:
        """Execute a single task with retry/backoff logic."""
        task.state = TaskState.RUNNING
        delay = task.retry_delay

        for attempt in range(1, task.retries + 2):  # +1 for the initial attempt
            task.attempts = attempt
            start = time.perf_counter()
            try:
                task.fn(self._context)
                task.duration = time.perf_counter() - start
                task.state = TaskState.SUCCESS
                return
            except Exception as exc:
                task.duration = time.perf_counter() - start
                task.error = str(exc)
                if attempt <= task.retries:
                    print(
                        f"    [RETRY {attempt}/{task.retries}] "
                        f"'{task.task_id}' failed: {exc}  "
                        f"(waiting {delay:.1f}s)"
                    )
                    time.sleep(delay)
                    delay *= 2  # exponential backoff

        task.state = TaskState.FAILED

    def run(self) -> bool:
        """
        Execute all waves in topological order.
        Tasks in each wave run in parallel.
        Returns True if all tasks succeeded, False otherwise.
        """
        waves = self._dag.topological_sort()
        all_ok = True

        for wave_num, wave in enumerate(waves, start=1):
            # Mark tasks that have a failed upstream dependency as UPSTREAM_FAILED
            runnable = []
            for tid in wave:
                task = self._dag.tasks[tid]
                if any(
                    self._dag.tasks[up].state in (TaskState.FAILED, TaskState.UPSTREAM_FAILED)
                    for up in task.upstream
                ):
                    task.state = TaskState.UPSTREAM_FAILED
                    all_ok = False
                    print(f"  ↳ '{tid}': UPSTREAM_FAILED (skipped)")
                else:
                    runnable.append(task)

            if not runnable:
                continue

            print(f"\n  Wave {wave_num}: {[t.task_id for t in runnable]}")
            with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
                futures = {pool.submit(self._run_task, t): t for t in runnable}
                for future in as_completed(futures):
                    task = futures[future]
                    icon = "✓" if task.state == TaskState.SUCCESS else "✗"
                    print(
                        f"    {icon} '{task.task_id}': {task.state.name}"
                        f"  (attempts={task.attempts}, duration={task.duration:.3f}s)"
                        + (f"  error={task.error}" if task.error else "")
                    )
                    if task.state != TaskState.SUCCESS:
                        all_ok = False

        return all_ok


# ---------------------------------------------------------------------------
# Demo pipeline: ETL workflow
# ---------------------------------------------------------------------------

def make_etl_dag(fail_transform: bool = False) -> DAG:
    """
    Build a small ETL DAG:

      extract_crm  ──┐
                      ├──> join_sources ──> transform ──> load ──> notify
      extract_erp  ──┘          │
                                 └──> validate (runs in parallel with transform)
    """
    rng = random.Random(42)

    def extract_crm(ctx: dict) -> None:
        time.sleep(rng.uniform(0.02, 0.05))
        ctx["crm_records"] = 1_200
        print(f"      extracted {ctx['crm_records']:,} CRM records")

    def extract_erp(ctx: dict) -> None:
        time.sleep(rng.uniform(0.02, 0.05))
        ctx["erp_records"] = 850
        print(f"      extracted {ctx['erp_records']:,} ERP records")

    def join_sources(ctx: dict) -> None:
        time.sleep(rng.uniform(0.03, 0.06))
        ctx["joined_records"] = ctx["crm_records"] + ctx["erp_records"]
        print(f"      joined: {ctx['joined_records']:,} records")

    def validate(ctx: dict) -> None:
        time.sleep(rng.uniform(0.01, 0.03))
        ctx["validation_passed"] = True
        print(f"      validated {ctx['joined_records']:,} records – OK")

    def transform(ctx: dict) -> None:
        time.sleep(rng.uniform(0.04, 0.08))
        if fail_transform:
            raise RuntimeError("Schema mismatch in column 'amount'")
        ctx["transformed_records"] = int(ctx["joined_records"] * 0.92)
        print(f"      transformed to {ctx['transformed_records']:,} clean records")

    def load(ctx: dict) -> None:
        time.sleep(rng.uniform(0.02, 0.05))
        ctx["loaded"] = ctx["transformed_records"]
        print(f"      loaded {ctx['loaded']:,} records into warehouse")

    def notify(ctx: dict) -> None:
        print(f"      sent completion notification  (rows_loaded={ctx.get('loaded', 0):,})")

    dag = DAG("daily_etl")
    dag.add_task(Task("extract_crm", extract_crm))
    dag.add_task(Task("extract_erp", extract_erp))
    dag.add_task(Task("join_sources", join_sources, upstream=["extract_crm", "extract_erp"]))
    dag.add_task(Task("validate",    validate,    upstream=["join_sources"]))
    dag.add_task(Task("transform",   transform,   upstream=["join_sources"], retries=1))
    dag.add_task(Task("load",        load,        upstream=["transform", "validate"]))
    dag.add_task(Task("notify",      notify,      upstream=["load"]))
    return dag


# ---------------------------------------------------------------------------
# Backfill simulation
# ---------------------------------------------------------------------------

def simulate_backfill(dates: list[str]) -> None:
    print("\n" + "=" * 60)
    print("Backfill simulation")
    print("=" * 60)
    print(f"Re-processing {len(dates)} historical partitions sequentially...\n")
    for ds in dates:
        print(f"  Running DAG for partition: {ds}")
        ctx: dict = {"execution_date": ds}
        dag = make_etl_dag(fail_transform=False)
        scheduler = Scheduler(dag, context=ctx)
        ok = scheduler.run()
        status = "SUCCESS" if ok else "FAILED"
        print(f"  Partition {ds}: {status}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("Workflow Orchestration Demo")
    print("=" * 60)

    # --- 1. Happy-path run ---
    print("\n[1] Happy-path DAG run")
    dag = make_etl_dag(fail_transform=False)
    ctx: dict = {}
    waves = dag.topological_sort()
    print(f"  Execution waves: {waves}")
    scheduler = Scheduler(dag, context=ctx, max_workers=4)
    ok = scheduler.run()
    print(f"\n  Final status: {'ALL TASKS SUCCEEDED' if ok else 'SOME TASKS FAILED'}")

    # --- 2. Failure + upstream propagation ---
    print("\n" + "=" * 60)
    print("[2] Failure propagation run  (transform will fail after retries)")
    print("=" * 60)
    dag2 = make_etl_dag(fail_transform=True)
    scheduler2 = Scheduler(dag2, context={}, max_workers=4)
    ok2 = scheduler2.run()
    print(f"\n  Final status: {'ALL TASKS SUCCEEDED' if ok2 else 'SOME TASKS FAILED'}")
    failed = [t.task_id for t in dag2.tasks.values() if t.state == TaskState.FAILED]
    skipped = [t.task_id for t in dag2.tasks.values() if t.state == TaskState.UPSTREAM_FAILED]
    print(f"  Failed tasks          : {failed}")
    print(f"  Upstream-failed tasks : {skipped}")

    # --- 3. Backfill ---
    simulate_backfill(["2024-01-08", "2024-01-09", "2024-01-10"])

    # --- 4. Summary of concepts ---
    print("=" * 60)
    print("Key orchestration concepts demonstrated")
    print("=" * 60)
    print()
    print("  1. DAG definition     – tasks declare upstream dependencies;")
    print("     the scheduler derives execution order via topological sort.")
    print()
    print("  2. Parallel waves     – tasks with no mutual dependencies run")
    print("     concurrently, reducing total wall-clock time.")
    print()
    print("  3. Retries + backoff  – transient failures are retried with")
    print("     exponential delay before marking a task as FAILED.")
    print()
    print("  4. Failure propagation– downstream tasks are automatically")
    print("     marked UPSTREAM_FAILED when a dependency fails, preventing")
    print("     partial or inconsistent pipeline results.")
    print()
    print("  5. Backfill           – the same DAG runs for historical")
    print("     partitions to re-process or recover missing data.")


if __name__ == "__main__":
    main()
