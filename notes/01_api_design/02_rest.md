## REST  
Representational State Transfer, often referred to as REST, is an architectural style used to design web services. It uses a stateless communication model between clients and servers, relies on standard HTTP methods, and focuses on simple but powerful conventions.

### REST (Representational State Transfer)  
REST emphasizes a uniform way for clients and servers to exchange representations of resources. The approach fosters decoupled systems that are easier to maintain, scale, and evolve over time.

The diagram below outlines how a client typically makes a request to a RESTful service, and how the server responds:

```
+---------------------+                   +----------------------+
|                     |                   |                      |
|    REST Client      |                   |    RESTful API       |
|  (Web, Mobile, etc.)|                   |    Server            |
+---------------------+                   +----------------------+
         ||                                        ||
         || 1. Client sends a HTTP                 ||
         ||    request (GET, POST,                 ||
         ||    PUT, DELETE)                        ||
         \/                                        \/
+---------------------+                   +-----------------------+
|                     |                   |                       |
|  Prepare HTTP       |                   |  Process HTTP Request |
|  Request with URL,  |-----------------> |  & Determine Response |
|  Headers, and Body  |                   |  (Fetch, Create,      |
|  (if applicable)    |                   |  Update, Delete Data) |
|                     |                   |                       |
+---------------------+                   +-----------------------+
                                               ||
                                               || 2. Server processes
                                               ||    the request and 
                                               \/    prepares a response
+----------------------+                 +----------------------+
|                      |                 |                      |
|  Receive & Process   |                 |  Send HTTP Response  |
|  HTTP Response       | <---------------|  with Status Code,   |
|  (Data, Status Code) |                 |  Headers, and Body   |
|                      |                 |  (if applicable)     |
+----------------------+                 +----------------------+
         ||                                        
         || 3. Client uses the                    
         ||    received data                       
         \/                                       
+----------------------+                   
|                      |                   
|  Display/Use Data    |                   
|  (Render, Trigger)   |                   
|                      |                   
+----------------------+                   
```

This flow shows how a request starts with the client, moves to the server, then returns with a response containing data and status information. The client then processes the response for display or further actions.

### Core Principles of REST  
REST is built upon certain guiding principles that shape how a client and server communicate. These principles ensure a scalable, reliable, and efficient system.

#### Client-Server Architecture  
A client-server model means the client handles presentation (for example, a web page or mobile app), while the server deals with data storage and manipulation. When the client and server are properly separated, each side can scale or change independently. This arrangement can be represented with a simple performance equation for total request latency:  

```
T_total = T_client + T_server
```

T_client accounts for client-side processing, and T_server measures server-side handling. Keeping these roles distinct prevents either side from unduly affecting the other’s performance.

#### Statelessness  
A stateless protocol means that every request contains all the information needed for the server to process it. The server does not store session data. One way to quantify server memory usage is:  

```
M_active = R_requests * (D_server / T_stateless)
```

R_requests is the request rate, D_server is the duration of server processing, and T_stateless is the time factor associated with not storing state. Statelessness helps keep M_active low and makes the system simpler to maintain.

#### Cacheable  
REST encourages caching of responses to reduce unnecessary calls and lower bandwidth usage. A simple formula for cache effectiveness is:  

```
L_final = L_initial * (1 - C_hitRate)
```

L_initial is the original load (requests per second), C_hitRate is the fraction of requests served from the cache, and L_final is the remaining load after caching. The ASCII diagram below illustrates basic caching:

```
   Client              Server
      |                   |
 GET  | --------------->  |  Resource
      |  <--------------- |  Representation
      |                   |
      |  Cache response   |
      |  for some time    |
      |                   |
      |  Use cached       |
 GET  |  response         |
      |  if allowed       |
      |                   |
```

#### Layered System  
Layering allows you to insert intermediaries (like proxies, firewalls, or load balancers) between the client and server without the client needing to know. Each layer interacts only with the layer directly before or after it. This modularity makes it easier to scale components, introduce caching servers, or handle security in separate layers.

#### Uniform Interface  
A uniform interface simplifies how clients interact with servers because the same conventions apply everywhere. Resources are identified by URIs, and actions are performed through well-known HTTP methods (GET, POST, PUT, DELETE, and so forth). Uniformity increases predictability and reduces the learning curve for developers using the API.

