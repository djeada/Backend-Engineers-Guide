
## Transaction Analytics and Data Warehousing

Data Warehousing is an effective method to perform retroactive processing on data and calculations. Instead of querying the main database, which could potentially put too much load on it, data is extracted from the transaction databases, transformed, and loaded into the data warehouse which is optimized for reads across the entire dataset.

### Stars and Snowflakes Schema
The data in an analytics table is typically structured using the stars and snowflakes schema:
- A centralized **fact table** for important events, such as each sale in a grocery store.
- The fact table has multiple **foreign keys** to rows of many other **dimension tables**, such as a product table or a customer table.
- The snowflakes schema builds on the aforementioned star schema, where each dimension table has **sub-dimension tables**.

### Column Oriented Storage
In order to optimize for analytical speed, data warehouses typically use **column oriented storage**:
- Traditional approach: Most non-analytical (transactional) databases use **row oriented storage**, as we typically want to access all of the values in a row. This means that there is locality in the storage of a row. 
- Column oriented storage: Stores each value from the column together, and keeps the order of the values in the column the same as what the rows would be in the table. This increases the locality of these values, allowing them to be read much faster.
- Compression: Storing all of the column values can be easily compressed in order to reduce the amount of space that the data takes up. Bitmap encoding can be used to reduce the amount of space needed if the number of distinct values in a column is small compared to the number of rows. The bitmap encoding can then be further compressed to a **run length encoding** by saying how many 0s and 1s are repeated and combining these numbers.

### Sorting and Materialized Views
Sometimes it makes sense to **sort all of the columns** in the same order to help speed up queries, in addition to help compress columns even further. Replicas of the data warehouse can also be sorted in multiple different ways to make certain queries faster. 

**Materialized views** is an optimization by the database to precompute common queries in order to cache the result. This way it does not have to be recalculated all the time. The downside of this is that on writes, materialized views must be updated, so writes take longer, and it offers less flexibility than querying raw data. A special type of materialized view is the **data cube**, which groups aggregates by two different dimensions, such as date and product number to find the total sales for each combination.

Writing to column oriented storage is hard if you want to write in the middle of a sorted list, but **LSM-trees** allow doing this efficiently and then rewriting the column segments to propagate the changes.
