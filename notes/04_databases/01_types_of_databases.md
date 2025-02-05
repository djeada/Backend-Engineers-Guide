## Types of Databases  
Databases store and organize data so that applications and users can retrieve, manage, and manipulate information efficiently. The choice of database often depends on data structure requirements, scale, performance expectations, and the nature of the workload. Over the years, numerous types of databases have emerged, each suited to different use cases. This set of notes explores various database models, their architectures, strengths, and ideal deployment scenarios.

### Relational Databases (RDBMS)  
Relational databases organize data into structured tables (relations) consisting of rows (tuples) and columns (attributes). They rely on a rigid schema and support powerful querying via Structured Query Language (SQL).

#### Core Ideas  
1) Data is represented in two-dimensional tables.  
2) Relationships between tables are defined through foreign keys.  
3) ACID (Atomicity, Consistency, Isolation, Durability) guarantees transactional integrity.  
4) SQL queries enable complex joins, aggregations, and constraints.

### Example Tables  

```
 Table: customers
 +----+-----------------+-----------------+
 | id | name            | email           |
 +----+-----------------+-----------------+
 | 1  | Alice Johnson   | alice@example.com |
 | 2  | Bob Smith       | bob@example.com   |
 +----+-----------------+-----------------+

 Table: orders
 +----+------------+-------------+----------+
 | id | order_date | customer_id | total    |
 +----+------------+-------------+----------+
 | 1  | 2025-01-02 | 1           | 50.00    |
 | 2  | 2025-01-03 | 2           | 75.00    |
 +----+------------+-------------+----------+
```

#### Pros  
1) Rigid schema enforces data consistency.  
2) Powerful SQL ecosystem with decades of tooling and community support.  
3) Transactions preserve data integrity and handle concurrent writes safely.

#### Cons  
1) Horizontal scaling can be challenging, often requiring sharding or replicas.  
2) Schema changes may be complex in agile environments.  
3) Fixed schema might slow performance if data structures evolve frequently.

#### Popular Implementations  
MySQL, PostgreSQL, Microsoft SQL Server, Oracle Database.

### NoSQL Databases  
NoSQL (“Not Only SQL”) is an umbrella term for databases that diverge from the relational model. They often support flexible schemas, scale horizontally on clusters of commodity hardware, and handle large, rapidly changing datasets.

#### Key-Value Stores  
They store data in a simple key-value format, much like a dictionary or hash map. Each record is identified by a key, and its associated value can be any blob of data.

- **Pros**: Extremely fast lookups by key, good for caching or real-time session data.  
- **Cons**: Limited querying abilities beyond key-based retrieval.  
- **Popular Systems**: Redis, Amazon DynamoDB (when used in a key-value style).

```
 Key: session12345
 Value: {"cartItems": 3, "lastLogin": "2025-01-05", ...}
```

#### Document Stores  
They store data as structured documents (often JSON). Each document can have a unique schema, facilitating rapid schema evolution.

- **Pros**: Flexible schema, intuitive for storing objects.  
- **Cons**: Complex queries might be less optimized compared to relational joins.  
- **Popular Systems**: MongoDB, CouchDB, Firebase Firestore.

```
{
  "_id": "user123",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "orders": [
    { "orderId": 101, "total": 50.0 },
    { "orderId": 102, "total": 75.0 }
  ]
}
```

#### Column-Family Stores  
They group data by column families instead of rows. This approach helps optimize queries that only access subsets of columns, commonly used for analytical workloads.

- **Pros**: Highly scalable for wide-column data, efficient for column-based operations.  
- **Cons**: Can be more complex to model relationships.  
- **Popular Systems**: Apache Cassandra, HBase.

```
   Row Key     |  CF: Personal           |  CF: Address
---------------------------------------------------------
 "user123"     | name = "Alice Johnson"  |  city = "New York"
               | email = "alice@x.com"   |  zip  = "10001"
---------------------------------------------------------
```

#### Graph Databases  
They store data as nodes and edges, where edges represent relationships between nodes. This model fits well for social networks, recommendation engines, and knowledge graphs.

- **Pros**: Simple traversal for connected data, flexible schema for relationship-heavy structures.  
- **Cons**: Not as optimized for large-scale tabular or aggregate queries.  
- **Popular Systems**: Neo4j, Amazon Neptune, ArangoDB.

