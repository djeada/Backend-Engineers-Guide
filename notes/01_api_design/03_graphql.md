## GraphQL  
GraphQL is a query language for APIs that allows clients to request exactly the data they need in a single request. It provides a type system to describe data and offers a more efficient, flexible, and powerful alternative to traditional REST-based architectures. These notes explore the fundamentals of GraphQL, including its anatomy, how it processes queries, common best practices, and example commands illustrating how to interact with a GraphQL server. ASCII diagrams and code blocks provide additional clarity.

### What is GraphQL?  
GraphQL is a specification and set of tools that enable clients to define the structure of the data required and receive precisely that data from a server. It was initially developed by Facebook to improve the efficiency and flexibility of data fetching in mobile apps, but it has since been widely adopted in various contexts.

The  diagram below offers a conceptual view of how a GraphQL client communicates with a GraphQL server, which in turn interacts with one or more data sources (databases, microservices, etc.):

```
+------------------------+                  +-------------------------+
|                        |                  |                         |
|    GraphQL Client      |                  |    GraphQL Server       |
| (Web, Mobile, etc.)    |                  | with Schema & Resolvers |
+------------------------+                  +-----------+-------------+
         | 1. Sends Query or Mutation                  |
         |-------------------------------------------->|
         |                     2. Receives Query       |
         |                        Parses & Validates   |
         |                        Resolves Fields      |
         |                        Fetches Data         |
         |                        from Data Sources    |
         |                     3. Gathers Results      |
         |<--------------------------------------------|
         | 4. Receives Response (Precisely the data needed)
         |
+------------------------+                   
|                        |                   
|  Renders or Processes  |                   
|  the Returned Data     |                   
|                        |                   
+------------------------+                   
```

The client sends a query or mutation describing the shape of the data it wants, the server resolves that request by retrieving information from data sources, and it sends back exactly what was requested.

### Concepts of GraphQL

GraphQL is a query language and runtime for APIs that gives clients more control over the data they receive. Unlike REST, where each endpoint usually returns a fixed response shape, GraphQL allows the client to request exactly the fields it needs. This can reduce over-fetching, where the server returns unnecessary data, and under-fetching, where the client has to make multiple requests to collect related data.

GraphQL centers around three main concepts: the **schema**, the **query language**, and **resolvers**. The schema defines the structure of the API, including the available data types, fields, and relationships. The query language allows clients to ask for specific data in a clear and nested format. Resolvers are the server-side functions that fetch or compute the actual data requested by the client.

Together, these concepts make GraphQL flexible and strongly typed. Clients can explore the schema to understand what data is available, while servers can enforce clear rules about what can be requested and how data should be returned.

#### Schema Definition Language (SDL)

Schemas in GraphQL are described using a human-readable syntax called the **Schema Definition Language**, or SDL. The schema acts like a contract between the client and the server. It explains what types of data exist, which fields each type contains, how types relate to each other, and which operations clients are allowed to perform.

For example, a book application might include `Book` and `Author` types. A book has an ID, a title, and an author. An author has an ID, a name, and a list of books. These relationships are defined directly in the schema.

```graphql
type Book {
  id: ID!
  title: String!
  author: Author!
}

type Author {
  id: ID!
  name: String!
  books: [Book!]!
}

type Query {
  book(id: ID!): Book
  books: [Book!]!
  author(id: ID!): Author
}

type Mutation {
  addBook(title: String!, authorId: ID!): Book!
}
```

Example query:

```graphql
query {
  book(id: "1") {
    id
    title
    author {
      name
    }
  }
}
```

Example output:

```json
{
  "data": {
    "book": {
      "id": "1",
      "title": "GraphQL Basics",
      "author": {
        "name": "Jane Smith"
      }
    }
  }
}
```

This example schema defines a `Book` type with an `id`, `title`, and `author`. It also defines a `Query` type for retrieving books or authors, and a `Mutation` type for adding new books. The exclamation mark, such as in `ID!` or `String!`, means the field is required and cannot return `null`.

The example query asks for a single book with the ID `"1"`. Instead of returning every possible field on the book, the server returns only the requested fields: `id`, `title`, and the author’s `name`. This shows one of GraphQL’s main benefits: clients can shape the response to match their exact needs.

#### Queries, Mutations, and Subscriptions

