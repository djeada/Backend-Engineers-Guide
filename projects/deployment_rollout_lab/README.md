# Deployment Rollout Lab

This mini-project groups the deployment demos into a single lab for studying **safe production rollouts**.

## What you will practice

1. How rolling updates preserve availability while versions overlap
2. How canary releases reduce blast radius with gradual traffic shifts
3. Why health and readiness checks matter during cutovers

## Quick start

Run all demos at once:

```bash
cd projects/deployment_rollout_lab
./run.sh
```

Or run individual demos from the repository root:

```bash
python scripts/deployment/rolling_deploy_example.py
python scripts/deployment/canary_deploy_example.py
python scripts/deployment/health_check_example.py
```

## Suggested walkthrough

### 1. Rolling deployment

```bash
python scripts/deployment/rolling_deploy_example.py
```

Focus on:

- how many instances stay healthy during the update
- the trade-off between one-at-a-time and two-at-a-time rollout batches
- why backward compatibility matters when old and new versions coexist

Read next:

- [`scripts/deployment/rolling_deploy_example.py`](../../scripts/deployment/rolling_deploy_example.py)
- [`notes/09_deployment/`](../../notes/09_deployment/)

### 2. Canary deployment

```bash
python scripts/deployment/canary_deploy_example.py
```

Focus on:

- how the canary percentage increases over time
- how observed error rate drives promotion or rollback
- why automatic rollback is safer than waiting for a full outage

Read next:

- [`scripts/deployment/canary_deploy_example.py`](../../scripts/deployment/canary_deploy_example.py)

### 3. Readiness checks

```bash
python scripts/deployment/health_check_example.py
```

Focus on:

- the difference between liveness and readiness
- why a process can be alive but still not ready to serve traffic
- how orchestrators use readiness gates during rollout

Read next:

- [`scripts/deployment/health_check_example.py`](../../scripts/deployment/health_check_example.py)

## Extension ideas

- Change the canary error threshold and see how rollout decisions shift
- Increase `max_unavailable` in the rolling deployment example and compare availability
- Add a simulated dependency failure to the readiness example to model a bad deploy
