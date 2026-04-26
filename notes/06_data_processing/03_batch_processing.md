## Batch Processing

Batch processing is a method for handling large volumes of data by grouping records into a single **batch** and processing them together. Unlike real-time or stream processing, batch processing does not usually require immediate results. Instead, data is collected over a period of time and processed on a schedule or when enough data has accumulated.

Batch processing is useful when tasks can run independently from user interactions. Common examples include nightly analytics jobs, financial reconciliation, report generation, data warehouse updates, machine learning feature preparation, log analysis, and large-scale file transformations.

A batch job may process thousands, millions, or billions of records at once. Because the workload can be planned and scheduled, batch systems are often optimized for throughput, fault tolerance, and efficient use of compute resources.

```text id="ep9q1g"
Batch Processing Flow

+---------------+    +--------------+    +----------------------------+    +--------------+
|               |    |              |    |                            |    |              |
| Data Sources  +--->+ Data Storage +--->+ Batch Processing System    +--->+ Final Output |
|               |    |              |    |   +-----+  +-----+  +-----+|    |              |
+---------------+    +--------------+    |   | J1  |  | J2  |  | J3  ||    +--------------+
      |                      |           |   +-----+  +-----+  +-----+|           |
      |                      |           +----------------------------+           |
      |                      |                           |                        |
      |                      |                           |                        |
      |______________________|___________________________|________________________|
                          Accumulation Over Time
```

Example batch input:

```json id="k9iuuk"
[
  {
    "customer": "Customer A",
    "category": "Electronics",
    "amount": 250
  },
  {
    "customer": "Customer B",
    "category": "Clothing",
    "amount": 50
  }
]
```

Example batch output:

```json id="y5ulff"
{
  "Electronics": 250,
  "Clothing": 50
}
```

In this simple example, the batch job reads multiple purchase records and produces totals grouped by category.

### How Batch Processing Works

Batch processing usually follows a predictable flow. Data is collected, stored, processed, and then written to an output destination.

The storage layer is important because batch jobs typically process data that has accumulated over time. This data may be stored in files, databases, object storage, data lakes, message queues, or warehouse staging tables.

A batch processing system then reads the stored data and runs one or more jobs. These jobs may be executed sequentially or in parallel. For large workloads, parallel processing is especially important because it allows many machines or workers to process different parts of the dataset at the same time.

The final output may be a report, dashboard table, transformed dataset, machine learning training set, search index, or another downstream input.

Example daily batch run:

```text id="v0qhux"
00:00 - Collect previous day's events
01:00 - Start batch aggregation job
01:30 - Write results to analytics warehouse
02:00 - Refresh dashboard tables
```

Example output:

```json id="id8gt2"
{
  "job": "daily_sales_summary",
  "recordsProcessed": 1200000,
  "durationMinutes": 28,
  "status": "success"
}
```

Batch processing is often chosen when the system values throughput and completeness more than immediate response time.

### MapReduce

MapReduce is a distributed batch processing model designed to process massive datasets across a cluster of machines. It breaks a large job into smaller tasks that can run in parallel.

MapReduce has two main phases: **Map** and **Reduce**. Between them is a **shuffle and sort** phase, where intermediate results are grouped by key.

The MapReduce framework handles much of the complexity of distributed execution. It splits input data, assigns work to nodes, moves intermediate data, groups keys, retries failed tasks, and writes final output.

```text id="q90ywx"
MapReduce Flow

                   +-----------------+
                   |    Input Data   |
                   +-----------------+
                           |
                           v
+-------------------------+-------------------------+
|    Split into Chunks / Distribute to Mappers      |
+-------------------------+-------------------------+
          |                                 |
          v                                 v
+---------------------+             +---------------------+
|  Map Function       |             |  Map Function       |
|  Process Chunks     |             |  Process Chunks     |
+---------+-----------+             +---------+-----------+
          |                                   |
          v                                   v
+---------------------+             +---------------------+
|  Intermediate Data  |             |  Intermediate Data  |
|  Key-Value Pairs    |             |  Key-Value Pairs    |
+---------+-----------+             +---------+-----------+
          |                                   |
          v                                   v
+---------------------+             +---------------------+
|     Shuffle &       |             |     Shuffle &       |
|     Sort Phase      |             |     Sort Phase      |
|   Group by Key      |             |   Group by Key      |
+---------+-----------+             +---------+-----------+
          |                                   |
          v                                   v
+---------------------+             +---------------------+
| Reduce Function     |             | Reduce Function     |
| Aggregate Results   |             | Aggregate Results   |
+---------+-----------+             +---------+-----------+
          |                                   |
          +----------------+------------------+
                           |
                           v
                   +-----------------+
                   |  Final Output   |
                   | Combined Data   |
                   +-----------------+
```

The **map stage** processes input records and emits intermediate key-value pairs. The **shuffle and sort phase** groups all values with the same key. The **reduce phase** combines each group into a final result.

Example high-level output:

```json id="e6gylw"
{
  "mapTasks": 12,
  "reduceTasks": 3,
  "recordsProcessed": 5000000,
  "status": "completed"
}
```

