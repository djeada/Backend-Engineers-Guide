## Batch Processing

Batch processing is a method for handling large volumes of data by grouping them into a single **batch**, typically without immediate user interaction. It is often **useful** in scenarios where tasks can be processed independently and do not require real-time results, such as nightly analytics jobs, building machine learning models, or transforming data for further analysis. A well-known paradigm in this domain is **MapReduce**, which operates across distributed clusters to handle massive datasets in parallel.

```
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
                          (Accumulation Over Time)
```

- Collecting data over time allows the system to gather information gradually and then process it all at once.
- A dedicated data storage layer temporarily holds raw inputs until the system is ready to process them in bulk.
- Batch processing systems are set up to handle many tasks either one after the other or in parallel, making them suitable for large datasets.
- The final outputs from batch processing are used for generating reports, analytics, or as input for additional data workflows.

### MapReduce

MapReduce is a two-phase process (Map and Reduce) that breaks down a dataset into smaller tasks, distributing them across multiple nodes. It automates data distribution, task coordination, and failure handling, making it **valuable** for large-scale batch processing.

```
MapReduce Flow

                   +-----------------+
                   |    Input Data   |
                   +-----------------+
                           |
                           v
+-------------------------+-------------------------+
|    Split into Chunks / Distribute to Mappers     |
+-------------------------+-------------------------+
          |                                 |
          v                                 v
+---------------------+             +---------------------+
|  Map Function       |             |  Map Function       |
|  (Process Chunks)   |             |  (Process Chunks)   |
+---------+-----------+             +---------+-----------+
          |                                   |
          v                                   v
+---------------------+             +---------------------+
|  Intermediate Data  |             |  Intermediate Data  |
|  (Key-Value Pairs)  |             |  (Key-Value Pairs)  |
+---------+-----------+             +---------+-----------+
          |                                   |
          v                                   v
+---------------------+             +---------------------+
|     Shuffle &       |             |     Shuffle &       |
|     Sort Phase      |             |     Sort Phase      |
|   (Group by Key)    |             |   (Group by Key)    |
+---------+-----------+             +---------+-----------+
          |                                   |
          v                                   v
+---------------------+             +---------------------+
| Reduce Function     |             | Reduce Function     |
| (Aggregate Results) |             | (Aggregate Results) |
+---------+-----------+             +---------+-----------+
          |                                   |
          +----------------+------------------+
                           |
                           v
                   +-----------------+
                   |  Final Output   |
                   | (Combined Data) |
                   +-----------------+
```

- The map stage divides a large dataset into many smaller pieces and processes these pieces in parallel, making it easier to handle and analyze massive amounts of data.
- The shuffle and sort phase gathers all the intermediate data produced by the map stage and groups together items that share the same key, which helps organize the data for the next step.
- The reduce phase takes each group of similar items and combines them to generate the final output, such as summing numbers or merging records.
- MapReduce is built to handle failures by automatically restarting any tasks on different nodes if a mapper or reducer fails, ensuring the overall process continues smoothly.

#### Example Dataset

| Customer  | Category    | Amount |
|-----------|-------------|--------|
| Customer A | Electronics | 250    |
| Customer B | Clothing    | 50     |
| Customer C | Electronics | 300    |
| Customer D | Books       | 20     |
| Customer E | Clothing    | 80     |

**Step 1: Map Phase**

In the **Map Phase**, each record is processed to output a key-value pair where the key is the product category and the value is the purchase amount. For example, the mapping function (in pseudo-code) could look like this:

```
map(record):
    key = record.Category
    value = record.Amount
    emit(key, value)
```

For our dataset, the mapper will produce:

- (`Electronics`, 250)
- (`Clothing`, 50)
- (`Electronics`, 300)
- (`Books`, 20)
- (`Clothing`, 80)

**Step 2: Shuffle and Sort Phase**

After mapping, the MapReduce framework automatically shuffles and sorts the key-value pairs so that pairs with the same key are grouped together. The grouping results in:

```
Electronics: [250, 300]
Clothing: [50, 80]
Books: [20]
```

**Step 3: Reduce Phase**

In the **Reduce Phase**, the reducer takes each key and its list of values to perform an aggregation operation (in this example, summing the amounts). The pseudo-code for the reducer might be:

```
reduce(key, values):
    total = 0
    for value in values:
        total += value
    emit(key, total)
```

Applying this:

- For `Electronics`: 250 + 300 = 550
- For `Clothing`: 50 + 80 = 130
- For `Books`: 20

**Final Output**

The final output is a set of key-result pairs:

```
Electronics -> 550
Clothing -> 130
Books -> 20
```

This step-by-step example demonstrates how MapReduce can efficiently process and summarize data by breaking the task into mapping, shuffling, and reducing steps.

### Joins in MapReduce

Performing joins combines data from different sources or tables. There are multiple **ways** to execute joins in a MapReduce context:

- A **sort-merge** join (reduce-side join) sends both datasets through mappers keyed by the join field, then merges them in the reducer.  
- A **broadcast hash** join (map-side join) is **helpful** when one dataset is small enough to fit in memory on each mapper.  
- A **partitioned hash** join (map-side join) is **appropriate** when both datasets need partitioning by the same key to avoid memory issues.

```
Sort-Merge Join (Conceptual)

  Dataset A          Dataset B
  (Mapped by Key)    (Mapped by Key)
         \                 / 
          \               /
           \    Shuffle  /
            \          /
             \        /
        (Reduce: Merge on Key)
                 |
               Output
```

- Each mapper is **configured** to emit (key, value) pairs, where key is the join column.  
- The reducer then **collects** all pairs with the same key and merges them accordingly.  

### When to Use Batch Processing

- Data analytics tasks can be **handled** effectively by periodically aggregating large volumes of data.  
- Building search indexes is **practical** by refreshing them nightly or weekly in a batch job.  
- Machine learning pipelines often **require** large batch transformations before model training.  
- ETL workflows can be **simplified** by loading, cleansing, and restructuring data in bulk.  

### Alternatives to MapReduce

Although MapReduce has been **popular** for massive-scale processing, newer frameworks and models offer different trade-offs:

**Apache Spark**

- Apache Spark uses in-memory computing to store intermediate results, which significantly speeds up computations that involve multiple iterations over the same data; for example, iterative machine learning algorithms benefit from not having to repeatedly read from disk.  
- Apache Spark also optimizes execution plans at runtime and can cache datasets in memory, reducing the overall processing time for complex workflows that involve several stages.  

**Pregel**

- The Pregel model takes a vertex-centric approach to graph processing, where each vertex independently processes its data and communicates with its neighbors in iterative steps; this design is well suited for applications like social network analysis.  
- In recommendation engines, the Pregel model helps update relationships between nodes efficiently by allowing each vertex to process messages concurrently, making it easier to compute complex interactions among a large number of users and items.  

**Hive and Pig**

- Hive offers a SQL-like query language that lets users interact with large datasets stored in Hadoop using familiar commands, which simplifies the process of extracting meaningful insights from the data.  
- Pig provides a dataflow scripting language that abstracts the complexities of writing low-level MapReduce programs, enabling developers to create and manage data pipelines with more readable and maintainable scripts.  
- Both Hive and Pig are designed to bridge the gap between raw MapReduce operations and user-friendly data processing, making it easier for analysts and developers to work with large-scale data without needing deep knowledge of the underlying execution details.
