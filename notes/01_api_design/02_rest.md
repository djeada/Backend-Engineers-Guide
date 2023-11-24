## REST (Representational State Transfer)

REST APIs adopt a request-response model where clients utilize HTTP methods to solicit information, and servers respond using HTTP status codes.

```
+---------------------+                   +----------------------+
|                     |                   |                      |
|    REST Client      |                   |    RESTful API       |
|  (e.g., Web Browser,|                   |    Server            |
|   Mobile App)       |                   |                      |
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
|  (e.g., Render in UI |                   
|   or Trigger Action) |                   
|                      |                   
+----------------------+                   
```

## Core Principles of REST

REST operates on a set of guiding principles:

- **Client-Server Architecture**: This principle separates the user interface from data storage concerns, enhancing the user interface's portability across different platforms and bolstering scalability by simplifying server components.

   I. Non-RESTful system:

   In a system that doesn't adhere to the client-server architecture, the user interface and data storage logic might be tightly intertwined and reside on the same server. This lack of separation means that changes in the user interface can directly impact the data storage logic, and vice versa. Such a system is difficult to maintain, and its scalability is limited, as UI changes may necessitate corresponding backend changes.

   II. RESTful system:

   In contrast, a RESTful system adheres to a clear client-server architecture. The client is only responsible for the user interface, and the server manages the data storage. This separation of concerns means the user interface can be updated or entirely changed without affecting the server. Similarly, server-side changes have minimal impact on the client. This clear delineation allows each to scale independently, increasing the overall system's robustness and flexibility.

- **Stateless**: Every client-to-server request must encapsulate all the necessary information for processing. 

   I. Non-RESTful system:

   In a system that doesn't respect the stateless principle, the server might maintain the client's state between requests. This means the server has to keep track of and manage all active clients' states, which can increase complexity and limit scalability. Further, the presence of server-side state can lead to inconsistencies and potential errors in state management.

   II. RESTful system:

   Conversely, a RESTful system is stateless. Every client-to-server request contains all the information needed for the server to understand and process the request. The server does not need to remember previous requests or sessions, making the system easier to manage, more robust, and more scalable.
  
- **Cacheable**: This principle necessitates that the data within a response to a request be explicitly or implicitly marked as cacheable or non-cacheable. 

   I. Non-RESTful system:

   A system that does not implement caching will always fetch fresh data from the server, even if the data hasn't changed since the last request. This practice can result in unnecessary data transfers, which consume bandwidth and increase response times, leading to a slower, less efficient system.
  
   II. RESTful system:

   In contrast, a RESTful system uses caching as stipulated by the cacheable principle. Responses are explicitly or implicitly labeled as cacheable or non-cacheable. Cacheable responses can be reused for subsequent requests, reducing server load and network traffic, leading to faster response times and an overall more efficient system.
  
- **Layered System**: In this setup, the architecture can comprise hierarchical layers, constraining component behavior such that each component cannot "see" beyond the immediate layer they interact with.

   I. Non-RESTful system:

   In a system that isn't layered, components may have visibility into, or dependencies on, multiple other components or layers. This lack of layering can result in tight coupling between components, making the system more rigid and harder to change or extend.

   II. RESTful system:

   In contrast, a RESTful system adheres to the principle of a layered architecture. This means that each component or layer can only interact with the layer directly below or above it. This separation makes the system more modular, allowing for easier updates and extensions without affecting the whole system.
  
- **Uniform Interface**: The mode of communication between a client and a server must maintain uniformity. This principle simplifies and decouples the architecture, allowing each component to evolve independently.

   I. Non-RESTful system:

   In a non-RESTful system, different clients may have different interfaces to communicate with the server. This could lead to high complexity in maintaining multiple interfaces, and less reuse of components, reducing the system's overall efficiency and maintainability.

   II. RESTful system:

   A RESTful system, on the other hand, follows the principle of a uniform interface. Regardless of the client making the request, the server's interface remains the same. This consistency simplifies the architecture and allows components to evolve independently of each other. It also makes the system more predictable and easier to use for developers.
  
## Components of REST

- **Resources**: These are akin to Object instances in OOP, each with a unique identifier, typically a URI.

- **Request Methods**: REST explicitly uses HTTP methods like GET, POST, PUT, DELETE, among others.

- **Response Codes**: HTTP response status codes denote the successful completion of a specific HTTP request, such as 200 (OK), 404 (Not Found), 500 (Internal Server Error), etc.

### API Call Caching

Caching makes API calls faster. When clients ask for something, servers check if the response is cached. If so, the server sends the cached response, reducing data sent and speeding up the response.

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


## REST vs SOAP

- REST is generally faster and uses less bandwidth. It leverages less messaging overhead than SOAP.

- SOAP, on the other hand, is highly extensible, and it allows for language, platform, and transport independence, which means it can be used over any protocol (HTTP, SMTP, TCP, etc.)

## RESTful APIs

A RESTful API is an API that adheres to the principles of REST. It uses HTTP requests to GET, PUT, POST, and DELETE data.

## Creating a RESTful API

When designing a RESTful API:

- Use HTTP methods explicitly.
- Be stateless.
- Expose directory structure-like URIs.
- Transfer XML, JavaScript Object Notation (JSON), or both.

## Example: Blogging Platform RESTful API

### POST - Create a new post

Endpoint: `POST /posts`

Request Body:

```json
{
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post."
}
```

Successful Response:

```json
{
    "id": 1,
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post."
}
```

### GET - Retrieve all posts

Endpoint: `GET /posts`

Successful Response:

```json
[
    {
        "id": 1,
        "title": "My First Blog Post",
        "content": "This is the content of my first blog post."
    },
    ...
]
```

### GET - Retrieve a specific post

Endpoint: `GET /posts/{id}`

Example: `GET /posts/1`

Successful Response:

```json
{
    "id": 1,
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post."
}
```
### PUT - Update a post

Endpoint: `PUT /posts/{id}`

Request Body:

```json
{
    "title": "My Updated Blog Post",
    "content": "This is the updated content of my blog post."
}
```

Successful Response:

```json
{
    "id": 1,
    "title": "My Updated Blog Post",
    "content": "This is the updated content of my blog post."
}
```

### DELETE - Delete a post

Endpoint: `DELETE /posts/{id}`

Example: `DELETE /posts/1`

Successful Response: `HTTP 204 No Content`


## Best Practices for REST API Design

- **Versioning**: Keep backward compatibility by allowing different versions of APIs to be available to clients.
  
- **Error handling**: Use HTTP status codes to explain errors and always return human-readable error messages.
  
- **Secure REST APIs**: Always use HTTPS and consider token-based authentication.

- **Pagination**: Don't return all resources at once, but divide them into pages.

- **Filtering, Sorting, and Searching**: Give users the ability to find exactly what they need by providing robust filtering, sorting, and searching options.
  
- **Use of status codes**: Use HTTP status codes to indicate the outcome of the HTTP request. They indicate whether a specific HTTP request has been successfully completed.

- **API Documentation**: Clear, comprehensive documentation is essential. It helps developers understand how to use your API effectively.

