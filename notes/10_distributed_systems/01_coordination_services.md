## Coordination Services in Distributed Systems

In large-scale distributed systems, many processes, microservices, or nodes must work together while running on different machines. These systems need a reliable way to agree on shared state, detect failures, elect leaders, coordinate ownership, and distribute configuration.

Coordination services solve these problems by providing strongly consistent primitives such as distributed locks, leader election, service discovery, membership tracking, and configuration storage.

Common coordination systems include **Apache ZooKeeper**, **etcd**, and **HashiCorp Consul**. These tools prevent application developers from having to implement low-level distributed consensus logic themselves.

Example coordination need:

```json id="1c6f3l"
{
  "cluster": "job-scheduler",
  "nodes": ["node-a", "node-b", "node-c"],
  "requirement": "only one node should run the daily billing job"
}
```

Without coordination, two nodes might run the same job at the same time. With coordination, the cluster can elect one active leader and make the others wait.

### Why Coordination Services Matter

Distributed systems are hard because failures are partial. One node may crash while others continue. A network partition may isolate part of the cluster. Two services may both believe they are responsible for the same task. A configuration update may reach some instances but not others.

Coordination services help manage these problems using a consistent store backed by a consensus protocol.

Typical problems they address include:

1. **Leader Election** Choose one node as the leader for a task or subsystem.
2. **Distributed Locking** Ensure only one process performs a critical operation at a time.
3. **Configuration Management** Store shared configuration in one consistent place.
4. **Service Discovery** Let services register themselves and discover other services dynamically.
5. **Membership and Heartbeats** Track which nodes are alive and which have disappeared.

Example output from a coordination service:

```json id="ygd9rb"
{
  "leader": "node-a",
  "followers": ["node-b", "node-c"],
  "clusterState": "healthy",
  "quorum": true
}
```

Coordination services are often small but critical. If they fail or are misused, the systems depending on them may become unavailable or inconsistent.

## Common Coordination Problems

Coordination problems appear whenever multiple nodes must make decisions together. The main goal is to avoid conflicting actions and keep the system predictable under failure.

### Leader Election

Leader election selects one node to act as the primary coordinator for a task. The leader may schedule jobs, assign partitions, manage cluster metadata, or perform writes that must not happen concurrently.

Follower nodes remain ready to take over if the leader fails.

```text id="djsyt1"
+-------------------+
|  Node A Leader    |
+-------------------+
         ^
         |
         | Leader election
         |
+-------------------+    +-------------------+
| Node B Follower   |    | Node C Follower   |
+-------------------+    +-------------------+

When Node A fails, Node B or Node C is elected as the new leader.
```

Example leader state:

```json id="vm1wa7"
{
  "electionPath": "/services/scheduler/leader",
  "currentLeader": "node-a",
  "leaderLeaseTtlSeconds": 10
}
```

Example failover result:

```json id="48m83r"
{
  "oldLeader": "node-a",
  "failureDetected": true,
  "newLeader": "node-b"
}
```

Leader election prevents split-brain behavior where multiple nodes think they are in charge.

### Distributed Locking

A distributed lock ensures that only one node can perform a critical operation at a time. This is useful for tasks such as running migrations, rebuilding indexes, processing a singleton job, or updating a shared resource.

Example:

```text id="dh4xjl"
Node A attempts lock: success
Node B attempts lock: waits
Node C attempts lock: waits

Node A releases lock.
Node B may acquire it next.
```

Example lock record:

```json id="q55r7c"
{
  "lockName": "nightly-billing-job",
  "owner": "node-a",
  "leaseExpiresInSeconds": 8
}
```

Distributed locks should usually be lease-based. If the lock owner crashes, the lease expires and another node can acquire the lock. Without leases, stale locks can block progress forever.

### Service Discovery

Service discovery lets services find each other dynamically. Instead of hard-coding IP addresses, service instances register their location and health status in a registry.

Example service registration:

```json id="5ks6vs"
{
  "service": "payments-api",
  "instanceId": "payments-api-3",
  "address": "10.0.2.15",
  "port": 8080,
  "health": "passing"
}
```

Example discovery result:

```json id="5t4440"
{
  "service": "payments-api",
  "healthyInstances": [
    "10.0.2.14:8080",
    "10.0.2.15:8080"
  ]
}
```

Service discovery is important in environments where instances come and go frequently, such as Kubernetes, auto-scaling groups, and microservice platforms.

### Configuration Management

Coordination services can store shared configuration values such as feature flags, database connection strings, service limits, or runtime tuning parameters.

Example configuration key:

```text id="fdnm4o"
/app/config/max_retries
```

Example value:

