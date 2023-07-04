## Analyzing Data with Data Warehouses

Data Warehousing is a helpful way to process and calculate data from the past. Instead of using the main database, data is taken from transaction databases, changed, and put into a data warehouse optimized for reading the entire dataset.

### Star and Snowflake Schemas
Analytics tables are usually structured with star and snowflake schemas:
- A central **fact table** for important events, like grocery store sales.
- The fact table has multiple **foreign keys** linked to rows in many **dimension tables**, like product or customer tables.
- The snowflake schema builds on the star schema, with each dimension table having **sub-dimension tables**.

### Column-Oriented Storage
Data warehouses use **column-oriented storage** to speed up analytics:
- Regular approach: Most non-analytical databases use **row-oriented storage** because we often want to access all values in a row. This means rows are stored close together.
- Column-oriented storage: Stores each column's values together, keeping the order of the values the same as in the table rows. This improves value reading speed.
- Compression: Storing all column values can be compressed to save space. Bitmap encoding can save space if there are fewer distinct values in a column compared to the number of rows. Bitmap encoding can be further compressed to **run-length encoding** by showing how many 0s and 1s repeat and combining these numbers.

### Sorting and Materialized Views
Sorting all columns in the same order can speed up queries and compress columns even more. Data warehouse replicas can be sorted in different ways to speed up certain queries.

**Materialized views** are a database optimization that precomputes common queries to cache the result. This avoids recalculating all the time. The downside is that writes take longer, and there's less flexibility than querying raw data. A special materialized view is the **data cube**, which groups aggregates by two different dimensions, like date and product number, to find total sales for each combination.

Writing to column-oriented storage is tricky if you want to write in the middle of a sorted list, but **LSM-trees** allow efficient writing and rewriting of column segments to make changes.
