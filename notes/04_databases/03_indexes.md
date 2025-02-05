## Indexing  

Indexing is one of the most effective ways to optimize database queries. By maintaining auxiliary data structures that map certain key values to their physical or logical locations, indexes allow a database to rapidly locate rows that match a search condition. This reduces the number of full-table scans required, significantly speeding up SELECT operations as well as certain UPDATE and DELETE statements that rely on indexed columns. In many relational databases, proper indexing is key to high performance. This document outlines the core concepts, different types of indexes, how to create and manage them in common database systems, and best practices to avoid pitfalls.

### Concepts and Purpose

#### Why Indexes Exist  
Without indexes, a database engine must scan every row in a table to find matches for a given condition (e.g., `WHERE name = 'Alice'`). This approach can be expensive if the table has millions of rows, leading to slow queries. An index stores enough information for the database to skip large portions of data that do not match the query.

#### How Indexes Are Organized  
Indexes typically use data structures like B-trees, hash tables, or specialized index structures (e.g., GIN in PostgreSQL, or an LSM tree in some NoSQL systems). Regardless of implementation details, the essential principle is that the index is smaller (or more efficiently traversed) than the full table, making lookups faster.

#### Trade-offs  
1. **Improved Read Performance**: Queries filtering or sorting by indexed columns can run significantly faster.  
2. **Decreased Write Performance**: INSERTs, UPDATEs, and DELETEs must also update the index, adding overhead.  
3. **Space Overhead**: Indexes require additional storage on disk and memory usage.

### Types of Indexes

#### B-Tree Indexes  
Most relational databases default to B-tree (or a variation like B+ tree). B-tree indexes suit common lookups on columns that are used in equality or range comparisons.

1. **Equality**: `WHERE column = 42`  
2. **Range**: `WHERE column BETWEEN 10 AND 20`  
3. **Sorting**: Queries with `ORDER BY column ASC` can utilize B-tree indexes if the sort matches the index order.

**ASCII Diagram of a Simplified B-Tree**  
```
             (Root)
             /    \
            /      \
        [10,20]   [30,40]
         /  \        /  \
     leaves ...   leaves ...
```
In actual databases, the B-tree might have multiple levels and nodes that contain many keys.

#### Hash Indexes  
Hash-based indexes store a hash of the indexed column. They offer O(1) equality lookups (`=`) if the hash function is well-distributed, but are typically limited in their support for range queries or ordering. Some DBs (like PostgreSQL) provide hash indexes, but they are often overshadowed by B-tree flexibility.

#### Bitmap Indexes  
Bitmap indexes encode row IDs for each distinct column value as a bitmap. They can be very space-efficient for low-cardinality columns (i.e., columns with few distinct values, such as a “status” field). They allow bitwise operations to combine multiple conditions quickly.

**Example**:  
- Column “status” has possible values [‘open’, ‘closed’, ‘pending’].  
- The database stores a bitmap for each status, marking which row IDs have that status.

#### Full-Text and Specialized Indexes  
- **Full-Text Index**: Helps searching text fields for keyword occurrences, often employing an inverted index.  
- **Spatial Index**: Manages geometry data for proximity and region queries (e.g., find points near a location).  
- **GIN/GIST Index** (PostgreSQL): Generalized Inverted Index or Generalized Search Tree for complex data types (JSON fields, arrays, hstore, geometric data).

#### Composite/Multi-Column Indexes  
An index can cover multiple columns, typically in a specified order. For example, `(country, city)` might speed queries that filter by both. However, only queries that match the leading columns of the index can effectively use it. If the query only filters by `city` and not by `country`, the composite index might not help (depending on the DB engine’s optimizations).

```sql
-- Example creation of a composite index in PostgreSQL or MySQL
CREATE INDEX idx_country_city ON addresses(country, city);
```

#### Covering Indexes  
Some systems (like MySQL’s InnoDB) offer “covering indexes,” where all columns requested by a SELECT statement are part of the index, so the engine can answer the query from the index alone without reading full table rows. This optimization can drastically improve performance for read-heavy workloads.

### Creating and Managing Indexes  

