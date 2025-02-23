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

#### Attributes  
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

- Relational data is typically managed in a relational database management system, while semi-structured JSON data is often stored in a document-oriented database.
- Key-based lookups perform best in key-value stores, and managing complex relationships in data may be achieved with graph databases.
- Systems that need to scale horizontally might use NoSQL, NewSQL, or distributed relational databases to handle growing workloads.
- Some applications require strict ACID compliance for consistency, whereas others operate effectively with eventual consistency.
- Database performance is influenced by factors such as response time, data ingestion rates, and the ability to handle concurrent operations.
- Mature database solutions offer a range of drivers, libraries, and community support that can simplify integration and ongoing development.

### Setting Up SQLite and Preparing the Benchmark Environment

SQLite is a file-based database, making it ideal for simple benchmarks. First, install Python (if not already installed) and use the built-in `sqlite3` module.

#### Steps to Set Up

1. **Install Python:**  
   Ensure Python 3 is installed on your machine.

2. **Create a Benchmark Script:**  
   Save the following script as `sqlite_benchmark.py` (you can adjust parameters as needed).

#### Measuring Transactions per Second (TPS)

This script creates a database, a table, and then inserts a fixed number of records while timing the operation. The TPS is calculated as the number of transactions divided by the elapsed time.

```python
import sqlite3
import time

# Configuration
DB_FILE = 'benchmark.db'
NUM_TRANSACTIONS = 10000  # Total number of inserts to simulate TPS measurement

# Connect to SQLite (creates the file if it doesn't exist)
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Setup: Drop table if exists and create a new one
cur.execute("DROP TABLE IF EXISTS test;")
cur.execute("CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT);")
conn.commit()

# Begin transaction for bulk insert performance (faster than individual commits)
start_time = time.time()
cur.execute("BEGIN TRANSACTION;")
for i in range(NUM_TRANSACTIONS):
    cur.execute("INSERT INTO test (data) VALUES (?);", (f"Sample data {i}",))
cur.execute("COMMIT;")
end_time = time.time()

# Calculate TPS
elapsed_time = end_time - start_time
TPS = NUM_TRANSACTIONS / elapsed_time

print(f"Transactions per Second (TPS): {TPS:.2f}")
print(f"Total time for {NUM_TRANSACTIONS} transactions: {elapsed_time:.2f} seconds")
```

**What to Expect:**  
- **TPS Value:** A higher TPS indicates the database efficiently handles many inserts.  
- **Interpretation:** If TPS is lower than expected, check for disk I/O constraints or adjust transaction boundaries.

> **TODO:** Plot TPS vs. number of transactions (e.g., X-axis: Number of Transactions, Y-axis: TPS).

#### Measuring Read/Write Latency

This script measures the latency for individual read and write operations. It calculates the average latency and can be extended to compute percentiles.

```python
import sqlite3
import time
import statistics

DB_FILE = 'benchmark.db'
NUM_OPERATIONS = 1000  # Number of operations for each test

# Connect to the same SQLite database
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Prepare a list to store latencies
write_latencies = []
read_latencies = []

# Write Latency Measurement: Single row insert and commit each time
for i in range(NUM_OPERATIONS):
    start = time.time()
    cur.execute("INSERT INTO test (data) VALUES (?);", (f"Write test data {i}",))
    conn.commit()  # Committing each time for measurement granularity
    end = time.time()
    write_latencies.append(end - start)

# Read Latency Measurement: Single SELECT query
for i in range(NUM_OPERATIONS):
    start = time.time()
    cur.execute("SELECT * FROM test WHERE id = ?;", (i + 1,))  # Using id from 1 to NUM_OPERATIONS
    cur.fetchone()
    end = time.time()
    read_latencies.append(end - start)

# Calculate averages
avg_write_latency = statistics.mean(write_latencies)
avg_read_latency = statistics.mean(read_latencies)

print(f"Average Write Latency: {avg_write_latency*1000:.2f} ms")
print(f"Average Read Latency: {avg_read_latency*1000:.2f} ms")

# Optional: Calculate percentiles
write_95th = statistics.quantiles(write_latencies, n=100)[94] * 1000
read_95th = statistics.quantiles(read_latencies, n=100)[94] * 1000

print(f"95th Percentile Write Latency: {write_95th:.2f} ms")
print(f"95th Percentile Read Latency: {read_95th:.2f} ms")
```

**What to Expect:**  
- **Write Latency:** Expect slightly higher latency per write if each commit is executed separately.  
- **Read Latency:** Should be very low for indexed lookups.  
- **Interpretation:** High latencies may indicate disk bottlenecks or suboptimal commit strategies.

> **TODO:** Plot read and write latencies (X-axis: Operation Number, Y-axis: Latency in ms).

#### Discussion on Sharding/Partitioning and Replication in SQLite

SQLite is designed as a single-file, embedded database, so traditional sharding, partitioning, and replication are not directly supported.  
However, for academic purposes, you can simulate:

- **Partitioning:**  
  Create multiple SQLite files representing different partitions. Measure file size or access times per file.
  
- **Replication:**  
  Manually copy the database file to simulate replication, or use a tool/script to monitor file synchronization times.

Since these are not native to SQLite, the scripts above focus on TPS and latency. For production systems requiring sharding/replication, consider a more robust RDBMS like PostgreSQL or MySQL.

> **TODO:** (If simulating partitioning) Plot data file sizes or access times across multiple SQLite databases.

#### Running the Benchmark and Analyzing the Results

##### Steps to Run the Benchmark:
1. **Save the Scripts:**  
   Create two separate Python scripts (or combine them with appropriate function calls) for TPS and latency tests.
   
2. **Execute the Scripts:**  
   Run the scripts from the command line:
   ```bash
   python sqlite_benchmark.py
   ```
   
3. **Collect the Output:**  
   Note the TPS, average latencies, and percentile latencies printed to the console.

##### Interpreting the Metrics:
- **TPS:**  
  - **High TPS:** Good for write-heavy OLTP scenarios.
  - **Low TPS:** May indicate disk I/O issues or inefficient transaction management.
- **Latency:**  
  - **Low Read/Write Latency:** Ideal for real-time applications.
  - **High Latency:** Investigate commit frequency, disk speed, or query complexity.
  
4. **Visualization:**  
   Use tools like Python’s matplotlib or external tools to create plots. For example:
   ```python
   import matplotlib.pyplot as plt

   # Example: Plotting Write Latencies
   plt.figure(figsize=(10, 5))
   plt.plot(write_latencies, label="Write Latency")
   plt.xlabel("Operation Number")
   plt.ylabel("Latency (seconds)")
   plt.title("Write Latency per Operation")
   plt.legend()
   plt.show()
   ```

> **TODO:** Enhance visualization by plotting multiple metrics together (e.g., TPS vs. Time, Latency Percentiles).