#### Code on Demand (Optional)  
This optional constraint allows servers to send executable code (such as JavaScript) to clients when needed. While rarely used in practice, it permits extending client functionality after deployment. The server transfers logic rather than just data, letting the client adapt its behavior without an update.

### Components of a RESTful System  
A RESTful approach identifies resources, manipulates those resources with standard HTTP methods, and communicates success or failure with standardized status codes.

##### Resources  
Resources are anything of interest that can be named, such as users, orders, articles, or blog posts. Each resource is usually identified by a URI like `/users/123` or `/posts/42`. Collections of resources are represented by plural nouns (e.g., `/users`), while individual resources include an identifier (e.g., `/users/42`).

##### Request Methods  
Common HTTP methods include GET for retrieval, POST for creation, PUT for full replacement, and DELETE for removals. PATCH is used for partial updates when only specific fields need to change. The table below summarizes each method and its typical semantics:

| Method  | Purpose              | Idempotent | Safe | Typical Status Codes       |
|---------|----------------------|------------|------|----------------------------|
| GET     | Retrieve a resource  | Yes        | Yes  | 200, 404                   |
| POST    | Create a resource    | No         | No   | 201, 400, 409              |
| PUT     | Replace a resource   | Yes        | No   | 200, 204, 404              |
| PATCH   | Partially update     | No*        | No   | 200, 204, 404              |
| DELETE  | Remove a resource    | Yes        | No   | 204, 404                   |
| HEAD    | Retrieve headers only| Yes        | Yes  | 200, 404                   |
| OPTIONS | Describe allowed methods | Yes    | Yes  | 200, 204                   |

\* PATCH can be made idempotent depending on implementation, but it is not required.

##### Response Codes  
HTTP status codes convey the result of a request. The table below lists commonly used codes grouped by category:

| Code | Name                  | Meaning                                                     |
|------|-----------------------|-------------------------------------------------------------|
| 200  | OK                    | Request succeeded; response body contains the result        |
| 201  | Created               | A new resource was successfully created                     |
| 204  | No Content            | Request succeeded; no body is returned                      |
| 301  | Moved Permanently     | Resource has a new permanent URI                            |
| 304  | Not Modified          | Cached version is still valid                               |
| 400  | Bad Request           | The request was malformed or invalid                        |
| 401  | Unauthorized          | Authentication is required or has failed                    |
| 403  | Forbidden             | The client lacks permission for this action                 |
| 404  | Not Found             | The requested resource does not exist                       |
| 409  | Conflict              | The request conflicts with the current state of the resource|
| 422  | Unprocessable Entity  | The request body is syntactically correct but semantically invalid |
| 429  | Too Many Requests     | The client has exceeded a rate limit                        |
| 500  | Internal Server Error | An unexpected server-side error occurred                    |
| 502  | Bad Gateway           | The server received an invalid response from an upstream server |
| 503  | Service Unavailable   | The server is temporarily unable to handle the request      |

### Idempotency  
An operation is idempotent if performing it multiple times produces the same result as performing it once. GET, PUT, and DELETE are idempotent by convention, which means repeating a failed request is safe. POST is not idempotent because each call may create a new resource. APIs often include an `Idempotency-Key` header so clients can safely retry POST requests without creating duplicates:

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Idempotency-Key: abc-123-unique" \
  -d '{"title":"Retry-safe Post"}' \
  http://example.com/posts