#### Syntax Examples

##### PostgreSQL  
```sql
-- Create a B-tree index on the "username" column
CREATE INDEX idx_username ON users (username);

-- Create a composite index on "country" and "city"
CREATE INDEX idx_location ON addresses (country, city);

-- Create a unique index
CREATE UNIQUE INDEX idx_unique_email ON users (email);
```

##### MySQL / MariaDB  
```sql
-- Create an index on "last_name"
CREATE INDEX idx_last_name ON employees (last_name);

-- Create a composite index
CREATE INDEX idx_full_name ON employees (last_name, first_name);

-- Dropping an index
DROP INDEX idx_last_name ON employees;
```

##### SQL Server (T-SQL)  
```sql
CREATE INDEX idx_customer_city ON Customers (City);

-- Clustered index (SQL Server concept: determines physical storage order)
CREATE CLUSTERED INDEX idx_custid ON Customers(CustomerID);

-- Dropping an index
DROP INDEX idx_customer_city ON Customers;
```

#### Creating Indexes on Large Tables  
For big tables, creating an index can lock the table for the duration of the build. Some engines allow “online” or “concurrent” index builds to minimize blocking.

**PostgreSQL** (Concurrent build):
```sql
CREATE INDEX CONCURRENTLY idx_bigtable_col1 ON bigtable (col1);
```
**MySQL** (Online DDL in InnoDB):
```sql
ALTER TABLE bigtable ADD INDEX idx_col1(col1), ALGORITHM=INPLACE, LOCK=NONE;
```

These options reduce downtime but can be slower or require extra resources.

#### Unique Indexes  
A unique index enforces that no two rows have the same indexed value. If you attempt an insert or update that duplicates the indexed field, the DB will throw an error. Typically used for fields like email addresses or user IDs.

#### Primary Key and Clustered Indexes  
Some database systems, such as SQL Server, treat the primary key as the default clustered index (i.e., it dictates the on-disk storage order). Others (PostgreSQL, MySQL InnoDB) also have concepts of clustering or rely on the primary key index for row retrieval.

### Performance Considerations  

#### Insert/Update Overhead  
Every row insertion or modification requires updating the associated indexes. The more indexes a table has, the more overhead. This can slow down high write loads if a table has an excessive number of indexes.

#### Selectivity and Cardinality  
An index is most useful if it significantly narrows down the rows the database must read. Columns with high cardinality (many distinct values) often benefit from indexing. Columns with very low cardinality (e.g., boolean or two possible statuses) might not help much unless used in combination with other columns (like a composite index).

#### Index Statistics  
Databases maintain internal statistics about distribution of column values. The query planner uses these stats to decide whether to use an index or do a sequential scan. If stats become stale, queries might degrade in performance. Periodic analyze/re-index operations keep stats accurate.

**ASCII Diagram** – In a simplified sense, the DB chooses either a sequential scan or an index scan:

```
                 Query arrives
                       |
    +--------(Check stats & cost)--------+
    |                                    |
    v                                    v
Sequantial Scan                Index Scan (Locate matching rows quickly)
    |                                    |
    v                                    v
Scan entire table        Use index to find row offsets, 
( Potentially slow )      fetch rows from table
```

### Advanced Features  

#### Partial (Filtered) Indexes  
Some databases (notably PostgreSQL) allow partial indexes restricted to rows meeting certain conditions. For example, only indexing “active” rows can reduce index size and overhead:

```sql
CREATE INDEX idx_active_users
ON users (last_login)
WHERE active = true;
```
Queries that filter `WHERE active = true` can utilize this partial index.

#### Covering Indexes (MySQL, SQL Server)  
An index that contains all queried columns is called a “covering index.” The DB can answer a query directly from the index structure. For example, if you SELECT only `first_name` and `last_name` from a table that has an index on `(first_name, last_name)`, the engine doesn’t need to touch the data pages.

#### Function/Expression Indexes  
Some DBs allow indexing the result of a function or expression. This helps if queries often filter on a computed value.

**PostgreSQL** Example:
```sql
CREATE INDEX idx_lower_email ON users ((lower(email)));
```
Then queries like `SELECT * FROM users WHERE lower(email) = 'alice@example.com';` can use the index.

