
## REST: Representational State Transfer

REST APIs operate on a simple request/response system. When a client makes a request using an HTTP method, the server returns a response with an HTTP status code.

### REST API Constraints

There are four constraints that a RESTful API must adhere to:

1. Client-server architecture with no third party
2. Cacheability (response can be cacheable)
3. Statelessness (there is no state, client and server are completely separated)
4. Uniform interface

### HTTP Headers

Client and server can pass extra bits of information with the request and response using HTTP headers. Some commonly used headers are:

- `Accept` - type of data client can understand
- `Accept-Encoding` - which encoding method client can understand
- `Accept-Language` - client is expecting a response in a given language
- `Content-type` - specifies the media type of the resource
- `Host` - specifies the domain name
- `Authorization` - used to pass credentials to the server
- `Access-Control-Allow-Origin` - which origin is allowed to access the resources
- `Access-Control-Allow-Methods` - which methods are allowed to access the cross-origin resources

### HTTP Status Codes

HTTP status codes are three-digit numbers that indicate the status of the server's response. Here are some commonly used status codes:

- Successful responses:
  - `200 OK` - everything is fine
- Redirection messages:
  - `301 Moved Permanently` - the resource has been moved permanently to the new URL
- Client errors:
  - `400 Bad Request` - invalid syntax
  - `401 Unauthorized` - credentials are incorrect
  - `404 Not Found` - invalid URL
- Server errors:
  - `500 Internal Server Error`

### HTTP Methods

HTTP methods are used to specify the desired action to be performed on a resource. Here are some commonly used methods:

- The `GET` method is the most common of all these. It is used to fetch the desired resources from the server.
- The `PUT` method is used whenever you need to change the resource which is already on the server.
- The `POST` method is used to submit the information to the server.
- The `PATCH` request is used to modify only the necessary part of the response.
- The `DELETE` method is used to delete the specified resources.

### Caching in API Calls

Caching can be used to improve the performance of API calls. When a client sends a request, the server checks if the response is cached. If it is cached, the server sends the cached response to the client, which reduces the amount of data sent over the network and improves the response time.

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
