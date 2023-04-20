## REST
REST APIs work with a basic request/response system. Clients use HTTP methods to ask for things, and servers reply with HTTP status codes.

### REST API Rules

RESTful APIs follow these rules:

1. Client-server setup without third parties
2. Responses can be stored in cache
3. No state (client and server are separate)
4. Consistent interface

### HTTP Headers

HTTP headers let clients and servers share extra info. Common headers include:

- `Accept` - data types the client can understand
- `Accept-Encoding` - encoding methods the client can understand
- `Accept-Language` - expected response language
- `Content-type` - resource media type
- `Host` - domain name
- `Authorization` - credentials for the server
- `Access-Control-Allow-Origin` - allowed origins to access resources
- `Access-Control-Allow-Methods` - allowed methods to access resources

### HTTP Status Codes

HTTP status codes are three-digit numbers showing the server's response. Some common codes:

- Good responses:
  - `200 OK` - all is well
- Redirection messages:
  - `301 Moved Permanently` - resource moved to new URL
- Client errors:
  - `400 Bad Request` - wrong syntax
  - `401 Unauthorized` - wrong credentials
  - `404 Not Found` - wrong URL
- Server errors:
  - `500 Internal Server Error`

### HTTP Methods

HTTP methods tell what action to take on a resource. Common methods:

- `GET` - fetches resources from the server
- `PUT` - updates resources on the server
- `POST` - sends info to the server
- `PATCH` - changes only needed parts of the response
- `DELETE` - removes specified resources

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