```json id="7pmrqh"
{
  "max_retries": 5
}
```

Applications can watch configuration keys and reload settings when values change.

Example config update:

```json id="z3v7l9"
{
  "key": "/app/config/max_retries",
  "oldValue": 3,
  "newValue": 5,
  "watchersNotified": true
}
```

This avoids redeploying every service instance for small runtime configuration changes.

### Popular Coordination Systems

Different coordination systems provide similar core ideas but differ in APIs, data models, operational style, and ecosystem.

#### Apache ZooKeeper

Apache ZooKeeper is one of the earliest widely adopted coordination services. It provides a replicated hierarchical data store where clients create, read, update, and watch nodes called **znodes**.

ZooKeeper stores data in a tree-like structure:

```text id="vyx3fa"
/services
/services/web
/services/web/node-1
/config
/config/db_url
/locks
/locks/mylock
```

Key ZooKeeper concepts:

* **ZNodes**: Tree nodes that can hold data and children.
* **Ephemeral ZNodes**: Automatically deleted when the client session ends.
* **Sequential ZNodes**: Nodes created with increasing sequence numbers.
* **Watches**: Notifications triggered when znodes change.
* **Quorum Writes**: Writes require agreement from a majority of ZooKeeper nodes.

Example ZooKeeper commands:

```bash id="opv2jo"
# Connect to a ZooKeeper server
zkCli.sh -server 127.0.0.1:2181

# Create a znode
create /mylock "some-data"

# List children
ls /

# Set data
set /mylock "updated"
```

Example ZooKeeper output:

```text id="0c73s6"
Created /mylock
[mylock, zookeeper]
```

ZooKeeper is commonly used for leader election, distributed locks, configuration, membership tracking, and coordination in older Hadoop ecosystem tools.

#### etcd

**etcd** is a strongly consistent key-value store that uses the Raft consensus algorithm. It is widely known as the backing store for Kubernetes cluster state.

etcd stores data in a flat key-value namespace, often using slash-separated prefixes.

Example keys:

```text id="5gvayu"
/myapp/config/db_url
/myapp/leader
/services/api/node-1
```

Some etcd concepts:

* **Key-Value Store**: Stores keys and values.
* **Raft Consensus**: Replicates writes through a leader and quorum.
* **Watches**: Clients can watch keys or prefixes.
* **Leases**: Keys can expire automatically when a lease expires.
* **Transactions**: Supports atomic compare-and-swap operations.

Example etcd commands:

```bash id="er7w0n"
# Set a key
etcdctl put /myapp/config "config_data"

# Retrieve a key
etcdctl get /myapp/config

# Watch for changes
etcdctl watch /myapp/
```

Example output:

```text id="g7n5ch"
/myapp/config
config_data
```

etcd is a good fit for strongly consistent metadata, Kubernetes state, leader election, service coordination, and cluster configuration.

#### HashiCorp Consul

HashiCorp Consul combines service discovery, health checks, key-value storage, DNS-based service lookup, and access control.

Consul uses an agent model. Each node can run a Consul agent that registers local services, performs health checks, and communicates with the Consul server cluster.

Consul concepts:

* **Agents**: Run on nodes and participate in service registration and health checking.
* **Service Catalog**: Stores available services and instances.
* **DNS Interface**: Allows service discovery using DNS names.
* **Key-Value Store**: Stores configuration or coordination data.
* **ACL System**: Controls who can read or write data.

Example Consul commands:

```bash id="jmbmxf"
# Set a KV pair
consul kv put myapp/config "{\"max_retries\": 5}"

# Retrieve a KV pair
consul kv get myapp/config

# Register a service
consul services register -name="web" -port=8080
```

Example service discovery result:

```json id="y8649g"
{
  "service": "web",
  "port": 8080,
  "health": "passing"
}
```

Consul is especially useful when service discovery and health checking are first-class requirements.

### Typical Coordination Patterns

Coordination systems provide low-level primitives, but applications usually use them through common patterns.

#### Leader Election Pattern

In leader election, each node attempts to claim a leadership key, lock, or ephemeral node. The node that succeeds becomes leader. Other nodes watch the leader key and attempt to take over if it disappears or expires.

```text id="a5tp6t"
+--------------+   +---------+  +---------+
| ZK/etcd/etc  |---| Node A  |--| Node B  |
| KV store     |   +---------+  +---------+
       ^
       | ephemeral node or CAS check
       v
   Leader = Node A
```

Example leader key:

```json id="4ir8sq"
{
  "key": "/scheduler/leader",
  "value": "node-a",
  "lease": "10s"
}
```

Example election behavior:

