# Backend-Engineers-Guide

Search indexes
File storage
TCP/UDP/Networking
CRDTs
Operational Transform
Gossip Protocol
RAID/more operating systems concepts
Microservice architecture
Coordination services
DNS
Security
More about back of the hand calculations for systems

Background

Systems are designed with the intent of being:
Reliable
Working in the face of faults, both hardware and software
Scalable
Working as the system grows in both users, traffic, and data
Horizontal scaling is adding more of an existing resource
Vertical scaling is adding more power, such as different hardware
Maintainable
Easy to add different parts to the system and coordinate with other developers

Describing Load and Load Estimations

Oftentimes in an interview we will need to estimate the performance of a system, however there are many ways to measure this.  We can look at average performance, but this does not describe potential variation in calls to our service.

Three important metrics:
Throughput
The number of records processed per second
Good for batch jobs
Response time
The time between the client sending a request and receiving a response
More important when talking about online systems
Latency
The duration that a request is waiting to be handled

Another important concept is tail latency, which describes the latency at a certain percentile of requests.  For example, the latency metric of 1 second for p95 says that 95% of requests have a lower time than 1 second, the other 5% do not.

Types of Databases

In the majority of the systems we will be designing, there is a need to hold some sort of persistent data.  It would make no sense to hold application data in server memory, as not only would it be lost if the server crashed, but having many servers means that they would be out of sync if only one server stored certain information.  The solution to this is to store any persistent data in one or more databases.  I will now go into the types of databases, and the pros and cons of using each type.

Types of databases:
Relational databases (also known as SQL databases)
Consists of tables holding many rows of structured data
Rows of one table can have relation to rows of another table if both rows share a common key
Has a built in query optimizer that user the quickest implementation for a SQL statement (declarative language)
Non Relational databases (also known as NoSQL databases)
Instead of rows, a table holds a collection of keys mapped to values, which do not need to have any particular structure
Graph databases (also technically NoSQL)
Has vertices and edges, queries involve traversing the graph
Good for storing both homogenous and heterogenous data (with multiple types of edges)

The benefits of NoSQL:
NoSQL has better locality than SQL
What this means is that for a large document, for example some sort of social media profile, it can all be stored in area
Therefore pulling this document is much faster than having to fetch multiple related rows in a SQL table
However, in the event that we only need a certain part of this information, we will be sending more data over the network resulting in a slower call
Since sequential disk reads are faster, because the disk does not have to move around its head, having lots of data stored in the same place results in a faster query
NoSQL is easier to shard
To give a quick summary of sharding (will go into more detail later), it is taking a database that is too big and splitting it up over multiple machines
This is complicated with a SQL database, because when using a join call, you may potentially have to access many partitions resulting in lots of network calls
On the other hand, the increased locality of NoSQL means that the entire document will likely be on one machine and can be quickly accessed with a single network call
NoSQL data is not formatted
Makes it a bit more maintainable when adding new features to an object, or just having related data with slightly different structures
Not needing to format data in rows allows database formatting to more accurately reflect the data structure in memory that stores the object

The benefits of SQL:
SQL allows joins, whereas NoSQL does not
Generally speaking SQL allows easily fetching multiple related rows of various tables using the join command, whereas there is no support for this in NoSQL
You can do it using application code, however it will require many network calls and result in a slow query
As a result, it seems that SQL allows the data to be a bit more modular, where you can only request certain parts of a potentially large document, at the tradeoff that trying to fetch the entire document may take a long time
SQL has transactions
Transactions are something that will be covered later, but the gist is that they are an abstraction on top of database writes to provide some guarantees about them and simplify the edge cases a programmer must consider
However, in a distributed setting it rarely makes sense to use transactions and so this benefit is diminished

Indexes

Imagine a basic database where you want to fetch a record when making a read.  If all of the rows are just stored on a hard drive, every single time a read call is made, you would need to search for the row on the disk, resulting in a very slow O(n) time complexity.  Instead, this process can be sped up by creating an index, which allows a database to quickly search for rows based on certain values of the tuple that defines a record.

While indexes sound great, they also have tradeoffs:
Having an index speeds up reads, if it is frequently used (the application often queries for values based on the column the index corresponds to)
Having an index slows down writes, because on every write additional work must be done behind the scene to maintain the proper data formatting for the index

Note that all writes to databases (assuming no indexes) are done by just appending to a log, as this is the quickest way to write to disk (sequential writes).  It also makes concurrency much easier to deal with as there are no conflicts on crash of one value being partially overwritten.

In all of the following examples, the write logs can be compacted:
One line of a log has a key and its corresponding value (or a tombstone saying a key has been deleted)
We can find all of the old values of the key, and delete them from the log in order to save space, so that only the newest value of each key is kept
If the log is broken into multiple files, known as segments, just merge them afterwards
This can be done using a background process, copying the files to a new log and then switching over from the old log to the new one

There are multiple implementations to creating an index under the hood:
Hash indexes
Put the key in an in memory hashmap, where the value is the memory address of the proper row
On writes update the hash map
The downside of this is that all of the keys must fit in memory, since this is where hashmaps are kept, good for when not many distinct keys
Inefficient range queries since not all keys in a range can be scanned at once
Occasionally save the in memory hash table to disk to assist with crash recovery
SSTables and LSM-Trees
Keep each log structured storage segment sorted by key, each key only appears once in each merged segment file (ensured by compaction)
Merging segments is done by sequentially going through each and starting with the lowest key (resembles merge sort algorithm), very efficient and done in linear time, keep the most recent value for a given key
No longer need to keep all of the keys in memory, just a few (with their corresponding memory address), and as a result of the sorting, can run a binary search to quickly find the key we want
In order to get the keys sorted originally, writes should first go to an in memory sorted data structure such as a red-black or AVL tree (memtable)
When the memtable gets too big, write it to disk as an SSTable (sorted log) segment, then create a new memtable
For reads, first check the memtable, and then traverse through the disk segments from newest to oldest
From time to time merge and compact disk segments
To increase fault tolerance, keep a separate log on disk which logs memtable writes so that memtable can be restored in the event of a crash
For keys that do not exist, this may take a very long time to check since we need to go through all the segments, so can be optimized with bloom filters
Has very high write throughput since all disk writes are sequential, can perform efficient range queries
B-Trees
Most common implementation of databases indexes, also keeps pairs sorted by key
Break database into fixed size blocks or pages, read or write one page at a time, aligns nicely with disks which are also broken into blocks, each page has an address that is like a pointer
Turn the disk into a tree, where each node of the tree has pointers with sparse key names in between them, so that finding a given key is just traversing the pointers of the tree in a binary search until reaching a leaf page which stores the keys next to their values
To update values just find them in the B-tree and change them
To add values find where the key should be and add it to that page, but if there is no space on the page, split the page in two pieces and update the parent page to reference the two leaf pages properly
Keeps B-tree balanced, with a depth of O(log n) for n keys, most databases can fit into a tree that is only 3 or 4 levels deep
Include a write ahead log of things that the B-tree will do in order to be able to recreate the tree on a crash