GraphQL offers three primary operation types: **queries**, **mutations**, and **subscriptions**. Each operation has a different purpose, but all use GraphQL’s field-based syntax to describe what data should be returned.

A **query** is used for reading data. It is comparable to a `GET` request in REST because it retrieves information without changing it. Queries are commonly used to load pages, show user profiles, display product lists, or fetch related records.

Example query:

```graphql
query {
  books {
    id
    title
    author {
      name
    }
  }
}
```

Example output:

```json
{
  "data": {
    "books": [
      {
        "id": "1",
        "title": "GraphQL Basics",
        "author": {
          "name": "Jane Smith"
        }
      },
      {
        "id": "2",
        "title": "API Design Patterns",
        "author": {
          "name": "Alex Johnson"
        }
      }
    ]
  }
}
```

This query requests a list of books. For each book, the client asks for the book’s `id`, `title`, and the author’s `name`. The response follows the same shape as the query, which makes GraphQL responses predictable and easy to work with.

A **mutation** is used for creating, updating, or deleting data. It is comparable to REST operations like `POST`, `PUT`, `PATCH`, or `DELETE`. Mutations are used when the client wants to make a change on the server.

Example mutation:

```graphql
mutation {
  addBook(title: "Learning GraphQL", authorId: "1") {
    id
    title
    author {
      name
    }
  }
}
```

Example output:

```json
{
  "data": {
    "addBook": {
      "id": "3",
      "title": "Learning GraphQL",
      "author": {
        "name": "Jane Smith"
      }
    }
  }
}
```

In this example, the client creates a new book by calling the `addBook` mutation. The mutation accepts arguments such as `title` and `authorId`, then returns the newly created book. Just like with queries, the client controls which fields are returned after the operation.

A **subscription** is used for real-time updates. Subscriptions allow clients to stay connected to the server and receive new data when an event happens. They are commonly used for chat apps, notifications, live dashboards, stock prices, or collaborative tools.

Example subscription:

```graphql
subscription {
  bookAdded {
    id
    title
    author {
      name
    }
  }
}
```

Example output:

```json
{
  "data": {
    "bookAdded": {
      "id": "4",
      "title": "Real-Time GraphQL",
      "author": {
        "name": "Mia Chen"
      }
    }
  }
}
```

In this example, the client subscribes to the `bookAdded` event. Whenever a new book is added, the server can push an update to the client. This is different from normal queries, where the client must send a request each time it wants fresh data.

#### Resolvers

Resolvers are functions that connect GraphQL operations to actual backend data. When a client sends a query, GraphQL looks at each requested field and calls the appropriate resolver to produce the value for that field. Resolvers may fetch data from a database, call another API, check permissions, transform data, or compute a value.

A resolver for `Query.book` might look like this in JavaScript:

```js
const resolvers = {
  Query: {
    book: (parent, args, context, info) => {
      // parent is the result of the previous resolver in the chain
      // args contains the arguments passed in the query
      // context might hold things like database connections or user info
      // info provides query execution details
      return context.db.getBookById(args.id);
    },
    books: (parent, args, context) => {
      return context.db.getAllBooks();
    }
  },
  Mutation: {
    addBook: (parent, args, context) => {
      return context.db.createBook(args.title, args.authorId);
    }
  },
  Book: {
    author: (parent, args, context) => {
      return context.db.getAuthorById(parent.authorId);
    }
  }
};
```

Example query handled by these resolvers:

```graphql
query {
  book(id: "1") {
    id
    title
    author {
      id
      name
    }
  }
}
```

Example output:

```json
{
  "data": {
    "book": {
      "id": "1",
      "title": "GraphQL Basics",
      "author": {
        "id": "10",
        "name": "Jane Smith"
      }
    }
  }
}
```

In this example, the `Query.book` resolver receives the argument `id: "1"` and uses it to fetch the matching book from the database. Then, because the query also asks for the book’s author, the `Book.author` resolver runs and uses the book’s `authorId` to retrieve the related author.

Resolvers can also include logic for caching, authorization, validation, and data transformation. For example, a resolver might check whether the user is logged in before returning private data, or it might format a date before sending it back to the client. This makes resolvers one of the most important parts of a GraphQL server because they control how requested fields are actually resolved.