```json id="1gxyuy"
{
  "node-a": "acquired leadership",
  "node-b": "watching leader key",
  "node-c": "watching leader key"
}
```

If `node-a` fails to renew its lease, the key expires and another node can become leader.

#### Locking / Mutex Pattern

A distributed mutex allows only one process to enter a critical section.

Example critical section:

```text id="ygdgc2"
Only one node may run database migration version 42.
```

Example lock flow:

```json id="yf8pe8"
{
  "lock": "/locks/db-migration-42",
  "owner": "node-b",
  "status": "acquired"
}
```

Example failed acquisition:

```json id="sdlhy1"
{
  "lock": "/locks/db-migration-42",
  "requester": "node-c",
  "status": "waiting",
  "reason": "lock already held by node-b"
}
```

When the owner finishes, it releases the lock. If it crashes, the lease or ephemeral node should eventually expire.

#### Distributed Configuration Pattern

A coordination service can store configuration under known paths. Applications read these values at startup and watch them for updates.

Example config key:

```text id="0j5ffd"
/app/config/db_url
```

Example value:

```text id="znp21u"
jdbc:mysql://dbhost:3306/mydb
```

Example update event:

```json id="ym0e53"
{
  "key": "/app/config/db_url",
  "event": "updated",
  "newValue": "jdbc:mysql://new-dbhost:3306/mydb"
}
```

Applications can react by reloading connections, updating in-memory settings, or rolling changes gradually.

#### Membership and Heartbeats Pattern

Nodes can register themselves by creating ephemeral keys or session-based entries. As long as the node remains alive and connected, the entry exists. If the node crashes or loses its session, the entry disappears.

Example membership keys:

```text id="guk7n6"
/services/worker/node-a
/services/worker/node-b
/services/worker/node-c
```

Example membership state:

```json id="1byj1m"
{
  "service": "worker",
  "activeNodes": ["node-a", "node-b", "node-c"]
}
```

Example failure detection:

```json id="j1bo3w"
{
  "event": "node_removed",
  "node": "node-b",
  "reason": "session expired"
}
```

Other components can watch membership changes and rebalance work when nodes join or leave.

### Architecture and Deployment

Coordination services are usually deployed as small clusters. They rely on consensus, so deployment design affects availability, performance, and correctness.

#### Cluster Setup

Coordination clusters typically run with 3 or 5 nodes. Each node stores a copy of the coordination state. A leader handles writes, and followers replicate the log.

```text id="fz3xr6"
+----------+  +----------+  +----------+
| Node1    |  | Node2    |  | Node3    |
| Leader   |  | Follower |  | Follower |
+----------+  +----------+  +----------+
         Replication / Consensus
```

An odd number of nodes helps avoid ties during elections. More nodes are not always better. Consensus writes require majority agreement, so larger clusters can increase write latency.

Example quorum math:

```json id="g92xva"
{
  "clusterSize": 3,
  "quorumRequired": 2,
  "toleratedFailures": 1
}
```

For a 5-node cluster:

```json id="m88hfw"
{
  "clusterSize": 5,
  "quorumRequired": 3,
  "toleratedFailures": 2
}
```

#### Failover and Quorum

A coordination service needs a majority of nodes to make progress on writes. If the current leader fails, the remaining nodes elect a new leader as long as a quorum is available.

Example healthy failover:

```json id="mxuit5"
{
  "oldLeader": "node1",
  "newLeader": "node2",
  "quorumAvailable": true,
  "writesAllowed": true
}
```

Example partition without quorum:

```json id="vbpgpk"
{
  "partition": ["node1"],
  "clusterSize": 3,
  "reachableNodes": 1,
  "quorumAvailable": false,
  "writesAllowed": false
}
```

This behavior protects consistency. A minority partition should not accept writes because that could create conflicting cluster state.

#### High Availability Considerations

Coordination clusters should be treated as critical infrastructure. Many applications may depend on them.

Best deployment practices include:

* Run coordination nodes on stable infrastructure.
* Avoid colocating them with noisy application workloads.
* Monitor leader changes, disk latency, request latency, and quorum health.
* Use reliable networking between coordination nodes.
* Back up important state where appropriate.
* Secure client and peer communication with TLS.
* Restrict access using authentication and authorization.

Example monitoring snapshot:

```json id="w60b7d"
{
  "cluster": "etcd",
  "leaderChangesLastHour": 0,
  "quorum": true,
  "p99RequestLatencyMs": 12,
  "healthyMembers": 3
}
```

Frequent leader changes or high disk latency can indicate instability.

### Implementation Tips and Commands

Applications should usually rely on official clients or established libraries. Distributed locks and leader election are easy to get subtly wrong.

#### ZooKeeper Basic Lock Example