LSM-trees versus B-trees:
LSM trees thought to be faster for writes (just write to an in memory tree), B-trees thought to be faster for reads (traverse the tree as opposed to checking all segments linearly)
The compaction process in LSM-trees can take up computer resources

You can construct secondary indexes (on non unique fields) from these data structures very easily by just making them point to a list or appending the primary key of the row onto the secondary index key to make them unique. 

In an index, it is often preferable to store the actual rows in an append-only heap file, with the key value mapping pointing to the offset of said row.  However, this incurs a read penalty when trying to get the value from the heap file, and also means that if a value is updated such that it can no longer fit in its old position of the heap file, it must be moved, and all the indexes holding the corresponding key must be updated.  In some situations you can store the actual values in the index (clustered index), but on writes every cluster index must now be updated.  One middle ground to this is the covering index which stores only a few columns of the row in the index.

Multicolumn indexes can also be created by basically just concatenating fields, have to be careful the way this is done because it is done using an outer sort order with an inner one, so not all queries will use the index.  Some databases have true multidimensional indexes.

Transaction Analytics and Data Warehousing

Many companies that want to do retroactive processing on some of their data or calculations will have a second database, known as a data warehouse, that stores all of their data.  This will be optimized for reads across the whole dataset, using the values of only a few columns at once.  This solution is preferable to querying the main database as that would potentially put too much load on it.

Data is typically extracted from the transaction databases, transformed to the proper format for analytics, and then loaded into the data warehouse.  The index patterns discussed above do not work as well for analytics, so there is a need to create new ways of storing the data.

The data in an analytics table is typically done via the stars and snowflakes schema:
There is a centralized fact table for important events that we may want to analyze (such as each sale in a grocery store)
The fact table has multiple foreign keys to rows of many other tables, known as dimension tables (in the grocery example possibly a product table or a customer table)
The snowflakes schema builds on the aforementioned star schema, where each dimension table has sub dimension tables

In order to optimize for analytical speed, data warehouses typically use column oriented storage:
Traditional approach
Most non analytical (transactional) databases use row oriented storage, because we typically want to access all of the values in a row
This means that there is locality in the storage of a row
However, for analytics queries most only use a few out of the hundreds of columns in a given row
Column oriented storage
Store every value from each column together instead, keep the order of the values in the column the same as what the rows would be in the table
Increased locality of these values allows reading them much faster
Compression
Storing all of the column values can be easily compressed in order to reduce the amount of space that the data takes up
If the number of distinct values in a column is small compared to the number of rows, a bitmap encoding can easily reduce the amount of space needed (turn each possible value into a 0 for the indices of the column where the index is not equal to the value and a 1 if it is equal to the value)
Can further compress the bitmap encoding to a run length encoding by saying how many 0s and 1s are repeated and combining these numbers
When trying to find rows that have values of either A or B for a specific column, load their bitwise encodings and bitwise OR them to quickly get a result
Using column oriented storage allows better parallelization, and compressing it allows more of the data to fit in CPU cache

Sometimes it makes sense to sort all of the columns in the same order to help speed up queries, in addition to help compress columns even further (if all equal values are next to one another this is easiest to compress).  Can even have replicas of the data warehouse sorted in multiple different ways to make certain queries faster.

Writing to column oriented storage is hard if you want to write in the middle of a sorted list, but LSM-trees allow doing this efficiently and then rewriting the column segments to propagate the changes.

A further way that analytics can be sped up is with materialized views:
Materialized views
An optimization by the database to precompute certain common queries in order to cache the result
This way it does not have to be recalculated all the time
Trade offs
Caches the result of common computations so that they do not constantly have to be rerun
The downside of this is that on writes materialized views must be updated, so writes take longer
Less flexibility than querying raw data
Data cube
Special type of materialized view that groups aggregates by two different dimensions (for example date and product number to find the total sales for each combination)

Encoding

Encoding allows us to send data from machine to machine, as objects in memory must be translated to encodings.  Generally, we should not use language specific encoders as they are slow and lock you into a given language.  JSON and XML, the most common encodings, are useful in the sense that they are so ubiquitous.  But in some cases, as in dealing with very large amounts of proprietary data, it can make sense to use a custom binary encoding to reduce the amount of space used by an encoding and greatly speed up the transfer of data.  Some of these binary encoders are greatly able to reduce the amount of space used by requiring a schema predefined for the data - but in defining a schema, it is important that our applications are able to stay both forwards and backwards compatible.  To maintain backwards compatibility, if you add a new field to a schema, it cannot be made required (or it must have a default value).  Schemas can be useful because having a database of them can help to keep track of forward and backward compatibility, and also allow for compile time type checking in statically typed languages.

Replication

Replication is the process of storing multiple copies of the same data on multiple different computers.  It serves three main purposes.  Firstly, the redundancy of the data means that a service can still serve reads and writes if one of the database nodes crashes.  Secondly, replication can actually speed up the process of reading or writing if the operation is performed by a database node that is geographically closer to the client.  Finally, replicating data to many databases allows the reduction of load on each database.  However, there are many different ways of implementing replication, each with their own benefits and drawbacks, and we will read about them below.

