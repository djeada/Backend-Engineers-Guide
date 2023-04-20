## Indexes
Indexes help databases quickly search for rows based on specific values in a record. They speed up reads but slow down writes because more work is needed to maintain the index.

### Log Structured Storage
Log structured storage is a way to create an index. It writes data to a log, then compacts the log by deleting old values and keeping new ones. Segments are made by breaking the log into files and merging them.

#### Hash Indexes
Hash indexes put a key in an in-memory hashmap, where the value is the memory address of the row. Writes update the hashmap, but all keys must fit in memory, and range queries are slow.

#### SSTables and LSM-Trees
SSTables and LSM-Trees sort log structured storage segments by key. Merging is done by going through each segment and keeping the most recent value for a key. Not all keys need to be in memory, just a few. Reads check the memtable and disk segments from newest to oldest. Segments are merged and compacted.

#### B-Trees
B-Trees are common in database indexes. They divide the database into fixed-size blocks or pages and read or write one page at a time. The disk becomes a tree with nodes having pointers and sparse key names. To update values, find them in the B-Tree and change them. To add values, find where the key should be and add it to that page. A write-ahead log is used to recreate the tree if it crashes.

### Secondary Indexes
Secondary indexes can be made using the mentioned data structures, pointing to a list or appending the primary key of the row to the secondary index key. Rows can be stored in an append-only heap file, with the key value mapping pointing to the row's offset. Alternatively, actual values can be stored in the index (clustered index). A covering index stores only some columns of the row in the index.

Multicolumn indexes can be created by combining fields, but this must be done carefully, as not all queries will use the index. Some databases have true multidimensional indexes.