MapReduce is designed for fault tolerance. If one mapper or reducer fails, the framework can restart that task on another node.

#### Example Dataset

Suppose we have customer purchase data and want to calculate total sales by category.

| Customer   | Category    | Amount |
| ---------- | ----------- | -----: |
| Customer A | Electronics |    250 |
| Customer B | Clothing    |     50 |
| Customer C | Electronics |    300 |
| Customer D | Books       |     20 |
| Customer E | Clothing    |     80 |

The goal is to produce category totals.

Expected final output:

```text id="ba8o6i"
Electronics -> 550
Clothing -> 130
Books -> 20
```

#### Step 1: Map Phase

In the map phase, each input record is processed independently. The mapper emits a key-value pair. In this example, the key is the product category and the value is the purchase amount.

Pseudo-code:

```text id="d08kn8"
map(record):
    key = record.Category
    value = record.Amount
    emit(key, value)
```

Example mapper input:

```json id="k3rt3q"
{
  "Customer": "Customer A",
  "Category": "Electronics",
  "Amount": 250
}
```

Example mapper output:

```json id="2s0jt7"
{
  "key": "Electronics",
  "value": 250
}
```

For the full dataset, the mapper produces:

```text id="fnp8gm"
(Electronics, 250)
(Clothing, 50)
(Electronics, 300)
(Books, 20)
(Clothing, 80)
```

The map phase does not yet calculate totals. It only converts each record into a structure that can be grouped by category.

#### Step 2: Shuffle and Sort Phase

After mapping, the MapReduce framework automatically groups values by key. All values for `Electronics` go together, all values for `Clothing` go together, and so on.

Grouped output:

```text id="dh3z5f"
Electronics: [250, 300]
Clothing: [50, 80]
Books: [20]
```

Example shuffle output:

```json id="o9w2x6"
{
  "Electronics": [250, 300],
  "Clothing": [50, 80],
  "Books": [20]
}
```

This step prepares the data for reduction. The reducer can now process each category with all of its values available together.


#### Step 3: Reduce Phase

The reduce phase receives one key and a list of values. It then performs an aggregation operation. In this example, the reducer sums purchase amounts for each category.

Pseudo-code:

```text id="8lmnuj"
reduce(key, values):
    total = 0
    for value in values:
        total += value
    emit(key, total)
```

Example reducer input:

```json id="1vxotp"
{
  "key": "Electronics",
  "values": [250, 300]
}
```

Example reducer output:

```json id="41e0ih"
{
  "key": "Electronics",
  "total": 550
}
```

Applying the reducer to each group:

```text id="5l3jpo"
Electronics: 250 + 300 = 550
Clothing: 50 + 80 = 130
Books: 20 = 20
```

#### Final Output

The final output is a set of key-result pairs:

```text id="240cv5"
Electronics -> 550
Clothing -> 130
Books -> 20
```

Example JSON output:

```json id="z5ppvl"
{
  "Electronics": 550,
  "Clothing": 130,
  "Books": 20
}
```

This example shows how MapReduce breaks a problem into smaller pieces. Mappers process records independently, the framework groups intermediate values, and reducers aggregate the grouped data.

### Joins in MapReduce

Joins combine records from different datasets using a shared key. In relational databases, joins are common and usually handled by the database engine. In MapReduce, joins require more planning because data may be distributed across many machines.

There are several ways to perform joins in a MapReduce context.

#### Sort-Merge Join

A sort-merge join, also called a reduce-side join, sends both datasets through mappers keyed by the join field. The shuffle phase groups matching records together, and the reducer merges records with the same key.

```text id="phfyxq"
Sort-Merge Join Conceptual View

  Dataset A          Dataset B
  Mapped by Key      Mapped by Key
         \                 / 
          \               /
           \    Shuffle  /
            \           /
             \         /
        Reduce: Merge on Key
                 |
               Output
```

Example customer dataset:

```json id="oivvyy"
[
  {
    "customerId": 1,
    "name": "Alice"
  },
  {
    "customerId": 2,
    "name": "Bob"
  }
]
```

Example order dataset:

```json id="22ry5m"
[
  {
    "orderId": "order-1",
    "customerId": 1,
    "amount": 100
  },
  {
    "orderId": "order-2",
    "customerId": 2,
    "amount": 50
  }
]
```

Mapper output:

```text id="bgihkd"
(1, customer: Alice)
(2, customer: Bob)
(1, order: order-1, amount: 100)
(2, order: order-2, amount: 50)
```

Reducer output:

```json id="io1j6d"
[
  {
    "customerId": 1,
    "name": "Alice",
    "orderId": "order-1",
    "amount": 100
  },
  {
    "customerId": 2,
    "name": "Bob",
    "orderId": "order-2",
    "amount": 50
  }
]
```

Sort-merge joins work with large datasets, but they require a shuffle, which can be expensive.

#### Broadcast Hash Join

A broadcast hash join is useful when one dataset is small enough to fit in memory on each mapper. The small dataset is copied to every mapper, and the mapper joins it with the larger dataset locally.