Single leader replication:
One of the nodes is designated to be the leader
All writes are sent to this leader, and they are written to the leader’s local storage
All of the other replicas are known as followers
Data is sent to the followers from the leader via a replication log
Each follower takes the log and updates the local data in the same order that the log specifies
Clients can perform reads from either the leader or the follower
Can be performed either synchronously or asynchronously
Synchronous replication is when the client only receives a message that a given write was successful once the changes have been propagated to all of the replicas (strong consistency)
Asynchronous replication is when the client receives a message saying that their write was successful the moment it reaches the leader database, all changes to the replicas are propagated in the background (eventual consistency)
While synchronous replication ensures that all followers have up to date data, it is impractical because a crash on one of the followers or just a follower operating slowly slows breaks the whole system
Typically synchronous replication means that only one follower is synchronous while the rest are asynchronous, if the synchronous follower fails another one of the followers is made synchronous
In a fully asynchronous system, writes to the leader that have yet to be propagated are lost on a crash
Setting up new followers is a relatively easy process, and does not affect write throughput of the system
Take a consistent snapshot of the leader database, and copy this to the follower node
Then connect to the leader, and use the replication log to catch up from the position of the snapshot in the log
Once caught up, start acting as a normal follower
It is very easy to recover from a follower crashing
Just check the log of changes that it needs to make to see what point the follower was upto when it crashed, and from then on connect to the leader and connect all of the changes since then
After catching up, continue to act as a normal follower
If the leader fails in this configuration, the system must perform a failover
First the system must determine that the leader has actually failed, this is impossible to do with complete certainty as there are a variety of things that can go wrong (crashes, power outage, network issues), so most systems have databases frequently communicate with one another and use a timeout to determine if a node is dead
Use some sort of consensus mechanism (will talk about this in more detail later) to determine a follower node that will become the new leader, typically good choice is the most up to date follower
Configure clients to send their write requests to the new leader, make sure if the old leader comes back it now realizes it is a follower
Failover can be a dangerous situation because you may need to discard some writes from the old leader, can lead to inconsistencies if other systems (not database) had already propagated those changes internally (such as a cache)
In some scenarios two nodes may end up thinking they are the leader, could lead to corrupted data (split brain, can be dealt with)
If timeout for determining failover is too small, may perform unnecessary failovers and introduce extra load on a system

Replication log implementation:
The most simple way is to just copy over the SQL statements used by the leader
However, this is a problem because some SQL commands are nondeterministic
While these values could be replaced with deterministic values by the original database, other solutions that are better have been made
Another option is to use a write ahead log in the same way that databases do for indexing
Append only sequence of bytes containing all writes to the database
This log already exists on disk, so just send it over network to followers
Disadvantage is write ahead log has which bytes were changed, so a change in the storage engine over a replica may render everything moot if things are stored in different locations, makes rolling upgrades impossible and requires downtime
A logical log describes all the changes made to a given row (usually by primary key)
Decoupling the storage index and the log allows for rolling upgrades and backwards compatibility

Problems with replication lag and eventual consistency:
Reading your own writes
After writing data and refreshing, you may still see the old data since the changes you have made have not yet been propagated on the replica you are reading from
Requires read-after-write consistency, which says that after uploading a page you will see the writes that you have just made
Can either always query the leader for areas of the application that are editable by the user, or keep track of the last write on the client, and for some amount of period of time afterwards only read from the leader (or a replica that is up to date as of that timestamp)
Monotonic reads
Reads occurring on several different replicas actually can make it seem as if you are moving back in time
Guarantee monotonic reads, one way of doing so is to make sure that each user always reads from the same replica, can be done based off of a hash of the user ID (this can break down if said replica fails)
Consistent prefix reads
When two things in the database have a causal relationship, but the one that precedes the other has a greater replication lag so to another user it seems like the latter write comes before the preceding one (happens when they are on different partitions, otherwise log would maintain order)
Could perhaps make sure causally related writes are on the same partition, but not always possible, so may have to explicitly keep track of causal dependencies

Multi leader replication:
Adds significant complexity to single leader replication, each of the leaders is also a follower for all of the other leaders
This introduces the need to resolve conflicting writes between different leaders
Works well in cases where there are multiple data centers in geographically different regions
Reduces latency of original write, and each datacenter can continue operating independently of the others, temporary network outages between datacenters do not stop writes from being processed
Need to be able to handle write conflicts between multiple leaders, for example when an entry is modified by two different clients to be two different values at the same time
One way to avoid conflicts is just by forcing all writes to a given field to go to the same leader
All the replicas must converge to a consistent state (have the same data)
Can determine which write wins based on a timestamp or giving replicas a priority, but this implies a loss of some data
Can also perhaps keep all of the conflicting data in some data structure and have a user resolve it down the line (on read), or use some code to help the database resolve it (on write)
A multileader replication setup can use a variety of different topologies, or configurations with which writes are propagated from one leader to another
This includes a circular topology (passed in a cyclic order), star topology (one central node), and all to all topology (all nodes communicate with one another)
In circle and star topologies, writes in the replication log are marked with which nodes they are passed through to avoid duplicate operations
In circle and star topologies, the failure of one node means the failure of the entire replication path, all to all avoids a single point of failure
However, in all to all replication, some messages may arrive faster than ones written before them leading to inconsistencies, which is a problem of causality (can be ordered with version vectors)

Leaderless replication:
Any replica can accept writes from any of the clients
No such thing as failover, simply set a threshold of the number of nodes that need to accept the write for the write to be successful, same with reads
If an unavailable node comes back online, a client may read from many nodes simultaneously, realize the previously offline node has an outdated value and update it accordingly (use version numbers to check which values are out of date), this process is known as read repair
Another way of ensuring up to date data is anti entropy, which is a background process that looks for data differences in replicas and copies the correct data over, however the writes are not copied in any particular order
If we can only write to a fraction of nodes at a time and read from a fraction, we can use a quorum in order to ensure that we always read from at least node with a most up to date copy of the data
This occurs when the number of nodes successfully written to plus the number of nodes read from are greater than the number of total replicas
Typically reads and writes are sent to all replicas in parallel
There are still cases where quorum reads and writes are not perfect
Even if writes do not succeed on the specified number of nodes they will not be rolled back on the nodes where they have been written
In the event that sloppy quorums are used, the writes may end up on different nodes than reads, such that there is no overlap between them
If a node with a new value fails and its data is restored using a node with an old value, the new value will be lost
Works well with multi-datacenter operation
Send writes to all nodes, but have the acknowledgements from the client’s local datacenter be sufficient to fulfill a quorum write in order to reduce the high cross datacenter latency of writes

Sloppy Quorums:
Sometimes a client can reach certain nodes in a cluster, but not the nodes that the data for a given write would typically go to
A sloppy quorum is instead writing and reading from these nodes outside of the cluster (still using the predefined thresholds for the number of reads and write nodes as a normal quorum)
Once the network outage is fixed the data is sent to the proper nodes, known as hinted handoff
There are no guarantees that reading from the proper number of nodes will return the new value, as the reads are probably going to the original nodes, not the ones where the data is written
Sloppy quorums are just useful for assuring durability of data

