## Types of Databases

In the majority of the systems we will be designing, there is a need to hold some sort of persistent data. It would make no sense to hold application data in server memory, as not only would it be lost if the server crashed, but having many servers means that they would be out of sync if only one server stored certain information. The solution to this is to store any persistent data in one or more databases. I will now go into the types of databases, and the pros and cons of using each type.

### Relational databases (SQL databases)

* Consist of tables holding many rows of structured data.
* Rows of one table can have a relation to rows of another table if both rows share a common key.
* Has a built-in query optimizer that uses the quickest implementation for a SQL statement (declarative language).
* Good for handling structured and transactional data.
* SQL databases are well-established and have a long history, meaning that there are many mature tools and libraries for interacting with them.
* They are good for complex queries and data integrity, but not very performant when dealing with large amount of unstructured data.

### Non-Relational databases (NoSQL databases)

* Instead of rows, a table holds a collection of keys mapped to values, which do not need to have any particular structure.
* Good for handling unstructured and semi-structured data.
* NoSQL databases are designed to handle large amounts of data and high levels of concurrency, which makes them a good choice for big data and real-time applications.
* They are more flexible in terms of data model, which means that adding new fields or changing the structure of the data does not require a complicated migration.
* They can also be horizontally scaled, which makes them more suitable for cloud and distributed environments.
* They are not good for complex joins and transactions, but they can be good for simple queries and high data availability.

### Graph databases (NoSQL)

* Has vertices and edges, queries involve traversing the graph.
* Good for storing both homogenous and heterogeneous data (with multiple types of edges).
* They are good for handling data with complex relationships, such as social networks, recommendation systems, and routing algorithms.
* They are good for traversing large datasets and discovering patterns in the data.
* They are not good for handling high write loads and large amounts of unstructured data.

In conclusion, the choice of database type will depend on the specific use case and requirements of the application. Relational databases are a good choice for structured and transactional data, while NoSQL databases are better suited for unstructured and semi-structured data, and graph databases are best for data with complex relationships. It is important