Example:

```text id="kvape2"
Small dataset: product categories
Large dataset: sales events
Each mapper loads product categories into memory
Each mapper joins sales events with category data
```

Example small lookup table:

```json id="grcjk5"
{
  "p1": "Electronics",
  "p2": "Books"
}
```

Example sales event:

```json id="iszqh0"
{
  "orderId": "order-9",
  "productId": "p1",
  "amount": 250
}
```

Example joined output:

```json id="5l1e0v"
{
  "orderId": "order-9",
  "productId": "p1",
  "category": "Electronics",
  "amount": 250
}
```

Broadcast hash joins avoid expensive shuffling of the large dataset, but they only work when the smaller dataset fits comfortably in memory.

#### Partitioned Hash Join

A partitioned hash join is used when both datasets are too large for one side to be broadcast. Both datasets are partitioned by the same join key so matching records end up in the same partition.

Example flow:

```text id="5vr5o4"
Partition customers by customerId
Partition orders by customerId
Process matching partitions together
Join records with the same customerId
```

Example output:

```json id="mye2jm"
{
  "joinType": "partitioned_hash_join",
  "partitionKey": "customerId",
  "status": "matching keys processed together"
}
```

This strategy reduces memory pressure but requires careful partitioning to avoid skew. If one key has too many records, one partition may become much larger than the others.

### When to Use Batch Processing

Batch processing is a good fit when immediate results are not required and the workload can be processed periodically. It is especially useful when the job needs to scan a large amount of data.

Common use cases include:

1. **Data Analytics** Periodically aggregate large volumes of data for dashboards, reports, or business intelligence.
2. **Search Index Building** Rebuild or refresh search indexes nightly or weekly.
3. **Machine Learning Pipelines** Transform large training datasets, generate features, and train models.
4. **ETL Workflows** Load, clean, enrich, and restructure data in bulk.
5. **Billing and Reconciliation** Calculate invoices, settlement files, and financial summaries on a scheduled basis.

Example nightly analytics job:

```json id="i2a51j"
{
  "job": "daily_active_users",
  "schedule": "nightly",
  "input": "user_events",
  "output": "analytics.daily_user_metrics"
}
```

Example output:

```json id="fzid8w"
{
  "date": "2024-01-12",
  "dailyActiveUsers": 48213,
  "newUsers": 1320,
  "returningUsers": 46893
}
```

Batch processing is not ideal when the system must react immediately. For fraud blocking, live monitoring, or real-time personalization, stream processing may be better.

### Alternatives to MapReduce

MapReduce was historically important for large-scale distributed processing, but newer frameworks offer different performance models, APIs, and developer experiences.

#### Apache Spark

Apache Spark is a distributed data processing engine that can run batch, streaming, SQL, and machine learning workloads. Compared with classic MapReduce, Spark can keep intermediate data in memory, which makes it faster for iterative workloads.

Spark is especially useful for workflows with multiple stages, repeated joins, interactive analytics, and machine learning algorithms that need to scan the same data several times.

Example Spark-style job:

```python id="qvbd6c"
sales_by_category = (
    sales_df
    .groupBy("category")
    .sum("amount")
)
```

Example output:

```json id="kr1dg3"
{
  "Electronics": 550,
  "Clothing": 130,
  "Books": 20
}
```

Spark can optimize execution plans and cache datasets in memory, reducing repeated disk reads for complex pipelines.

#### Pregel

Pregel is a graph processing model. Instead of thinking in terms of rows and tables, Pregel treats computation as work done by vertices in a graph. Each vertex processes messages, updates its state, and sends messages to neighboring vertices in iterative steps.

This model is useful for graph problems such as PageRank, shortest paths, social network analysis, fraud networks, recommendation systems, and connected components.

Example graph concept:

```json id="sfcy7x"
{
  "vertex": "user-1",
  "neighbors": ["user-2", "user-3"],
  "messagesReceived": ["score_update"]
}
```

Example output:

```json id="jueg7p"
{
  "vertex": "user-1",
  "updatedScore": 0.84,
  "messagesSentToNeighbors": 2
}
```

Pregel-style systems work well when relationships between entities are central to the computation.

#### Hive and Pig

Hive and Pig were created to make Hadoop and MapReduce easier to use.

**Hive** provides a SQL-like language called HiveQL. It allows analysts and engineers to query large datasets using familiar SQL syntax instead of writing low-level MapReduce jobs.

Example Hive query:

```sql id="ggrf03"
SELECT category, SUM(amount) AS total
FROM purchases
GROUP BY category;
```

Example output:

```text id="3v32r2"
Electronics  550
Clothing     130
Books        20
```

**Pig** provides a dataflow scripting language. It lets developers describe transformations step by step without writing raw MapReduce code.

Example Pig-style flow:

```text id="18srjz"
Load purchases
Group by category
Sum amount
Store result
```

Hive and Pig helped bridge the gap between raw distributed processing and more user-friendly data processing. Today, many teams use Spark SQL, Flink, dbt, cloud warehouses, or managed data processing tools for similar goals.