Detecting Concurrent Writes

A problem that occurs in both multileader and leaderless implementations of replications is being able to detect many concurrent writes.   Concurrent writes occur when two writes to the database from different clients do not know about each other.  While it is most important that the database replicas all converge to a consistent state, there are certain ways of dealing with concurrency that improve durability by not arbitrarily picking one write to keep and throwing out the others.

Detecting Concurrent Writes:
Both multileader and leaderless replication have to be able to detect and rectify possible concurrent writes
Events may arrive in a different order at different nodes, ultimately every node has to be in a consistent state
Concurrent writes happen when neither client knows about the write of the other before making their write
In last write wins, some arbitrary ordering is given to the writes in order to choose which one should be kept and which should not
This is easy to implement, but is bad for durability as writes are thrown away
Additionally, if using timestamps, these are hard to do due to clock skew
The only safe way to do this is only allowing each key to be written once and from then on being immutable
Instead, we can use version numbers in order to track what information a given client has about a key, useful because no writes are lost
On each write of a value to a key, the client passes the server the last version number of the key that it has seen, and the server assigns the write a new version number and returns it back to the client
If a client writes to the database with a given version number, the database can tell which data the client had access to at the time of writing
If the client is making a write independent of some existing value in the database, the database will give that write a new version number and return both versions of the data on subsequent reads
The application can then handle these two values and either merge them automatically or prompt the user to do so
This approach generalizes to many replicas using version vectors, use a version number per replica as well as per key
Each replica keeps track of its own version number plus the numbers of other replicas in order to indicate which values to overwrite and which to keep as siblings

Partitioning

When dealing with large systems, a common issue that may occur is that a single database table actually becomes too big to store on a single machine.  As a result, the table must be partitioned, or split, onto multiple different nodes.  How exactly this splitting is done is an implementation detail, but being able to partition a database greatly increases the scalability of a system by allowing a given database table to get arbitrarily big, and perhaps even store more relevant data in nodes closer to the users accessing it.  This being said, partitioning, also known as sharding, comes with many complications.

Approaches for partitioning the data:
Want to split up keys so that each partition has relatively even load on it (both in data and queries), otherwise result is hot spot partitions
Can partition keys by range chunks, not necessarily even ranges because some ranges will have more data and activity than others
These ranges can be chosen manually or automatically by the database
Keep keys in sorted order within the partition
In certain scenarios, such as partitioning by timestamp ranges, this can easily lead to hotspots if most of the queries want recent data
Can partition by hash of key and split by a range of hashes, good hash functions will uniformly distribute the keys
Loses the ability to do fast range queries, have to check all partitions
Helps reduce hotspots, but if all of the activity is on one key, then hot spots will still occur, can perhaps be mitigated for certain keys by adding a random number to the key every time and thus partitioning all of the operations to it, but makes reads slow because need to check all of the partitions for the key data
Certain databases allow partitioning by a hash of one key (for example a user id), but then allow you to do efficient range queries on other columns of the data (such as a timestamp)

Partitioning and Secondary Indexes

As discussed previously, secondary indexes are an additional way of storing data in a database that can speed up certain queries.  However, in a partitioned database, not all of the data is available in each partition and making queries based on a secondary index can take a long time.  As we will see below, there are multiple ways to approach building secondary indexes in this situation.

Local Indexes:
Each partition keeps track of every possible secondary index for only its local data
Lower overhead on writes since no need to coordinate across multiple partitions
Potentially very high overhead on reads since need to query all partitions in order to combine the data from all of the local indexes

Global Indexes:
Instead of having each node keep track of all of the indexes for only its local data, instead having each partition hold all of the ids corresponding to a given term, and partition the terms among the nodes
For example, a car sales website would hold all the ids of red cars on partition 1, even if an id of one of the red cars was not held in that particular partition
The terms can be partitioned either by the term itself (better for range scans if querying multiple terms), or a hash of the term (better for distributing load)
The downside of the global index is that writes may have to go to multiple partitions (which introduces network latency), where on the other hand reads become much faster because they only go to one partition
Requires a distributed transaction for the index to be completely up to date, which is quite slow

Rebalancing Partitions
Inevitably, as your system scales, you will have to rebalance the data on each partition, as you will likely have to add or remove nodes in the cluster at some point.  You may also need a new machine to take over a failed machine.  Either way, it is important to know how to gradually add and remove data from a given shard.

Rebalancing Process:
Use hash ranges instead of hashes mod the number of nodes in the cluster
This is bad because adding and removing nodes will make almost every key have to be remapped to another node, uses a tremendous amount of network bandwidth to do
Better to use a system that keeps the majority of keys in place and only moves a few
Instead it is better to use a fixed number of partitions
Create many more partitions than there are nodes to start, assign several small partitions to each node
When adding a new node it can steal a few partitions from each of the existing nodes, do the opposite if a node is removed
While the partition transfer is happening continue to use the old node to accept reads and writes for it
Want to choose a high enough number that allows for future scaling, but also not one that is too high as each partition has management overhead (also large partitions take longer to rebalance)
In certain key range partitions, databases will dynamically partition to help balance load
When a partition gets too big, it is split, and if a partition is too small, it is merged
Good because dynamic splitting keeps a small overhead when little data, and stops each partition from becoming too large in size
While some databases let you choose a starting partition configuration (which is prone to human error), others do not, and so you need to start with one partition which could be a bottleneck
Can also keep the number of partitions per node constant, and go from there
Sometimes it is not good to let the database rebalance automatically because it may incorrectly detect a failed node and try to rebalance, putting more load on network and breaking more things
Use a third party service like zookeeper to keep track of which partition is in which database and use this to coordinate with either a routing layer or a client on which database to access

Transactions

Transactions are an abstraction used by databases to reduce all writes to either a successful one that can be committed, or an erroneous one that can be aborted.  While transactions are somewhat hard to implement in distributed systems (we will discuss later), in a single database they can be rather useful.  They hope to provide the safety guarantees outlined by ACID.