```
 (Alice) -- friends_with --> (Bob)
   |                           |
 works_at                    likes
   v                           v
 (Company X)               (Music Genre)
```

### Time Series Databases  
Time series databases efficiently store and query data points indexed by timestamps, often used for monitoring, IoT sensor data, or financial market feeds.

#### Characteristics  
1) Data is typically written in an append-only fashion with timestamps.  
2) Specialized query optimizations (window functions, downsampling).  
3) Retention policies automatically expire old data.

#### Pros  
1) Optimized for high-ingest rates and fast queries on ranges of time.  
2) Built-in functions for aggregates over time windows.  

#### Cons  
1) Less flexible for complex relational queries unrelated to time.  
2) Schema design often tailored to specific metric structures.

#### Popular Systems  
InfluxDB, TimescaleDB (extension of PostgreSQL), Prometheus (for ephemeral monitoring data).

### Object-Oriented Databases  
They store data as objects, similar to how object-oriented programming languages represent data. Each record is an object with attributes and methods.

#### Pros  
1) Natural integration with OO languages (Java, C++, etc.).  
2) Potentially fewer layers of abstraction between code and stored data.  

#### Cons  
1) Less widely adopted than relational or NoSQL models.  
2) Query optimization can be less mature.  

#### Popular Systems  
db4o (database for objects), ObjectDB.

### NewSQL Databases  
They blend ACID transactions of traditional RDBMS with the horizontal scalability of NoSQL. They aim to solve the “scaling problems” of relational systems while preserving strong consistency.

#### Pros  
1) SQL interface and relational semantics.  
2) Distributed architecture for horizontal scale.  
3) Maintains ACID guarantees.  

#### Cons  
1) Less mature than traditional RDBMS.  
2) Can be complex to deploy and manage in distributed environments.  

#### Popular Systems  
CockroachDB, Google Cloud Spanner, TiDB.

### Distributed and Cloud-Native Databases  
Some databases are designed from the ground up for distributed deployments across multiple regions. They offer automatic sharding, replication, and fault tolerance.

#### Key Attributes  
1) Data is split into shards or partitions across nodes.  
2) Replication ensures data redundancy for fault tolerance.  
3) Global or multi-region deployment can reduce latency for geo-distributed workloads.

```
        +----------------------------------+
        |       Distributed Cluster        |
        +----------------------------------+
        |  Node A   |  Node B   |  Node C  |
        +-----------+----------+----------+
        | Shard1,2  | Shard3,4 | Shard5,6 |
        +-----------+----------+----------+
            ^           ^          ^
            |  Replicas, consistent hashing
            |  or partition key
            |
         Clients distribute queries across nodes
```

### Selecting the Right Database  
1) **Data Structure**: Relational data often fits RDBMS, while semi-structured JSON data might benefit from document stores.  
2) **Query Patterns**: Key-based lookups align well with key-value stores, while highly connected data might need a graph approach.  
3) **Scalability**: Horizontal scaling can be easier with NoSQL, NewSQL, or distributed RDBMS solutions.  
4) **Consistency Model**: ACID (strong consistency) or eventual consistency.  
5) **Performance**: Latency needs, data ingestion rates, and concurrency levels.  
6) **Ecosystem and Tooling**: Established solutions have robust drivers, libraries, and community support.

### Example Metrics and Formulas for Database Performance  

#### Transactions per Second (TPS)  
A common measure for OLTP systems. If `N_trx` transactions occur over a period `T_seconds`, TPS is:

```
TPS = N_trx / T_seconds
```

#### Read/Write Latency  
Often measured as average or percentile latencies:

```
Avg_Read_Latency = (Sum_of_Read_Durations) / (Number_of_Reads)
```

#### Sharding and Partitioning  
When distributing data across multiple shards, a formula for node usage might be:

```
Data_Per_Node = (Total_Data_Volume) / (Number_of_Shards)
```

#### Replication  
Replication ensures fault tolerance at the cost of overhead:

```
Effective_Storage = (Number_of_Replicas) * (Data_Volume)
```

In synchronous replication, writes commit only after multiple nodes confirm the update, which can increase latency.