ZooKeeper users often use Apache Curator, which provides recipes for locks and leader election.

Example Java pseudo-code:

```java id="2y7w4n"
import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.framework.recipes.locks.InterProcessMutex;

CuratorFramework client = ...; // connect to ZooKeeper

InterProcessMutex lock = new InterProcessMutex(client, "/mylock");

try {
    lock.acquire();
    // Perform critical operation
} finally {
    lock.release();
}
```

Example behavior:

```json id="7ox7kl"
{
  "lock": "/mylock",
  "owner": "current-process",
  "criticalOperation": "running"
}
```

Using a library is safer than manually creating and deleting znodes for complex locking behavior.

#### etcd Lock and Lease Example

etcd supports leases and locking through `etcdctl`.

Example command:

```bash id="1i7wsr"
# Create a lease for 10 seconds
LEASE_ID=$(etcdctl lease grant 10 | grep ID | awk '{print $3}')

# Lock key with that lease
etcdctl lock --lease=$LEASE_ID mylock "Performing critical section"
```

Example output:

```text id="st6g83"
mylock/694d...
Performing critical section
```

The lease prevents the lock from living forever if the process crashes. When the lease expires, the lock can be released automatically.

#### Consul Leader Election Example

Consul can use sessions to implement leader election or locks.

Example commands:

```bash id="0dqeqi"
# Create a session with a TTL
SESSION_ID=$(consul session create -name "my-leader-session" -ttl=10s | grep ID | awk '{print $2}')

# Attempt to acquire leadership
consul kv put myapp/leader "node1" -acquire=$SESSION_ID
```

Example output:

```text id="mx93ml"
Success! Data written to: myapp/leader
```

Example state:

```json id="l1rzd0"
{
  "leaderKey": "myapp/leader",
  "leader": "node1",
  "sessionTtl": "10s"
}
```

The leader must renew the session. If it stops renewing, the session expires and another node can acquire the key.

### Best Practices

Coordination services are powerful, but they should be used carefully. They are not general-purpose databases or high-volume event buses.

#### 1. Keep Clusters Small

Use 3 or 5 nodes for most coordination clusters. Larger clusters can increase consensus latency because writes require majority replication.

Example:

```json id="h0y1sz"
{
  "recommendedClusterSizes": [3, 5],
  "reason": "balance fault tolerance and consensus latency"
}
```

#### 2. Use Dedicated Resources

Coordination nodes should run on stable machines with reliable disks and networks. Avoid running heavy application workloads on the same nodes.

Example risk:

```json id="g8ig0n"
{
  "problem": "application workload caused disk latency spike",
  "effect": "coordination cluster leader changed repeatedly"
}
```

#### 3. Secure the Cluster

Enable TLS, authentication, and authorization. Coordination services often contain sensitive cluster state, service addresses, configuration, and locks.

Example secure settings:

```json id="2w3870"
{
  "clientTls": true,
  "peerTls": true,
  "authentication": "enabled",
  "authorization": "enabled"
}
```

Network access should be limited so only trusted clients and cluster members can connect.

#### 4. Be Careful with Watches

Watches are useful, but too many watches or very frequently changing keys can overload the coordination service.

Example watch risk:

```json id="vz8n6o"
{
  "watchedKey": "/metrics/high_frequency_counter",
  "updatesPerSecond": 5000,
  "risk": "too many watch notifications"
}
```

Coordination stores should not be used for high-frequency metrics or event streams. Use monitoring systems or message brokers for that.

#### 5. Design with Quorum Awareness

Understand how many failures your cluster can tolerate. A 3-node cluster can tolerate 1 node failure. A 5-node cluster can tolerate 2 node failures.

Example:

```json id="lplscz"
{
  "clusterSize": 3,
  "canTolerateFailures": 1,
  "losesQuorumAtFailures": 2
}
```

Deploy nodes across failure domains carefully. If all nodes are in the same rack, zone, or host group, one infrastructure failure can take down the cluster.

#### 6. Use Official Client Libraries

Distributed coordination is subtle. Official libraries and mature recipes handle retries, sessions, leases, fencing tokens, reconnection, and edge cases better than ad hoc implementations.

Example:

```json id="ihouo9"
{
  "manualLockImplementation": "risky",
  "officialClientRecipe": "preferred"
}
```

For locks that control external resources, consider using fencing tokens. A fencing token is a monotonically increasing value that helps downstream systems reject stale lock holders.

Example fencing token:

```json id="hfbsbu"
{
  "lock": "payment-batch",
  "owner": "node-b",
  "fencingToken": 1042
}
```

If an old lock holder resumes after a pause, downstream systems can reject operations with an older token.