### GraphQL vs REST

GraphQL and REST both help clients communicate with servers, but they organize that communication in different ways. REST usually exposes multiple endpoints, where each endpoint represents a resource such as `/posts`, `/users`, or `/comments`. GraphQL, on the other hand, usually exposes a single endpoint where clients send queries that describe exactly what data they want.

The biggest difference is how much control the client has over the response. In REST, the server decides the shape of each endpoint’s response. This can be useful because it keeps endpoints predictable, but it can also lead to responses that include too much or too little data. In GraphQL, the client defines the response shape by selecting specific fields in the query.

GraphQL and REST address similar problems but approach them differently:

* GraphQL focuses on **asking for exactly what is needed** in one request.
* REST typically relies on **multiple endpoints** that may return more data than required or less than required, forcing the client to make further requests or filter the responses.

A performance advantage of GraphQL is that it can reduce **over-fetching** and **under-fetching**. Over-fetching happens when an API returns fields the client does not need. Under-fetching happens when the client has to make several requests to different endpoints to gather all the required data.

Example REST requests:

```bash
curl "http://example.com/books/1"
curl "http://example.com/books/1/author"
curl "http://example.com/books/1/reviews"
```

Example REST output:

```json
{
  "book": {
    "id": "1",
    "title": "GraphQL Basics",
    "description": "A beginner-friendly introduction to GraphQL.",
    "publishedYear": 2025,
    "isbn": "978-1234567890"
  },
  "author": {
    "id": "10",
    "name": "Jane Smith",
    "bio": "Jane writes about APIs and backend systems."
  },
  "reviews": [
    {
      "id": "100",
      "rating": 5,
      "comment": "Clear and practical."
    }
  ]
}
```

In a REST API, the client may need to call multiple endpoints to collect the book, author, and review data. Some of the returned fields, such as `description`, `publishedYear`, `isbn`, or `bio`, may not be needed by the client.

Example GraphQL query:

```graphql
query {
  book(id: "1") {
    title
    author {
      name
    }
    reviews {
      rating
    }
  }
}
```

Example GraphQL output:

```json
{
  "data": {
    "book": {
      "title": "GraphQL Basics",
      "author": {
        "name": "Jane Smith"
      },
      "reviews": [
        {
          "rating": 5
        }
      ]
    }
  }
}
```

In the GraphQL version, the client asks only for the book title, author name, and review ratings. The response follows the same structure as the query, so the client receives only the fields it requested.

### Query Execution and Performance

GraphQL can improve performance in network-limited scenarios because it can reduce the number of round trips between the client and server. Instead of sending several separate REST requests, a client can often send one GraphQL query that collects related data in a single response.

A simple way to describe this is to compare the total time needed for multiple REST requests with the time needed for one GraphQL request. If a REST client must call `N` endpoints to build a screen, the total REST time may include the cost of each request plus network latency between them.

A simplified comparison might look like this:

```text
T_rest = request_1 + request_2 + request_3 + ... + request_N

T_graph = one GraphQL request
```

If:

```text
T_graph < T_rest
```

then GraphQL may provide a faster experience for the client, especially when network latency is high or when the client needs deeply related data.

Example REST flow:

```bash
curl "http://example.com/users/1"
curl "http://example.com/users/1/posts"
curl "http://example.com/posts/5/comments"
```

Example REST output:

```json
{
  "user": {
    "id": "1",
    "name": "Jane Smith"
  },
  "posts": [
    {
      "id": "5",
      "title": "Understanding GraphQL"
    }
  ],
  "comments": [
    {
      "id": "90",
      "text": "Very helpful explanation."
    }
  ]
}
```

This REST flow requires multiple requests: one for the user, one for the user’s posts, and one for the comments on a post. If these requests depend on each other, the client may need to wait for one response before sending the next request.

Example GraphQL query:

```graphql
query {
  user(id: "1") {
    id
    name
    posts {
      id
      title
      comments {
        id
        text
      }
    }
  }
}
```

Example GraphQL output:

```json
{
  "data": {
    "user": {
      "id": "1",
      "name": "Jane Smith",
      "posts": [
        {
          "id": "5",
          "title": "Understanding GraphQL",
          "comments": [
            {
              "id": "90",
              "text": "Very helpful explanation."
            }
          ]
        }
      ]
    }
  }
}
```

