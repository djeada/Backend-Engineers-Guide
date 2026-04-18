## REST  
Representational State Transfer, often referred to as REST, is an architectural style used to design web services. It uses a stateless communication model between clients and servers, relies on standard HTTP methods, and focuses on simple but powerful conventions. These notes explore the core principles of REST, examine its components, illustrate how requests flow, and include examples of building and interacting with a RESTful API.

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
Large collections should never be returned in a single response. Pagination splits results into manageable pages:

#### Offset-based pagination  
```bash
curl "http://example.com/posts?offset=20&limit=10"
```

#### Cursor-based pagination  
```bash
curl "http://example.com/posts?cursor=eyJpZCI6MjB9&limit=10"
```

Cursor-based pagination is preferred for large or frequently changing datasets because it avoids issues with items shifting between pages.

#### Filtering and sorting  
```bash
curl "http://example.com/posts?author=jane&sort=created_at&order=desc"
```

The server returns only the posts matching the filter criteria, sorted as requested. Consistent query parameter naming across all endpoints makes the API easier to learn.

### Creating a RESTful API  
Designing a RESTful API involves setting up endpoints for resources, determining how HTTP methods map to operations, and deciding on representations like JSON or XML. Maintaining statelessness and offering caching helps keep performance optimal.

These examples demonstrate how to create, read, update, and delete blog posts through a hypothetical RESTful service. Each code example is shown with the resulting output and a short interpretation.

#### POST - Create a new post  
```
POST /posts
```
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"title":"My First Blog Post","content":"This is my first blog post."}' \
http://example.com/posts
```
- Example output:
  ```json
  {
      "id": 1,
      "title": "My First Blog Post",
      "content": "This is my first blog post."
  }
  ```
- Interpretation of the output:  
  The server created a new post with an assigned ID (1). The response often comes with a 201 Created status code, indicating a successful resource creation.

#### GET - Retrieve all posts  
```
GET /posts
```
```bash
curl -X GET http://example.com/posts
```
- Example output:
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
- Interpretation of the output:  
  The response includes an array of posts. A 200 OK status code means the request was successful.

#### GET - Retrieve a specific post  
```
GET /posts/{id}
```
```bash
curl -X GET http://example.com/posts/1
```
- Example output:
  ```json
  {
      "id": 1,
      "title": "My First Blog Post",
      "content": "This is my first blog post."
  }
  ```
- Interpretation of the output:  
  The server returned the post identified by ID 1. This also typically comes with a 200 OK status code.

#### PUT - Update a post  
```
PUT /posts/{id}
```
```bash
curl -X PUT -H "Content-Type: application/json" \
-d '{"title":"My Updated Blog Post","content":"Updated content."}' \
http://example.com/posts/1
```
- Example output:
  ```json
  {
      "id": 1,
      "title": "My Updated Blog Post",
      "content": "Updated content."
  }
  ```
- Interpretation of the output:  
  The server updated the existing post with new title and content. A 200 OK or 204 No Content status code may be returned.

#### DELETE - Delete a post  
```
DELETE /posts/{id}
```
```bash
curl -X DELETE http://example.com/posts/1
```
- Example output:
  ```
  (No response body)
  ```
- Interpretation of the output:  
  The post with ID 1 was removed. A 204 No Content code is typically returned to indicate success. Retrieving the post again would yield a 404 Not Found error.

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
