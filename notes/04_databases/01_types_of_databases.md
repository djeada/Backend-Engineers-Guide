## Types of Databases

Databases store persistent data and prevent issues like data loss or server sync problems.

### Relational Databases (SQL)

- Use tables with rows of structured data. Each table represents an entity, and rows represent records.
- Rows in different tables can be related through common keys (foreign keys), enabling complex relationships.
- Built-in query optimizer for SQL (Structured Query Language) statements, which is a declarative language.
- Good for structured and transactional data such as financial systems, customer databases, and inventory management.
- Mature tools and libraries available, including extensive support from database management systems (DBMS) like MySQL, PostgreSQL, Oracle, and Microsoft SQL Server.
- Good for complex queries, data integrity (ACID compliance), and ensuring data consistency.
- Less performant for large unstructured data, and scalability can be challenging due to the rigid schema.

### Non-Relational Databases (NoSQL)

- Use collections of key-value pairs, documents, wide-column stores, or graphs with flexible structure.
- Good for unstructured and semi-structured data, such as JSON, XML, or multimedia files.
- Handle large data amounts and high concurrency levels, often with eventual consistency.
- Flexible data models allow easier migrations and schema updates.
- Horizontally scalable, making them suitable for cloud and distributed environments.
- Good for simple queries, high data availability, and applications requiring quick read and write operations, such as social media platforms, real-time analytics, and IoT.
- Designed for distributed data, high performance, and fault tolerance.
- Not ideal for complex joins and transactions, and may lack strong consistency guarantees.

### Graph Databases (NoSQL)

- Store data as vertices (nodes) and edges (relationships) in a graph.
- Good for both homogenous and heterogeneous data, where relationships are as important as the data itself.
- Ideal for complex relationships, such as social networks, recommendation systems, fraud detection, and routing algorithms.
- Good for traversing large datasets, discovering patterns, and executing recursive queries efficiently.
- Often designed for read-heavy operations and can scale horizontally for distributed querying.
- Efficient for graph traversals and operations that involve deep linking and relationship exploration.
- Not suitable for high write loads and large unstructured data. May require specialized query languages like Cypher (used in Neo4j).