This GraphQL query retrieves the user, the user’s posts, and each post’s comments in one request. However, GraphQL is not automatically faster in every situation. A poorly designed GraphQL query can be expensive if it requests too much nested data or triggers too many database lookups. Performance depends on schema design, resolver efficiency, caching, batching, and query limits.

### Best Practices for GraphQL

Designing a GraphQL API requires more than just defining types and resolvers. Because GraphQL gives clients a lot of flexibility, API designers need to add structure, performance protections, and security controls. Good GraphQL design helps clients request useful data while preventing slow, expensive, or unsafe queries.

There are several considerations for designing and deploying a GraphQL API:

* Use **schema stitching or federation** for large projects where multiple teams own different parts of the data.
* Implement **caching** at various layers, such as the resolver level or with data loader patterns, to reduce repetitive database lookups.
* Keep queries **small and focused** when possible, but maintain the flexibility that GraphQL offers.
* Employ **schema versioning** or deprecation strategies to allow clients to adapt over time.
* Pay attention to **security**, especially when exposing GraphiQL or Playground in production environments.

Example schema deprecation:

```graphql
type Book {
  id: ID!
  title: String!
  summary: String
  description: String @deprecated(reason: "Use summary instead.")
}
```

Example query:

```graphql
query {
  book(id: "1") {
    id
    title
    summary
  }
}
```

Example output:

```json
{
  "data": {
    "book": {
      "id": "1",
      "title": "GraphQL Basics",
      "summary": "A beginner-friendly guide to GraphQL concepts."
    }
  }
}
```

In this example, the schema keeps the older `description` field available but marks it as deprecated. This gives existing clients time to move to the newer `summary` field without breaking immediately.

For larger systems, federation can help split one GraphQL API into smaller parts owned by different teams. For example, one team might own user data, another team might own books, and another might own reviews. Federation allows these separate pieces to work together as one graph while still letting teams manage their own areas independently.

Security is also important. Since GraphQL clients can create deeply nested queries, servers should consider protections such as query depth limits, complexity limits, authentication checks, authorization checks, and disabling public development tools in production unless they are properly protected.


### The N+1 Problem and DataLoader

A common challenge with GraphQL is the **N+1 query problem**. This happens when the server first fetches a list of items and then runs a separate query for a related field on each item. The result is one query for the list, plus one extra query for each item in that list.

For example, imagine a client asks for 50 books and the author of each book. The server might first run one query to fetch the books. Then, for each book, it might run another query to fetch that book’s author. That creates 51 total queries: one query for the books and 50 separate author queries.

Without batching, the resolver might behave like this:

```js
const resolvers = {
  Book: {
    author: async (parent, args, context) => {
      return context.db.getAuthorById(parent.authorId);
    }
  }
};
```

Example query:

```graphql
query {
  books {
    id
    title
    author {
      id
      name
    }
  }
}
```

Example output:

```json
{
  "data": {
    "books": [
      {
        "id": "1",
        "title": "GraphQL Basics",
        "author": {
          "id": "10",
          "name": "Jane Smith"
        }
      },
      {
        "id": "2",
        "title": "API Design Patterns",
        "author": {
          "id": "11",
          "name": "Alex Johnson"
        }
      }
    ]
  }
}
```

The output looks correct, but the server may have done unnecessary work behind the scenes. If there are many books, calling the database once per author can become slow and inefficient.

DataLoader helps solve this problem by batching and caching lookups during a single request cycle. Instead of fetching each author one by one, DataLoader collects all requested author IDs and sends one batch query.

```js
const DataLoader = require('dataloader');

const authorLoader = new DataLoader(async (authorIds) => {
  // Single batch query instead of N individual queries
  const authors = await db.getAuthorsByIds(authorIds);
  return authorIds.map(id => authors.find(a => a.id === id));
});

const resolvers = {
  Book: {
    author: (parent) => authorLoader.load(parent.authorId)
  }
};
```

Example batched lookup:

```text
Requested author IDs: [10, 11, 12, 13]
Single database query: db.getAuthorsByIds([10, 11, 12, 13])
```

Example output:

