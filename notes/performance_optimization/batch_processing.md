
## Batch Processing

Batch processing is a technique used for performing operations on a potentially large, fixed size input set of files and returning an output. It is usually done in a distributed file store like Hadoop and can be transformed using batch processing tools like MapReduce to get a different output.

MapReduce is a popular batch processing tool, but there are other methods for optimization and speed-up for different scenarios of computation.

### MapReduce
* Passes in files and returns files to be piped into subsequent MapReduce calls
* Breaks each file into records, calls the mapper function to extract a key and value from each input record
* Sorts all of the key-value pairs by key
* Calls the reducer function to iterate over the sorted key-value pairs
* Only requires custom code to be written for the mapper and reducers
* Computation is parallelized across many machines automatically
* Designed for frequent faults, if a single map or reduce task fails only it gets restarted

### Joins in MapReduce
It is used to resolve associations within a dataset. Calling the database for each join can be too expensive since it requires a multitude of slow network calls.

There are three types of joins in MapReduce:
* **Sort-merge joins (reduce side join):** Have a mapper for both relevant database tables, and then send the result of both mappers to the same reducer nodes, making sure to sort them in between so that all of the relevant information is next to one another. If there are certain keys which are very popular (hot keys), randomly assign the partition for each instance of a given hotkey and replicate the necessary database information to each partition.
* **Broadcast hash joins (map side join):** If one of the datasets being joined on is so small that it can fit on memory in each of the mappers, use an in memory hash table on each mapper to do the joining.
* **Partitioned hash joins (map side join):** Same as broadcast hash join but for when each side of the join is partitioned the same way, do a broadcast hash join for each partition. If they are partitioned and sorted in the same way, one dataset does not even be loaded into memory, because a mapper can do the same merging operation that would normally be done by a reducer.

### When to Use Batch Processing
* Building search indexes
* Performing large computations that need to be precomputed (e.g. using machine learning)
* Performing ETL processes (taking data from transactional database and converting it for analytics)
* Building databases into batch jobs as opposed to slowing things down with network calls

### Alternatives to MapReduce
MapReduce can be inefficient when chaining together many MapReduce jobs because it needs to wait for one to completely finish before starting the next, and there is a lot of time wasted in writing out the intermediate state to disk. This is because certain hotkeys or stragglers can take much longer and delay the whole process.

A better alternative is dataflow engines such as Spark, which parallelizes computations to run as quickly as possible over multiple user-defined functions called operators. Data dependencies are explicitly declared so that the engine can optimize for them, and this reduces the amount of unnecessary mappers. It is slightly less fault tolerant than MapReduce because data is not materialized to intermediate state, so if it is lost, it has to be recomputed from the previous data needed to make the calculations. This means that the functions must be deterministic.

Batch processing is also frequently used on graph data in order to make things like recommendation algorithms. MapReduce is not efficient for this because the graph data infrequently changes, however MapReduce would create an entirely new output dataset. 

Instead, it is better to use the Pregel processing model, where one vertex can send a message to another vertex along an edge of a path. In each iteration of the batch processing, the vertex receives all the messages sent to it from the prior step, and then sends out new messages. This goes on until an end condition is met. The nodes remember their state in memory so the entire graph does not need to be rewritten. By occasionally writing vertex state to disk, a deterministic algorithm becomes fault tolerant in the event of a crash.