The meaning of ACID:
Atomicity
If a client makes several writes, but a fault occurs after only some of the writes are completed, the existing completed writes will be rolled back
Consistency
The application can rely on the properties of the database to ensure that invariants about the data will hold (in the face of faults)
Isolation
Concurrently executing transactions are isolated from one another (serializability), each transaction can pretend it is the only one running on the database
Most databases do not implement this due to performance penalties, instead use weak isolation levels
Durability
Once a transaction is completed, the data will never be forgotten, even in the face of faults

In single object writes, almost all database engines provide guarantees about atomicity and isolation so that the data for an individual key does not become moot or somehow mixed with the previous value - atomicity can be implemented using a log for crash recovery and isolation can be done using a lock on each object.

Weak Isolation Levels

As mentioned previously, having concurrent writes completely act as if they are sequential ican take up lots of resources and make the database slow.  Instead, some databases protect against only some concurrency issues.

Read Committed Isolation:
When reading from the database, you will only see committed data
Do not want to see database in a partially updated state before write is committed, furthermore that data could soon be rolled back
Do not use row level locks to implement because this will not allow any reads while a write is occurring, but instead just store the old committed value before the new value is committed, and return that instead
When writing to the database, you will only overwrite committed data
Delay the later write until the earlier write is either committed or aborted
Still does not prevent two processes reading an old value and then both updating it, having the first update completely thrown out (for example incrementing a counter)
Implement via row level locks, transactions hold a lock for each row they touch until it is committed or aborted

Snapshot Isolation and Repeatable Read:
While read committed isolation prevents many problems, there are plenty of concurrency bugs that can still occur
Read skew is when a client makes multiple consecutive reads, but in the middle of them the database changes so the client views the database in an inconsistent state
This is unacceptable when making a database backup or running analytics queries, database needs to be in consistent state or data will not make sense
Read skew can be solved by snapshot isolation, each transaction reads from a consistent snapshot of the database
Readers never block writers, writers never block readers
Database keeps several different committed versions of an object because in progress reads need different versions of them at points in time
Each transaction is given a monotonically increasing transaction ID, anytime it makes a write the written data is tagged with the ID (as well as a deleted by field in the event that the data is overwritten or deleted, can eventually be garbage collected)
When reading using a given transaction ID, get the value for each row that has the highest transaction ID less than or equal to the reader’s transaction ID

Dealing With Lost Updates:
Lost updates can occur when an application reads one piece of data, modifies it, and then writes it back - if two of these cycles happen concurrently it is possible that the update from one of them will be lost
Certain atomic write operations allow incrementing or using compare and set to ensure that these do not occur, usually the best choice when they can be used
Implemented via locks on an object
Can also lock certain rows explicitly within application code
Some databases can automatically detect lost updates (using snapshot isolation), thus eliminating the needs for locks and just aborting transactions that cause the lost update
This is better because it reduce the risk of making bugs when dealing with locks
Compare and set is an atomic operation that only occurs if the current value of the field to be updated is specified by the application (read it and then pass to compare and set)
These methods do not really work in replicated databases with many leaders, the best way to deal with lost writes is to create conflicting versions of writes (siblings) and deal with them in the application code

Write Skew and Phantoms:
Write skew occurs when concurrent writes to different parts of the database allow some invariant about the data to be broken (such as both doctors on call leaving their shift without realizing the other is at the same time) 
Can be avoided with complete serializability
This is impractical for the performance of the database
Instead should be using locks, lock all of the other rows that could break the invariant when updating one of them (no other doctors in the shift can leave the shift while one of them is in progress of doing so)
However, sometimes it is the case that write skew occurs when two transactions are actually creating a row in the database, not modifying it, and if both of these rows are created it will violate an invariant (phantom)
In this situation, there is no row to actually put a lock on
Therefore, we need to materialize conflicts by using a pre-populated blank row in the database (for example something like an unbooked meeting room with a given time slot) so that there is something to lock in order to avoid write skew

Serializable Isolation

While the above methods allow for a much faster method of providing some guarantees about concurrency bugs in the data, the best and most bug-free way to deal with concurrency is just to provide serializable isolation.  If you can deal with the performance penalty, you should do so.

Actual Serial Execution:
Literally implementing transactions serially on a single thread
RAM is now cheap enough to keep all data in memory
Non analytics transactions are typically pretty short
Throughput limited to a single CPU core, but no locking overhead
Do not allow multiple statements per transaction (HTTP request), too much network overhead and would create massive delays
Instead send the entire transaction to the database ahead of time as a stored procedure
Annoying to write these as they are hard to version control and deploy, less popular languages
If you can partition data so that each transaction only reads and writes from a single partition you can greatly speed up your throughput
Two Phase Locking:
Multiple transactions can concurrently read the same object as long as nobody is writing to it, but writes require exclusive access to the lock
Have a lock on each database object which is either in shared mode or exclusive mode
This results in relatively frequent deadlocks, in which case the database must abort one of the transactions and let the other complete before retrying it
Takes a great performance hit to have so much overhead on locking and any two transactions which even remotely overlap have to wait on one another, one slow transaction can slow everything down
For phantoms, we need predicate locks, which works like the exclusive shared lock above, but can apply to all objects matching a given search condition
Can apply to objects that do not even yet exist
Perform very poorly, too much checking for matching locks
To improve performance on this, use index-range locking, an approximation of predicate locking
Simplify a predicate by making it match a greater set of objects, works better with indexes on the superset
Any transaction on an item in the superset will match one of the locks

Serializable Snapshot Isolation:
Full serializability with a small concurrency penalty, but relatively new so not too widely implemented
Uses optimistic concurrency control, meaning there are no changes until something bad happens at which point transactions must be aborted and retried
Bad if things need to be retried too often, but in the event that they do not optimistic control is often better than pessimistic control (locking all the time)
All reads occur from snapshots, database needs to tell when a premise that a transaction has acted on has since changed
Detecting reads of a stale object (uncommitted write occurred before the read), at read time check if we have ignored any uncommitted writes and before making the corresponding write from our first read, check if any of the ignored writes have since committed and abort the current transaction if so
Detecting writes that affect prior reads (the write occurs after the read), keep track of which transactions have read a given object so that if the object changes, the other transaction will be aborted when it tries to write (similar to acquiring a write lock on the range of effected keys but is not blocking)

Unreliable Clocks

Oftentimes in distributed computing people attempt to use clocks or timestamps as a way of synchronizing events and receiving an order out of them.  However, for a variety of reasons, this is not a feasible tactic.  There is always a question of whether to use the timestamp from when a message was sent, or received, the difference of which is unbounded due to an asynchronous network.  Additionally, the clocks on the majority of computers are ever so slightly out of sync with one another, and get more out of sync as time passes.

