## HTTP Headers

HTTP headers let clients and servers share extra info. Common headers include:

- `Accept` - data types the client can understand
- `Accept-Encoding` - encoding methods the client can understand
- `Accept-Language` - expected response language
- `Content-type` - resource media type
- `Host` - domain name
- `Authorization` - credentials for the server
- `Access-Control-Allow-Origin` - allowed origins to access resources
- `Access-Control-Allow-Methods` - allowed methods to access resources

## HTTP Status Codes

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

## HTTP Methods

HTTP methods tell what action to take on a resource. Common methods:

- `GET` - fetches resources from the server
- `PUT` - updates resources on the server
- `POST` - sends info to the server
- `PATCH` - changes only needed parts of the response
- `DELETE` - removes specified resources

## HTTP/1.1

HTTP/1.1 was defined in 1997 and has been the standard for web traffic for a long time.

1. **Textual Protocol**: HTTP/1.1 is a textual protocol, which means that the transmission of data happens in human-readable format. While this is advantageous for manual debugging, it's less efficient for computers to parse.

2. **Connection Per Request**: HTTP/1.1 opens a new TCP connection for each request. This can lead to a condition known as "head-of-line blocking," where multiple requests can slow down the performance of each other.

3. **No Push Mechanism**: There is no built-in server push mechanism in HTTP/1.1, meaning the server can't proactively send resources to the client without a specific request from the client.

## HTTP/2

HTTP/2, ratified as a standard in 2015, was designed to overcome the limitations of HTTP/1.1 and improve performance.

1. **Binary Protocol**: HTTP/2 is a binary protocol, which means data is transferred in a format that is more machine-friendly. This leads to more efficient parsing and less errors compared to textual protocols.

2. **Multiplexing**: HTTP/2 introduces multiplexing, which allows multiple requests and responses to be sent simultaneously on the same connection. This effectively removes the "head-of-line blocking" issue in HTTP/1.1.

3. **Server Push**: HTTP/2 introduces a server push mechanism, where the server can send critical resources proactively to the client before the client even asks for them. This can reduce the perceived load time for users.

4. **Header Compression**: HTTP/2 uses HPACK compression to reduce overhead, which can significantly reduce the amount of data needed for HTTP headers.

5. **Stream Prioritization**: HTTP/2 allows requests to be prioritized, which can provide more resources to higher priority streams.
