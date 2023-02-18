## Linearizability

Linearizability is a technique used to make it appear as if there is only a single copy of the data. When a new value has been written or read, all subsequent reads from any replica will reflect the value that was written until it is overwritten again. Linearizability allows for consistent, up-to-date reads, but has a cost in terms of availability and speed.

## Ordering

In order to achieve linearizability, we need to determine an order in which every operation on the data occurred. This is done to keep track of causality and see which events depended on others. Having an ordering that only keeps track of causality does not provide a total order, which is needed for linearizability. 

We can use Lamport timestamps to generate sequence numbers across multiple machines consistent with causality:
* Each node has a unique identifier, and keeps a counter of the number of operations it has processed
* The timestamp is a tuple of the counter and the node ID, use an arbitrary ordering between the nodes and the counter to create a total order
* Every node and client keeps track of the maximum counter value it has seen so far, and includes the maximum on every request
* When a node receives a request or response with a maximum counter greater than its own counter value, it increases its own counter to that maximum

Lamport timestamps cannot show which operations were concurrent with one another, though they do provide a total ordering. They are also not sufficient to solve problems such as dealing with uniqueness constraints across different replicas. To solve these problems, we can use a protocol called total order broadcast which is used to exchange messages between nodes. This protocol ensures that no messages are lost, and that messages are delivered to every node in the same order each time. 

## Distributed Transactions and Consensus

We can use two phase commit to solve the atomic commit problem. The coordinator node sends writes to each node and then sends each node a prepare request. If all the nodes can commit, the coordinator tells them to do so, otherwise it tells them all to abort. The coordinator has an internal log with its decisions for each transaction in the event that it crashes.

Good consensus algorithms reach agreement by using a majority (quorum) of nodes, in order to improve availability. After new leaders are elected in a subsequent epoch (monotonically increasing in order to prevent split brain), consensus algorithms define a recovery process which nodes can use to get into a consistent state. Coordination services such as ZooKeeper are used internally in many other popular libraries, and are a replicated in memory key value store that allows total order broadcast to your database replicas.