```json
{
  "data": {
    "books": [
      {
        "id": "1",
        "title": "GraphQL Basics",
        "author": {
          "id": "10",
          "name": "Jane Smith"
        }
      },
      {
        "id": "2",
        "title": "API Design Patterns",
        "author": {
          "id": "11",
          "name": "Alex Johnson"
        }
      }
    ]
  }
}
```

Without DataLoader, fetching 50 books and their authors could trigger 51 queries: one query for the books and 50 queries for the authors. With DataLoader, it can become 2 queries: one query for the books and one batched query for all authors.

This improves performance without changing the GraphQL response shape. The client still receives the same clean nested data, but the server performs fewer database calls to produce it.

### Fragments

Fragments allow reusable sets of fields to be defined once and referenced in multiple queries. This helps reduce duplication and keeps GraphQL documents easier to maintain. Instead of repeating the same list of fields every time a client requests a `Book`, the shared fields can be placed into a fragment and reused wherever that same shape is needed.

Fragments are especially helpful in client applications where the same data appears in several parts of the user interface. For example, a book card, a featured book panel, and a recent books list might all need the book’s `id`, `title`, and author name. By using a fragment, the client can keep that shared field selection consistent across the application.

```graphql
fragment BookFields on Book {
  id
  title
  author {
    name
  }
}

query {
  recentBooks: books(limit: 5) {
    ...BookFields
  }
  featuredBook: book(id: "1") {
    ...BookFields
    description
  }
}
```

Example output:

```json
{
  "data": {
    "recentBooks": [
      {
        "id": "1",
        "title": "GraphQL Basics",
        "author": {
          "name": "Jane Smith"
        }
      },
      {
        "id": "2",
        "title": "API Design Patterns",
        "author": {
          "name": "Alex Johnson"
        }
      }
    ],
    "featuredBook": {
      "id": "1",
      "title": "GraphQL Basics",
      "author": {
        "name": "Jane Smith"
      },
      "description": "A beginner-friendly introduction to GraphQL concepts."
    }
  }
}
```

In this example, the `BookFields` fragment is reused in two places. The `recentBooks` field returns a list of books using the shared fields, while `featuredBook` uses the same fragment and also requests an extra `description` field. This keeps the query concise while still allowing each part of the query to request additional fields when needed.

### Error Handling

GraphQL handles errors differently from many REST APIs. Instead of relying only on HTTP status codes, GraphQL usually returns errors inside the response body. This allows the server to return both successful data and error details in the same response.

This is useful because GraphQL queries often request several fields at once. One field might fail while another field succeeds. In that case, the server can still return the successful parts of the response while also including an `errors` array that explains what went wrong.

A typical error response looks like this:

```json
{
  "data": {
    "book": null
  },
  "errors": [
    {
      "message": "Book not found",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["book"],
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

Example query that could produce this error:

```graphql
query {
  book(id: "999") {
    id
    title
  }
}
```

Example output:

```json
{
  "data": {
    "book": null
  },
  "errors": [
    {
      "message": "Book not found",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": ["book"],
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

In this example, the client requested a book with the ID `"999"`, but the server could not find it. The `data.book` value is `null`, and the `errors` array explains the problem. The `path` field shows which part of the query failed, while the `extensions.code` field provides a machine-readable error code that the client can use for conditional handling.

Because partial data can be returned alongside errors, clients should always check the `errors` array even when `data` is present. A response may not be a total failure just because it contains an error. The client needs to decide whether it can still use the partial data or whether it should show an error message to the user.

### Pagination Patterns

GraphQL APIs commonly use cursor-based pagination for large lists of data. This is often implemented using the Relay connection pattern, which organizes paginated results into `edges`, `nodes`, and `pageInfo`.

In this pattern, each item is wrapped in an `edge`. The actual resource, such as a book, appears inside the `node` field. The `cursor` field marks the item’s position in the list. The `pageInfo` object provides metadata about the current page, including whether more results are available and which cursor should be used to request the next page.

```graphql
query {
  books(first: 10, after: "cursor_abc") {
    edges {
      node {
        id
        title
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

Example output:

```json
{
  "data": {
    "books": {
      "edges": [
        {
          "node": {
            "id": "11",
            "title": "Advanced GraphQL Patterns"
          },
          "cursor": "cursor_011"
        },
        {
          "node": {
            "id": "12",
            "title": "Building APIs with GraphQL"
          },
          "cursor": "cursor_012"
        }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "cursor_012"
      }
    }
  }
}
```

In this example, the server returns a page of books after the cursor `"cursor_abc"`. Each returned book has its own cursor, and the `pageInfo.endCursor` value can be used to request the next page.

The `pageInfo.hasNextPage` value tells the client whether more results exist. If it is `true`, the client can send another query using the `endCursor` value as the next `after` argument. This approach scales well for large datasets and avoids the offset-drift problems found in offset-based pagination, where newly inserted or deleted records can cause items to shift between pages.

### Security Considerations

GraphQL gives clients a lot of flexibility, but that flexibility can also create security and performance risks. Because clients can request deeply nested data, a poorly controlled GraphQL API may allow expensive queries that overload the server or database.

For example, a client might send a query that asks for authors, each author’s books, each book’s reviews, and each review’s user. If that nesting continues too deeply, the server may need to perform a large amount of work for a single request. Security controls help prevent clients from accidentally or intentionally sending queries that are too expensive.

Several techniques help mitigate abuse:

* **Query depth limiting** rejects queries that nest beyond a configured depth, preventing deeply recursive requests.
* **Query complexity analysis** assigns a cost to each field and rejects queries whose total cost exceeds a threshold.
* **Persisted queries** require clients to send a query hash instead of the full query text, limiting what operations the server will execute.
* **Rate limiting** can be applied per client or per query complexity unit to cap resource usage.
* **Introspection controls** disable the schema introspection query in production to prevent attackers from discovering the full API surface.

Example query that may be too deeply nested:

```graphql
query {
  authors {
    books {
      reviews {
        user {
          reviews {
            book {
              author {
                books {
                  title
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Example error output:

```json
{
  "data": null,
  "errors": [
    {
      "message": "Query depth limit exceeded",
      "extensions": {
        "code": "QUERY_DEPTH_LIMIT_EXCEEDED",
        "maxDepth": 5
      }
    }
  ]
}
```

In this example, the server rejects the query because it is nested too deeply. Instead of trying to execute a potentially expensive operation, the server returns an error explaining that the query exceeded the allowed depth.

These protections are especially important for public APIs. A GraphQL server should validate not only whether a query is syntactically correct, but also whether it is safe and reasonable to execute. Authentication and authorization checks should also be applied inside resolvers so users can access only the data they are allowed to see.

### Introspection

GraphQL servers support introspection, which allows clients and tools to query the schema itself. Introspection makes it possible to discover available types, fields, arguments, and relationships directly from the API. This is one reason GraphQL works well with developer tools, documentation generators, and interactive query explorers.

During development, introspection is extremely useful. Tools such as GraphiQL, GraphQL Playground, and API documentation systems can use introspection to show developers what queries and mutations are available. This makes it easier to explore the API without manually reading separate documentation.

```graphql
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
        }
      }
    }
  }
}
```

Example output:

```json
{
  "data": {
    "__schema": {
      "types": [
        {
          "name": "Book",
          "fields": [
            {
              "name": "id",
              "type": {
                "name": "ID"
              }
            },
            {
              "name": "title",
              "type": {
                "name": "String"
              }
            },
            {
              "name": "author",
              "type": {
                "name": "Author"
              }
            }
          ]
        },
        {
          "name": "Author",
          "fields": [
            {
              "name": "id",
              "type": {
                "name": "ID"
              }
            },
            {
              "name": "name",
              "type": {
                "name": "String"
              }
            }
          ]
        }
      ]
    }
  }
}
```

This introspection query asks the server to return information about the schema’s types and fields. In the example output, the client can see that the API has a `Book` type with fields such as `id`, `title`, and `author`.

Introspection is valuable during development, but many teams restrict or disable it in production. The reason is that introspection can reveal the full API surface, including types and fields that an attacker could study. If introspection remains enabled in production, it should be protected with authentication, authorization, or other access controls.

### Working with GraphQL from the Client Side

Client applications usually communicate with a GraphQL server by sending an HTTP `POST` request to a GraphQL endpoint, such as `/graphql`. The request body is sent as JSON and commonly includes the GraphQL operation, any variable values, and sometimes the name of the operation to run.

This approach is different from REST, where the HTTP method and URL usually describe the action being performed. In GraphQL, most requests go to the same endpoint, and the operation inside the request body tells the server what data to read or modify.

The table below highlights a few common fields often included in the request:

| Field           | Description                                                    |
| --------------- | -------------------------------------------------------------- |
| `query`         | The GraphQL query or mutation string                           |
| `variables`     | A JSON object holding variable values for the query            |
| `operationName` | Identifies which named operation in the request should execute |

The `query` field contains the actual GraphQL operation. The `variables` field allows values to be passed separately from the query string, which makes requests easier to reuse and safer than directly inserting values into the query. The `operationName` field is useful when a request contains more than one named operation and the server needs to know which one to execute.

### Example Commands with curl

Below are some practical examples of how to interact with a GraphQL API using `curl`. Each example command is followed by an example response and a brief interpretation.

#### 1) Query Single Book

This example shows how to request one specific book by ID. The query is named `GetBook`, and the `$id` variable is used to pass the book ID into the request. Using variables keeps the query reusable because the same query can be used with different book IDs.

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "query": "query GetBook($id: ID!) { book(id: $id) { id title author { name } } }",
  "variables": {"id": "1"}
}' \
http://example.com/graphql
```

Example output:

```json
{
  "data": {
    "book": {
      "id": "1",
      "title": "GraphQL Handbook",
      "author": {
        "name": "Jane Doe"
      }
    }
  }
}
```

The server returned a JSON object with the requested book data, including the author’s name. The response follows the same general shape as the query. Since the query requested only `id`, `title`, and `author.name`, no other book fields are included.

#### 2) Query List of Books

This example requests a list of books from the server. The query asks only for each book’s `id` and `title`, so the response contains just those fields for each item in the list.

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "query": "query { books { id title } }"
}' \
http://example.com/graphql
```

Example output:

```json
{
  "data": {
    "books": [
      {
        "id": "1",
        "title": "GraphQL Handbook"
      },
      {
        "id": "2",
        "title": "Learning GraphQL"
      }
    ]
  }
}
```

The server responded with an array of books. Each book contains only the `id` and `title` fields because those were the only fields requested in the query. This demonstrates how GraphQL lets the client control the response shape and avoid unnecessary fields.

#### 3) Mutation: Add a Book

This example uses a mutation to create a new book. The client sends the book title and author ID as variables, and the server creates the new resource. After the mutation runs, the response returns the fields requested inside the `addBook` selection set.

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "query": "mutation AddBook($title: String!, $authorId: ID!) { addBook(title: $title, authorId: $authorId) { id title author { name } } }",
  "variables": {"title": "New Book", "authorId": "123"}
}' \
http://example.com/graphql
```

Example output:

```json
{
  "data": {
    "addBook": {
      "id": "3",
      "title": "New Book",
      "author": {
        "name": "Author Name"
      }
    }
  }
}
```

A new book was successfully created. The response includes the new book’s `id`, `title`, and associated author name because those fields were requested in the mutation. If the client needed more fields, such as `createdAt` or `description`, it could add them to the mutation response selection.

### Subscriptions Example

Subscriptions enable real-time data updates in GraphQL. Instead of sending a single request and receiving a single response, a client keeps an active connection open with the server. The server can then push new data to the client whenever a relevant event occurs.

Subscriptions are commonly used for chat messages, notifications, live dashboards, collaborative editing, or any feature where the client should update automatically when data changes. While `curl` is not typically used for real-time GraphQL subscriptions, the subscription syntax looks similar to a query.

```graphql
subscription {
  bookAdded {
    id
    title
    author {
      name
    }
  }
}
```

Example event output:

```json
{
  "data": {
    "bookAdded": {
      "id": "4",
      "title": "Real-Time GraphQL",
      "author": {
        "name": "Mia Chen"
      }
    }
  }
}
```

In this example, the client subscribes to the `bookAdded` event. When a new book is added, the server sends the new book data to the client automatically. The response includes only the fields requested in the subscription: `id`, `title`, and the author’s `name`.

Although subscriptions are part of GraphQL, they usually require a transport such as WebSockets or server-sent events rather than a simple one-time HTTP request. This is why normal `curl` examples are better suited for queries and mutations, while subscriptions are usually tested with GraphQL clients, browser tools, or application code.