#### Brin Indexes (PostgreSQL)  
Block Range Indexes (BRIN) store metadata about ranges of blocks in a table. They are space-efficient and can be beneficial for massive tables where data is naturally sorted (e.g., by time) but do not guarantee single-row precision.

#### Reindexing  
Over time, indexes can become fragmented or bloated, especially after many updates or deletes. Periodic reindexing compacts the index structure, improving lookup performance.

**PostgreSQL**:
```sql
REINDEX INDEX idx_username;
REINDEX TABLE users;
```

**MySQL**:
```sql
OPTIMIZE TABLE users;  -- can reorganize data and index structures
```

### Monitoring and Tuning  

1. **EXPLAIN Plans**: Evaluate how queries execute, check if indexes are used.  
   ```sql
   EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
   ```
   The plan might show “Index Scan” or “Index Cond” if an index is utilized.  

2. **Slow Query Logs**: Database servers can log queries that exceed a certain time threshold. Analyzing these logs highlights queries that might benefit from new or revised indexes.  

3. **Index Usage Statistics**: Some DB engines store usage counters for each index. If an index is rarely or never used, it can be dropped to improve write performance.  

4. **Maintenance Windows**: Large reorganizations or index builds might lock tables or hamper performance. Scheduling them off-peak can reduce user impact.

### Concrete Examples and Commands  

#### MySQL: Creating a Composite Index, Checking Use

**Create a table and indexes**:
```sql
CREATE TABLE orders (
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  order_date DATETIME,
  total_amount DECIMAL(10,2),
  status VARCHAR(20),
  INDEX idx_customer_date (customer_id, order_date)  -- composite index
);

-- Another single-column index for "status"
CREATE INDEX idx_status ON orders (status);
```

**Running EXPLAIN**:
```sql
EXPLAIN SELECT * 
FROM orders 
WHERE customer_id = 123 AND order_date >= '2025-01-01';
```
Expected plan to show it uses `idx_customer_date`.

**Dropping an index**:
```sql
DROP INDEX idx_status ON orders;
```
If we find we rarely filter by `status`, dropping this index can save overhead.

#### PostgreSQL: Function Index and Partial Index Example

```sql
-- Function index to ignore case in email lookups
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);

-- Index on the lower-cased version of email
CREATE INDEX idx_users_email_lower ON users ((lower(email)));

-- Partial index to handle only active users
CREATE INDEX idx_active_users_lower ON users ((lower(email))) WHERE is_active = true;
```

**Query**:
```sql
EXPLAIN ANALYZE
SELECT * FROM users
WHERE lower(email) = 'alice@example.com'
  AND is_active = true;
```
We expect the partial function index `idx_active_users_lower` to be used.

#### SQL Server: Clustered vs. Non-Clustered Index

```sql
CREATE TABLE Sales (
    SalesID INT PRIMARY KEY,          -- By default becomes a clustered index
    CustomerID INT NOT NULL,
    SaleDate DATETIME,
    Amount DECIMAL(10,2)
);

-- Non-clustered index on CustomerID
CREATE INDEX idx_customerid ON Sales (CustomerID);
```

**Clustered Index**: Physically orders the table by `SalesID`.  
**Non-Clustered Index**: A separate structure referencing the row pointers.

### Best Practices  

1. **Index Common Filter/Join Columns**: Create indexes on columns frequently used in `WHERE`, `JOIN`, or `ORDER BY` clauses.  
2. **Avoid Over-Indexing**: More indexes = more overhead on writes and extra storage. Evaluate if an index is truly beneficial.  
3. **Consider Composite Indexes**: Group columns often used together in queries, typically in the order they appear in the WHERE clause.  
4. **Use Partial or Filtered Indexes**: If only a subset of rows matter for a frequent query, partial indexes reduce size.  
5. **Maintain Stats**: Keep table and index statistics fresh so the query optimizer chooses the right plan.  
6. **Test with Real Queries**: Don’t guess which indexes are best—use `EXPLAIN` or query analysis to confirm.  
