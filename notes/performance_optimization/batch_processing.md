## Batch Processing

Batch processing is a technique for performing operations on large, fixed-size input sets of files and returning an output. It's often done in distributed file systems like Hadoop and uses batch processing tools like MapReduce for data transformation.

### MapReduce
* Processes files and returns output files for subsequent MapReduce calls
* Breaks files into records and extracts key-value pairs using mapper function
* Sorts key-value pairs by key
* Calls reducer function to process sorted key-value pairs
* Requires custom code for mapper and reducers
* Parallelizes computation across machines automatically
* Handles faults by restarting failed map or reduce tasks

### Joins in MapReduce
- **Sort-merge joins (reduce side join):** Use mappers for relevant database tables, send results to same reducer nodes, sort in between to group relevant info, handle hot keys by random partition assignment and replication
- **Broadcast hash joins (map side join):** For small datasets that fit in memory, use in-memory hash table on each mapper for joining
- **Partitioned hash joins (map side join):** Similar to broadcast hash join, but for partitioned datasets, use broadcast hash join for each partition; if partitioned and sorted the same way, only one dataset needs to be loaded in memory

### When to Use Batch Processing
* Building search indexes
* Large precomputed computations (e.g., machine learning)
* ETL processes (converting data from transactional databases for analytics)
* Building databases into batch jobs to avoid slow network calls

### Alternatives to MapReduce
- Dataflow engines like Spark: Parallelize computations with operators, optimize for data dependencies, less fault-tolerant than MapReduce
- Pregel processing model for graph data: Efficient for recommendation algorithms, uses message-passing along graph edges, nodes store state in memory, occasional disk writes for fault tolerance

