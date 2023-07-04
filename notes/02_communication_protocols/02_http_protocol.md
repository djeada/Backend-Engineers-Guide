
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