For measuring elapsed time, do not use time of day clocks (seconds since epoch):
They ignore leap seconds
They may jump back to a previous point in time if they become too out of sync with a clock server
Instead, better to use monotonic clock, which just measures relative time on a given computer (it is always increasing)
Synchronization with a time server is only as good as a network delay

For ordering events, do not use time of day clocks:
Writes may be silently discarded without an error message because the time on a given machine was earlier than on another
Logical clocks are better for this functionality

If you had synchronized clocks, you could potentially use timestamps as transaction IDs for snapshot isolation in a distributed database (cannot have one monotonically increasing timestamp across many systems).

Cannot rely on certain parts of code running within some amount of time due to process pauses (things like garbage collection that stop all running threads, or other context switches that take an arbitrary length of time).

Majority Truth in Distributed Systems

It is not possible to rely on one single node as a sole source of truth as it is prone to failures and process pauses.  Instead the state of the system as a whole should be voted on by a majority of nodes.

Using fencing tokens:
Sometimes, a node will incorrectly be declared dead and then come back to the system, assuming it still has the permissions that at previously had
Perhaps a lock on a certain object that has since expired
Perhaps being the leader in single leader replication
Every time privileges are granted (such as grabbing a lock), it comes with a monotonically increasing fencing token
If a write with a higher fencing token has already been processed all writes with a lower fencing token are moot

Byzantine Faults:
Sometimes nodes may act maliciously on purpose, perhaps by sending a fake fencing token
A situation where nodes are lying is known as a Byzantine fault
Systems are Byzantine fault tolerant if they can operate correctly if some nodes are not obeying protocol
Generally only have to worry about these when dealing with multiple parties that do not trust one another, we are only worried about the servers of one organization

Linearizability

The goal of linearizability is to make it appear as if there were only one copy of the data.  Once a new value has been written or read, all subsequent reads (regardless of replica) see the value that was written, until it is overwritten again.  Consensus algorithms are certainly linearizable, while the forms of replication discussed previously may not be.

Linearizability has a cost which is mostly seen in the lack of availability (when it comes to network problems) and speed induced by needing to make up to date reads.

Ordering

In order to achieve linearizability and make it seem as if there is just one copy of the data, we need to determine some sort of order which every operation on the data occurred in.  Having an ordering allows us to keep track of causality, and see which events depended on others.  However, just keeping track of causality alone does not provide a total order, which provides an ordering of every single operation on the database - this is what is needed for linearizability.

Note that having a total order may be overkill, oftentimes it is sufficient to just preserve causal consistency (can be done with the version vectors described earlier) without incurring the large performance penalties required by linearizability.

We can use Lamport timestamps in order to generate sequence numbers across multiple machines consistent with causality:
Each node has a unique identifier, and keeps a counter of the number of operations it has processed
The timestamp is a tuple of the counter and the node ID, use an arbitrary ordering between the nodes and the counter to create a total order
Every node and client keeps track of the maximum counter value it has seen so far, and includes the maximum on every request
When a node receives a request or response with a maximum counter greater than its own counter value, it increases its own counter to that maximum
Unlike version vectors, Lamport timestamps cannot show which operations were concurrent with one another, though they do provide a total ordering

Lamport timestamps are still not totally sufficient as they can only provide answers to concurrency bugs after the fact - in the moment problems like dealing with uniqueness constraints across different replicas cannot be solved.

To deal with these problems, we can discuss total order broadcast, which is a protocol for exchanging messages between nodes.  This protocol ensures that no messages are lost, and that messages are delivered to every node in the same order each time.  The reason this is stronger than timestamp ordering is that a node cannot retroactively insert a message into an earlier position in the order if later messages have been delivered.  Total order broadcast is in this way like a log.

Both linearizable storage and total order broadcast are equivalent to consensus: you need to get all of the nodes to agree on a value for every operation.

Distributed Transactions and Consensus

Although we have now spoken about some problems that can be reduced to consensus, it now seems best to actually discuss some ways that consensus can be achieved.  Firstly, we can talk about two phase commit, which is somewhat inefficient, but solves the problem of atomic commit (getting all replicas to agree on whether a transaction should be committed or aborted).

Two phase commit:
Algorithm used to solve the atomic commit problem
Coordinator node (the application) sends writes to each node
Coordinator then sends each node a prepare requests, in which each node responds saying whether it will be able to commit
If all the nodes can commit, the coordinator tells them to do so, otherwise it tells them all to abort
Coordinator has internal log with its decisions for each transaction in the event that it crashes
If the request to commit or abort does not reach all the participants, the coordinator must keep retrying on all nodes until they get the message, cannot accept a timeout
Two points of no return
Participants (database replicas) that say yes in the prepare stage must eventually commit the write and are not allowed to eventually abort it
Once the coordinator decides to commit or abort it must get this through to all of the participant nodes
The coordinator is a single point of failure and if it crashes none of the nodes can abort or commit after the have done their preparations (should be replicated)
To avoid this happening we would need a perfect failure detector to perform some sort of failover which is impossible due to unbounded network delay
When this happens the replicas often have a lock grabbed on many rows, which may prevent a significant amount of transactions until the coordinator node is back

Database internal distributed transactions (transactions using only the same database technology) can actually be pretty quick and optimized, however when using multiple different types of data systems (like databases, message brokers, email services), you need a transaction API (such as XA) which is often quite slow.

Unlike two phase commit, good consensus algorithms reach agreement by using a majority (quorum) of nodes, in order to improve availability.  After new leaders are elected in a subsequent epoch (monotonically increasing in order to prevent split brain), consensus algorithms define a recovery process which nodes can use to get into a consistent state.

Coordination services such as ZooKeeper are used internally in many other popular libraries, and are a replicated in memory key value store that allows total order broadcast to your database replicas.

Batch Processing

Batch processing is useful for when you want to perform some operations on a potentially very large, fixed size, input set of files and return an output.  Typically these files are in some sort of distributed file store like Hadoop, and can be transformed using certain batch processing tools like MapReduce to a different output.  However, MapReduce is itself not perfect and there are many optimizations that can be made to speed up batch processing in different scenarios of computation.