```

If the server has already processed a request with the same idempotency key, it returns the original response instead of creating a duplicate.

### HATEOAS  
Hypermedia as the Engine of Application State (HATEOAS) is a constraint where the server includes links in responses so clients can discover available actions dynamically. Rather than hardcoding endpoint URLs, clients follow links provided by the API:

```json
{
  "id": 1,
  "title": "My First Blog Post",
  "content": "This is my first blog post.",
  "_links": {
    "self": { "href": "/posts/1" },
    "author": { "href": "/users/42" },
    "comments": { "href": "/posts/1/comments" },
    "update": { "href": "/posts/1", "method": "PUT" },
    "delete": { "href": "/posts/1", "method": "DELETE" }
  }
}
```

HATEOAS makes APIs more discoverable and helps clients adapt when the server adds new features or changes URI structures.

### REST vs SOAP  
REST generally consumes fewer resources and uses less overhead than SOAP, making it a popular choice for modern web APIs. SOAP supports protocols beyond HTTP (such as SMTP), integrates standards for security and transactions, but can be more verbose.

| Aspect           | REST                              | SOAP                                        |
|------------------|-----------------------------------|---------------------------------------------|
| Protocol         | HTTP only                         | HTTP, SMTP, TCP, and others                 |
| Data format      | JSON, XML, or any format          | XML only                                    |
| Contract         | Informal (often OpenAPI/Swagger)  | Formal WSDL                                 |
| Statefulness     | Stateless by design               | Can be stateful or stateless                |
| Error handling   | HTTP status codes                 | SOAP fault elements in the XML body         |
| Security         | HTTPS, OAuth, JWT                 | WS-Security, WS-Trust                       |
| Tooling          | Lightweight, broad support        | Heavier, enterprise-oriented tooling        |
| Performance      | Generally faster (smaller payloads)| Slower due to XML parsing and envelope overhead |

### Content Negotiation  
Content negotiation allows the client and server to agree on the format of the data being exchanged. The client sends an `Accept` header indicating preferred formats, and the server responds with the best match:

```bash
curl -X GET -H "Accept: application/json" http://example.com/posts
```

The server uses the `Content-Type` header in the response to indicate the chosen format. Common media types include `application/json`, `application/xml`, and `text/plain`. A well-designed API typically defaults to JSON but can support additional formats when needed.

### Authentication and Authorization  
REST APIs commonly use one or more of the following strategies to control access:

- **API keys** are simple tokens passed in a header or query parameter. They identify the caller but provide limited security on their own.  
- **Bearer tokens (JWT)** are self-contained tokens that carry claims about the user. The server validates the token signature without needing a session store.  
- **OAuth 2.0** is a framework where a third-party authorization server issues tokens. It is well suited for delegated access, such as allowing an application to act on behalf of a user.  
- **Basic authentication** sends a base64-encoded username and password in the `Authorization` header. It should only be used over HTTPS.  

An example request with a bearer token:

```bash
curl -X GET \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://example.com/posts
```

### Rate Limiting  

Rate limiting protects an API from excessive use by capping the number of requests a client can make within a time window. Servers typically communicate limits through response headers:

| Header                  | Purpose                                         |
|-------------------------|-------------------------------------------------|
| `X-RateLimit-Limit`    | Maximum number of requests allowed in the window |
| `X-RateLimit-Remaining`| Requests remaining before the limit is reached   |
| `X-RateLimit-Reset`    | Timestamp when the window resets                 |
| `Retry-After`          | Seconds to wait before sending another request   |

When a client exceeds the limit, the server returns a `429 Too Many Requests` status code. Common strategies include fixed windows, sliding windows, and token-bucket algorithms.

### Pagination, Filtering, and Sorting

When an API returns a large collection of resources, it is usually not practical to send every item in a single response. Returning too much data at once can slow down the server, increase network usage, and make the client harder to work with. Pagination solves this problem by dividing results into smaller, manageable groups called pages.

Pagination is especially useful for endpoints that return lists, such as blog posts, users, products, comments, or search results. Instead of asking for every post at once, the client can request a limited number of posts at a time. This improves performance and gives users a smoother experience when browsing through data.

Filtering and sorting are often used together with pagination. Filtering allows the client to narrow the results based on specific criteria, while sorting controls the order in which the results are returned. Together, these features make an API more flexible and useful.

#### Offset-based pagination

Offset-based pagination uses two common query parameters: `offset` and `limit`. The `limit` parameter tells the server how many items to return, while the `offset` parameter tells the server how many items to skip before starting the response.

```bash
curl "http://example.com/posts?offset=20&limit=10"
```

Example output:

```json
{
  "data": [
    {
      "id": 21,
      "title": "Understanding API Pagination",
      "content": "Pagination helps divide large collections into smaller pages."
    },
    {
      "id": 22,
      "title": "REST API Design Tips",
      "content": "Consistent endpoint naming makes APIs easier to use."
    }
  ],
  "pagination": {
    "offset": 20,
    "limit": 10,
    "total": 52,
    "next_offset": 30,
    "previous_offset": 10
  }
}
```

In this example, the server skips the first 20 posts and returns the next set of results. The `pagination` object gives the client extra information about the current page, including the offset, limit, total number of posts, and where to start the next or previous page.

Offset-based pagination is simple to understand and easy to implement. It works well for smaller datasets or admin-style interfaces where users may want to jump to a specific page. However, it can become less reliable with large or frequently changing datasets. For example, if new posts are added or existing posts are deleted while a user is browsing, items may shift between pages, causing duplicates or missing results.

#### Cursor-based pagination

Cursor-based pagination uses a cursor value to mark the position of the last item retrieved. Instead of saying “skip 20 items,” the client says “continue after this specific point.” The cursor is usually an encoded value that represents information such as the last item’s ID, timestamp, or sorting position.

```bash
curl "http://example.com/posts?cursor=eyJpZCI6MjB9&limit=10"
```

Example output:

```json
{
  "data": [
    {
      "id": 21,
      "title": "Understanding API Pagination",
      "content": "Pagination helps divide large collections into smaller pages."
    },
    {
      "id": 22,
      "title": "REST API Design Tips",
      "content": "Consistent endpoint naming makes APIs easier to use."
    }
  ],
  "pagination": {
    "limit": 10,
    "next_cursor": "eyJpZCI6MjJ9",
    "previous_cursor": "eyJpZCI6MjB9",
    "has_more": true
  }
}
```

In this example, the server uses the cursor to determine where the next set of results should begin. The response includes a `next_cursor`, which the client can use to request the following page of results.

Cursor-based pagination is often preferred for large or frequently changing datasets because it avoids many of the problems caused by shifting records. It is especially useful for feeds, timelines, activity logs, and search results where new items may be added while users are browsing. A well-designed response may also include a `has_more` field so the client knows whether additional pages are available.

#### Filtering and sorting

Filtering allows clients to request only the resources that match certain conditions. Sorting determines the order in which those resources are returned. These options are usually passed as query parameters in the URL.

```bash
curl "http://example.com/posts?author=jane&sort=created_at&order=desc"
```

Example output:

```json
{
  "data": [
    {
      "id": 34,
      "title": "Advanced REST API Patterns",
      "author": "jane",
      "created_at": "2025-03-18T10:30:00Z",
      "content": "Advanced REST patterns help make APIs more predictable."
    },
    {
      "id": 27,
      "title": "Getting Started with REST",
      "author": "jane",
      "created_at": "2025-02-11T14:15:00Z",
      "content": "REST APIs use resources, methods, and representations."
    }
  ],
  "filters": {
    "author": "jane"
  },
  "sorting": {
    "sort": "created_at",
    "order": "desc"
  }
}
```

In this example, the server returns only posts written by `jane`. The results are sorted by the `created_at` field in descending order, so the newest post appears first.

Filtering and sorting make the API more efficient because the client receives only the data it actually needs. They also improve usability because clients can build features such as search pages, category views, author pages, and newest-first lists without needing to process all the data themselves.

Consistent query parameter naming across all endpoints makes the API easier to learn. For example, using `limit`, `cursor`, `sort`, and `order` in the same way across multiple endpoints helps developers understand the API more quickly and reduces mistakes when building applications.

### Creating a RESTful API

Designing a RESTful API means creating a clear and predictable way for clients, such as web apps, mobile apps, or other services, to interact with data on a server. In a RESTful design, each important object in the system is treated as a **resource**. For example, in a blogging application, a blog post can be represented as a resource called `posts`.

A RESTful API usually exposes resources through endpoints such as `/posts` or `/posts/{id}`. These endpoints are combined with HTTP methods like `POST`, `GET`, `PUT`, and `DELETE` to define what action should happen. The API also decides how data will be sent and received, commonly using JSON because it is lightweight and easy to read.

#### POST - Create a new post

The `POST` method is used when a client wants to create a new resource on the server. In this case, the client sends the title and content of a new blog post to the `/posts` endpoint. The server receives the data, creates a new post, assigns it a unique ID, and returns the newly created resource.

```
POST /posts
```

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"title":"My First Blog Post","content":"This is my first blog post."}' \
http://example.com/posts
```

