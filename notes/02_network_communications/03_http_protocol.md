## HTTP Protocol

HTTP (Hypertext Transfer Protocol) is the foundational protocol used for transferring data over the web. It is a request-response protocol between a client and a server.

```
[Client]          [Internet]          [Server]
  |                   |                   |
  |--- HTTP Request ->|                   |
  | GET / HTTP/1.1    |                   |
  | Host: example.com |                   |
  | User-Agent: ...   |                   |
  |                   |                   |
  |                   |--- HTTP Request ->|
  |                   | GET / HTTP/1.1    |
  |                   | Host: example.com |
  |                   | User-Agent: ...   |
  |                   |                   |
  |                   |<-- HTTP Response -|
  |                   | HTTP/1.1 200 OK   |
  |                   | Content-Type: ... |
  |                   | ...               |
  |<-- HTTP Response -|                   |
  | HTTP/1.1 200 OK   |                   |
  | Content-Type: ... |                   |
  | ...               |                   |
```

### Key Concepts

- **Request and Response**: Every interaction in HTTP is made up of a request made by the client and a response from the server.
- **Stateless Protocol**: HTTP is stateless, meaning each request-response pair is independent, and the server does not retain any state between different requests.
- **Methods**: HTTP defines a set of request methods to indicate the desired action to be performed. Common methods include GET, POST, PUT, DELETE.

### HTTP Request

- *Method*: Indicates the action (e.g., GET, POST).
- *URL*: The location of the resource on the server.
- *Headers*: Provide additional information (e.g., User-Agent, Content-Type).
- *Body*: Optional data sent to the server (mostly in POST requests).

### HTTP Response

- *Status Code*: Indicates the result of the request (e.g., 200 OK, 404 Not Found).
- *Headers*: Server information and further details about the response.
- *Body*: The actual content being delivered (e.g., HTML, JSON).

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

```
Client       Server
  |            |
  |---Req1---> |
  |<--Resp1--- |
  |            |
  |---Req2---> |
  |<--Resp2--- |
  |            |
  [Sequential Requests]
```

## HTTP/2

HTTP/2, ratified as a standard in 2015, was designed to overcome the limitations of HTTP/1.1 and improve performance.

1. **Binary Protocol**: HTTP/2 is a binary protocol, which means data is transferred in a format that is more machine-friendly. This leads to more efficient parsing and less errors compared to textual protocols.

2. **Multiplexing**: HTTP/2 introduces multiplexing, which allows multiple requests and responses to be sent simultaneously on the same connection. This effectively removes the "head-of-line blocking" issue in HTTP/1.1.

3. **Server Push**: HTTP/2 introduces a server push mechanism, where the server can send critical resources proactively to the client before the client even asks for them. This can reduce the perceived load time for users.

4. **Header Compression**: HTTP/2 uses HPACK compression to reduce overhead, which can significantly reduce the amount of data needed for HTTP headers.

5. **Stream Prioritization**: HTTP/2 allows requests to be prioritized, which can provide more resources to higher priority streams.

```
Client                 Server
  |                        |
  |---Req1---|             |
  |---Req2---|             |
  |---Req3---|             |
  |<---------Multiplexed---|
  |-----Data Flow----------|
  |                        |
  [Concurrent Streams]
```

## HTTP/1 vs HTTP/2

| Feature           | HTTP/1                        | HTTP/2                          |
|-------------------|-------------------------------|---------------------------------|
| **Protocol Type** | Text-based                    | Binary, making it more efficient|
| **Connections**   | One request per TCP connection| Multiplexed requests over a single TCP connection |
| **Performance**   | Slower due to TCP connection limits and head-of-line blocking | Faster, efficient use of a single connection reduces latency |
| **Compression**   | Headers are not compressed    | Header compression with HPACK   |
| **Server Push**   | Not available                 | Server can push resources proactively |
| **Prioritization**| No native prioritization      | Stream prioritization allows more important resources to be sent first |