MapReduce:
Allows passing in files and returns files to be piped into subsequent MapReduce calls
Break each file into records, call the mapper function to extract a key and value from each input record
Sort all of the key-value pairs by key
Call the reducer function to iterate over the sorted key-value pairs
Only write custom code for the mapper and reducers
Computation parallelized across many machines automatically
Designed for frequent faults, if a single map or reduce task fails only it gets restarted
This is because they are often run on shared servers which sometimes need to take back resources and will kill a MapReduce job to do so

Joins in MapReduce:
Resolving all occurrences of some association within a dataset
Actually calling the database to resolve every join is too expensive as it requires a multitude of slow network calls
Put a local copy of the database in the distributed file in order to improve locality
Sort-merge joins (reduce side join, join logic done in reducer)
Have a mapper for both relevant database tables, and then send the result of both mappers to the same reducer nodes, making sure to sort them in between so that all of the relevant information is next to one another
If there are certain keys which are very popular (hot keys), such that they need to be on more than one partition, randomly assign the partition for each instance of a given hotkey and replicate the necessary database information to each partition
While these are often slower, do not need to make any assumptions about data
Broadcast hash joins (map side join, join logic done in mapper)
If one of the datasets being joined on is so small that it can fit on memory in each of the mappers
Use an in memory hash table on each mapper to do the joining
Partitioned hash joins (map side join)
Same as broadcast hash join but for when each side of the join is partitioned the same way, do a broadcast hash join for each partition
If they are partitioned and sorted in the same way, one dataset does not even be loaded into memory, because a mapper can do the same merging operation that would normally be done by a reducer

When to use batch processing:
Building search indexes
Performing large computations that need to be precomputed (possibly using machine learning)
Build databases into batch jobs as opposed to slowing things down with network calls
Can then later export these files from the distributed file system
Performing ETL processes (taking data from transactional database and converting it for analytics)

Alternatives to MapReduce:
MapReduce is not actually very efficient because when chaining together many MapReduce jobs, you need to wait for one to completely finish before starting the next, and there is a lot of time wasted in writing out the intermediate state to disk
Bad as certain hotkeys or stragglers can take much longer and delay the whole thing
Should be using dataflow engines (like Spark)
Parallelize computation to run as quickly as possible over multiple user defined functions called operators
Reduces the amount of unnecessary mappers
Data dependencies explicitly declared so that the engine can optimize for these
Slightly less fault tolerant because data not materialized to intermediate state, so if it is lost, it is recomputed from the previous data needed to make the calculations
This means that the functions must be deterministic

Batch processing is also frequently used on graph data in order to make things like recommendation algorithms.  MapReduce is not efficient for this because the graph data infrequently changes, however MapReduce would create an entirely new output dataset.  Instead, it is better to use the Pregel processing model, where one vertex can send a message to another vertex along an edge of a path.  In each iteration of the batch processing, the vertex receives all the messages sent to it from the prior step, and then sends out new messages.  This goes on until an end condition is met. The nodes remember their state in memory so the entire graph does not need to be rewritten.  By occasionally writing vertex state to disk, a deterministic algorithm becomes fault tolerant in the event of a crash.

Stream Processing

Unlike batch processing, stream processing is quite similar but instead processes an unbounded set of data.  This is useful for when you want data to be processed as quickly as possible in an asynchronous manner, as we will see with something like message brokers.  While messages can in theory be sent directly from the producer to a consumer, a message broker allows for more fault tolerance and handles message loss for you.

Message brokers:
Kind of database optimized for handling message streams, clients can come and go, handles durability
Generally queue up messages if there are too many as opposed to just dropping them
Many message brokers will delete a message once it has been successfully delivered to consumers, as a result assume a small queue
When there are multiple consumers, two main patterns of messaging are used
Load balancing delivers each message to one consumer to share the work between them
Fan out delivers the message to all of the consumers
When a consumer finishes processing a message it sends an acknowledgement back to the queue
Unless you are using a separate consumer per queue, the fact that a consumer can crash while handling a message means that messages may be delivered out of order

Log based message brokers:
In the traditional style of message queues mentioned above, messages that have been acknowledged are deleted and can never be handled again
Adding new consumers means that they can only access new messages
In log based message brokers, every message is appended to the end of a log, and consumers read the end of the log sequentially, waiting for new messages to pop up
Log can be partitioned into many different queues
A topic is a group of partitions carrying messages of the same type
Each partition can be replicated for fault tolerance, and assigned to a group of nodes for load balancing
In each partition the broker assigns a monotonically increasing sequence number to every message, to assist with ordering them
Keeps track of which offset a consumer is on for each partition in the event that one of them crashes, improves fault tolerance
These can be made fast by using many partitions, however since each partition just has one consumer a single slow message can slow down the processing of the partition
If messages are expensive to process and order doesn’t matter and you care more about parallelizing them then an in memory queue may be better
Once the log gets large enough, it can be split into segments which can be discarded or archived
Can easily replay messages in order to try processing them again because they are not deleted from a log

Change Data Capture:
Treats a database leader as the leader of all other data systems that need to stay in sync (such as caches, search indexes, analytics databases)
Does so by taking the changes to a database and putting them into a log based message broker which can be used to update all of the other derived data sources
In order to keep the log small so that other derived data systems can be added in the future, we can use log compaction as is done with indexes

Event Sourcing:
Similar to change data capture, but with some subtle differences
The database is not the source of truth, with changes being derived from it
Instead have a central append only log of events, which do not log what the changes are in the database, but instead what the user is actually doing on the site
Derive your other data systems from the logs of events
More maintainable because other schemas can be derived from the same logs of events in the future, and makes things easier to debug (what actually happened on the client side, not just the state changes that client actions caused)
Does require asynchronous writes unless you want a large write penalty

Streams and time:
Hard to deal with all events in a given window because one could arrive to a stream late due to a network delay
Need to decide whether to disregard it or add it to the window after the fact
If a user clock is unreliable can potentially compare it to the server clock at the time of message sending to get an offset between the two, and then add it to the actual event time
Assumes network delay is minimal which it is not necessarily
When dealing with windows, if dealing with overlapping windows on fixed intervals (hopping windows), use tumbling windows (non overlapping windows of fixed length) and aggregate them together for the hopping window
Sliding windows with no fixed interval start and end points, but a fixed duration, can be implemented by keeping a buffer of events sorted by time and removing old events when they expire from the window

