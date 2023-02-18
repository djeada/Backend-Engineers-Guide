## Indexes
Indexes provide a way for databases to quickly search for rows based on certain values of the tuple that defines a record. This speeds up reads and reduces the time complexity from O(n) to O(log n). However, indexes also come with tradeoffs, as they slow down writes due to additional work needed to maintain the data formatting for the index.

### Log Structured Storage
Log structured storage is a common way of creating an index. It involves writing data to a log and then compacting the log. This is done by deleting any old values of a given key and keeping only the newest value. Segments are created by breaking the log into multiple files and merging them afterwards.

#### Hash Indexes
Hash indexes involve putting a key in an in-memory hashmap, where the value is the memory address of the proper row. Writes update the hashmap, but the downside is that all keys must fit in memory, and range queries are inefficient.

#### SSTables and LSM-Trees
SSTables and LSM-Trees keep each log structured storage segment sorted by key. Merging segments is done by sequentially going through each and starting with the lowest key. This is done in linear time and the most recent value for a given key is kept. No longer is it necessary to keep all keys in memory, just a few. Reads first check the memtable and then traverse through the disk segments from newest to oldest. From time to time, segments are merged and compacted.

#### B-Trees
B-Trees are the most common implementation of database indexes. They involve breaking the database into fixed-size blocks or pages and reading or writing one page at a time, aligning nicely with disks which are also broken into blocks. The disk is turned into a tree, where each node of the tree has pointers with sparse key names in between them. To update values, find them in the B-tree and change them. To add values, find where the key should be and add it to that page. A write-ahead log of things that the B-Tree will do is kept in order to recreate the tree on a crash.

### Secondary Indexes
Secondary indexes can be constructed from the above data structures by making them point to a list or appending the primary key of the row onto the secondary index key to make them unique. It is often preferable to store the actual rows in an append-only heap file, with the key value mapping pointing to the offset of said row. Alternatively, the actual values can be stored in the index (clustered index). As a middle ground, a covering index can be used which stores only a few columns of the row in the index.

Multicolumn indexes can also be created by concatenating fields, but one must be careful when doing this as it is done using an outer sort order with an inner one, meaning not all queries will use the index. Some databases have true multidimensional indexes.