Example output:

```json
{
  "id": 1,
  "title": "My First Blog Post",
  "content": "This is my first blog post."
}
```

The server created a new post and assigned it an ID of `1`. This ID can be used later to retrieve, update, or delete the specific post. A successful `POST` request often returns a `201 Created` status code, which indicates that the resource was successfully created on the server.

#### GET - Retrieve all posts

The `GET` method is used to request data from the server without changing it. When a client sends a `GET` request to `/posts`, it is asking the server to return a list of all available blog posts. This type of request is useful when displaying a feed, index page, or archive of posts.

```
GET /posts
```

```bash
curl -X GET http://example.com/posts
```

Example output:

```json
[
  {
    "id": 1,
    "title": "My First Blog Post",
    "content": "This is my first blog post."
  },
  {
    "id": 2,
    "title": "Another Post",
    "content": "More content."
  }
]
```

The response includes an array of post objects. Each object represents one blog post and contains fields such as `id`, `title`, and `content`. A `200 OK` status code means the request was successful and the server was able to return the requested data.

#### GET - Retrieve a specific post

A `GET` request can also be used to retrieve one specific resource. Instead of requesting `/posts`, the client includes the post’s ID in the URL, such as `/posts/1`. This tells the server to return only the blog post that matches that ID.

```
GET /posts/{id}
```