Stream Joins:
Just like batch processing, streams need to be able to perform joins on other datasets
However it is a bit more challenging because new events can appear anytime on a stream
Stream-stream join (good for joining two related streams of data)
If two streams are sending related events that you may want to join with one another, both streams must maintain state (probably for all events within a certain time window)
Can use an index to do so on the join key, and each stream can check the index when events come in
On expiration of an event from said time window you can record that there was no corresponding other event to join it with (useful in certain analytics cases)
Stream-table join (good for enriching data before sending to another stream)
Joining stream events with information from the database table, querying the database every time is too slow, should keep a local copy
However this table needs to be updated over time which can be done by the stream processor subscribing to the database changes of the actual database and updating its local copy
Table-table join (two streams maintaining local copies of tables that have to do joins)
Use change data captures to keep two tables up to date for each stream, and accordingly take the result of the join and send it where it needs to go
One issue is that these joins become nondeterministic
Can maybe be addressed by using a unique ID for the thing being joined with, but this requires much more storage

Fault tolerance:
Want to be able to ensure that each message is processed exactly once, no less and no more
Can use micro batching or checkpointing to retain state of stream
Break stream into small blocks, each of which is treated as a batch process which can be retried
Can also keep state to generate checkpoints of the stream, so that on crash it can restart from the most recent checkpoint
Not useful for stopping things external to the stream (such as sending an email) from occurring twice
Can use atomic transactions
Can use idempotence
An operation that can be done multiple times and has the effect of only being performed once, use these in processors to avoid processing messages many times

Load Balancing

The load balancer is a necessary component in any distributed system which helps to spread traffic around a cluster of servers or nodes.  It keeps track of the status of said servers so that it stops sending them requests if they crash.  Load balancers can and probably should be added between any layers where there are multiple nodes running so that traffic can be split up.

Benefits of load balancing:
Parallelization of server tasks
Less downtime of servers
How they work:
Periodically send health checks or heart beats to servers in order to determine whether or not they are running, adjust their pool of healthy servers accordingly
Use one of many algorithms to route traffic
Least connection method directs traffic to the server with the fewest active connections, good when many persistent connections (such as webhooks)
Least response time method directs traffic to server with fewest active connections and lowest average response time
Least bandwidth method directs to server currently serving least amount of traffic in megabits per second
Round robin just creates an order to the server and sends each request to the next server in the order
Weighted round robin is the same as round robin, but taking into account a weight for each server which indicates its computing capacity
IP hash uses a hash of the client IP address in order to determine which server to route to (layer 4 load balancing, which can only look at network details)
Can also use consistent hashing such that the majority of the requests go to the same server even when servers are added and taken away in order to increase in memory cache relevance on the server itself
Layer 7 load balancing hashes based on the contents of the actual request, requires more computing resources but more flexibility

Fault tolerance:
The load balancer exists to help reduce single points of failure but it itself is a single point of failure
Can use a cluster of load balancers which send heartbeats to one another such that if one load balancer fails the other takes over (active and passive load balancer)

Caching

In a distributed system, caching data allows you to store copies of data on either faster hardware, or just hardware located closer to the end user that will request it.  While this can greatly speed up certain read requests too, caching can at times become complicated, as storing multiple copies of data will inevitably lead to having to deal with stale (outdated) data.  Additionally, as they are made for faster reads, caches often have far fewer memory than databases, so it is important that we delete old entries from the cache.

Types of cache:
Hardware caches
On CPU (L1, L2, L3 cache)
Often the computer will use memory to cache disk results
Application server cache
Memory on the actual application server that remembers the results of certain queries, and returns them back if they are requested again
Still no guarantee that all requests will hit these, should instead use a global or distributed cache
Content Distribution Network (CDN)
Serve large amounts of static media
Request asks CDN for content, and if it is not there it queries the backend, serve it, and cache it locally (pull CDN)
Also possible to directly upload content, good for sites with either low traffic or data that does not change very frequently (like a newspaper)
Require changing URLs for static content, need to be careful to not serve stale content


Cache write policies:
Write through    
Data written to cache and database at the same time
Allows for complete data consistency (assuming neither fails, in which case may need distributed transactions which are slow)
Slows down write requests
Write around
Just write to the database
On a cache miss pull data from the database into the cache
Write back
Data first written to the cache only
Write to permanent storage only done after some amount of time
While this is the fastest we risk inconsistencies in the data if the cache crashes and cannot push to the database

Cache eviction policies:
First in first out
Last in first out
Least recently used (probably the best)
Least frequently used
Random replacement

Proxies

Proxies act as an intermediary server between the client and application server that can fulfill a variety of purposes such as adding information to a request, checking its own cache, or encrypting a message

Types of proxies:
Open proxy    
Accessible by any internet user
Anonymous proxies reveal its identity as a server but does not disclose the IP address of the user
Transparent proxies also identify both themselves and the IP address of the user, good for caching websites
Reverse proxy
Retrieves resources from one or more application servers and then returns the result to the client as if they were their own
Can do things such as encryption and decryption to save application servers from doing these potentially expensive operations

Consistent Hashing

Consistent hashing is a way of mapping keys to a given partition in a load balancing situation to ensure that when new nodes are added as few keys as possible are rebalanced to maximize existing caching and minimize network load and data invalidation.

To do so, create a ring representing the range of a given hash function, and hash each server partition to it.  To find which server a key goes to, take the hash of it, and move clockwise around the ring until hitting a server hash.  If a partition fails, move the keys that were on it to the next partition in the ring.  If a new partition is added, move the existing keys that are just before it to said partition.  Instead of just having one location for each partition on the ring, have a few locations for each in order to further randomize distribution.

Long Polling, WebSockets, Server Sent Events

All three of the topics above are methods to provide real time updates to a client from an application server.  However, each has their benefits and drawbacks which we can discuss below.

The worst option is likely polling, in which a client repeatedly makes http requests to a server in order to try and see if any changes have been made.  If many clients are doing so at the same time, this can overload the server.  This being said, it is easy to implement.

Long polling:
Open an http connection with the server and do not close it until the server has something to respond with
Once the server responds the client then makes another long polling request

WebSockets:
Full duplex communication channel between client and server
Lower message overhead due to not needing to resend headers
A bit harder to implement
Can only have as many open webhook connections as ports, so 65,000
Server Sent Events:
Only one way events from server to client, keeps an open connection
Best for if the server is generating data in a loop and will send multiple requests to clients