```bash
curl -X GET http://example.com/posts/1
```

Example output:

```json
{
  "id": 1,
  "title": "My First Blog Post",
  "content": "This is my first blog post."
}
```

The server returned the post identified by ID `1`. This is useful when displaying a single blog post page or when a client needs the full details of one resource. A successful response typically comes with a `200 OK` status code. If no post with that ID exists, the server would usually return a `404 Not Found` error.

#### PUT - Update a post

The `PUT` method is used to update an existing resource. In this example, the client sends new data for the post with ID `1`. The server replaces or updates the existing post with the new title and content provided in the request body.

```
PUT /posts/{id}
```

```bash
curl -X PUT -H "Content-Type: application/json" \
-d '{"title":"My Updated Blog Post","content":"Updated content."}' \
http://example.com/posts/1
```

Example output:

```json
{
  "id": 1,
  "title": "My Updated Blog Post",
  "content": "Updated content."
}
```

The server updated the existing post with the new title and content. The response shows the updated version of the resource, confirming that the change was applied successfully. A server may return a `200 OK` status code with the updated resource, or a `204 No Content` status code if the update succeeded but no response body is returned.

#### DELETE - Delete a post

The `DELETE` method is used to remove a resource from the server. In this example, the client sends a request to `/posts/1`, which tells the server to delete the blog post with the ID of `1`.

```
DELETE /posts/{id}
```

```bash
curl -X DELETE http://example.com/posts/1
```

Example output:

```text
(No response body)
```

The post with ID `1` was removed from the server. A successful delete operation often returns a `204 No Content` status code, meaning the request was successful but there is no response body to display. If the client tries to retrieve the same post again after deletion, the server would typically return a `404 Not Found` error because the resource no longer exists.

### Common Commands with curl  
curl is a popular command-line tool for sending HTTP requests to REST endpoints. The table below describes a few commonly used options:

| Option      | Description                                              |
|-------------|----------------------------------------------------------|
| -X METHOD   | Specifies the HTTP method (GET, POST, PUT, DELETE, etc.) |
| -H          | Adds extra HTTP headers                                  |
| -d          | Sends data in the request body (for POST, PUT, etc.)     |
| -i          | Includes HTTP response headers in the output             |
| -v          | Shows verbose (detailed) request/response information    |

### Best Practices for REST API Design  

A few guidelines improve the usefulness and maintainability of RESTful services:

- Version your endpoints so existing clients are not broken by changes. Common strategies include URL path versioning (`/v1/posts`), custom headers (`Accept-Version: v2`), and query parameters (`?version=1`).  
- Handle errors gracefully by using clear status codes and messages. Include a consistent error response body with fields like `code`, `message`, and `details` so clients can programmatically handle failures.  
- Use HTTPS to protect data in transit, and rely on token-based authentication or OAuth for secure access.  
- Split large data sets through pagination, filtering, or searching to keep responses manageable.  
- Document your endpoints, request formats, and response examples so developers can integrate quickly. Tools like OpenAPI (Swagger) generate interactive documentation from a specification file.  
- Use plural nouns for resource names (`/users`, `/posts`) and avoid verbs in URIs since the HTTP method already conveys the action.  
- Support idempotency keys for non-idempotent operations to allow safe retries.  
- Return appropriate status codes rather than always returning 200 with an error message in the body.  
- Provide meaningful `Location` headers after creating resources so clients can follow up immediately.  
- Consider hypermedia links (HATEOAS) to make the API self-discoverable and reduce tight coupling between client and server.
