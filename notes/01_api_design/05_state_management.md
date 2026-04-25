## State Management  
Stateful and stateless designs are common terms in software architecture. They describe how an application handles data over multiple interactions. This set of notes explains the differences between applications that remember information between requests and those that treat every request as a fresh transaction.
### The Concept of State

Software often needs to remember information about users, actions, preferences, sessions, or transactions. This remembered information is called **state**. State can influence how the application behaves in the future because the system can use previous information to decide what should happen next.

For example, an online store might remember that a user is logged in, which items are in their shopping cart, and what shipping address they selected. A banking application might remember the current step in a transfer process. A learning platform might remember which lesson a student completed most recently.

In a **stateful** design, the application stores information between requests. This information may be kept in server memory, a database, a cache, or another persistent storage system. In a **stateless** design, each request is handled independently, and the server does not rely on stored context from previous requests.

A quick concurrency formula for a system that stores user sessions in memory could look like this:

```text
M_total = N_sessions * S_session
```

Example calculation:

```text
N_sessions = 10,000
S_session = 50 KB

M_total = 10,000 * 50 KB
M_total = 500,000 KB
M_total ≈ 500 MB
```

Example output:

```text
Estimated memory required for session state: 500 MB
```

`M_total` indicates the total memory required, `N_sessions` is the number of simultaneous sessions, and `S_session` is the memory required per session. If the number of sessions grows, the memory required also grows. This can become a problem when session state is stored directly on the server, especially if the application needs to support many users at the same time.

### Stateful Applications

A **stateful application** tracks user or session data across multiple requests. This means the server remembers information about what happened earlier and can use that information when handling future requests.

For example, after a user logs in, the server might remember their session. When the user later views their profile, updates settings, or adds an item to a shopping cart, the server can connect those actions to the same user. This makes many application workflows easier to design because the server already has access to the needed context.

Stateful applications are useful when the system needs continuity. Multi-step forms, shopping carts, online games, chat sessions, dashboards, and transaction workflows often depend on state. The application can remember where the user is in the process and respond accordingly.

Here is a high-level ASCII diagram illustrating how a stateful server might maintain and update state as multiple clients interact:

```text
+-----------+            +-----------+
|  Client A |            |  Client B |
+-----+-----+            +-----+-----+
    |                        |
    |   Request with         |   Request with
    |   Session Info         |   Session Info
    v                        v
+-----------------------------------------+
|                API Server               |
|-----------------------------------------|
|  State Management (Session Tracking)    |
|  - User Data                            |
|  - Preferences                          |
|  - Interaction History                  |
+-----------------------------------------+
    ^                        ^
    |    Response with       |   Response with
    |    Updated State       |   Updated State
+-----+-----+            +-----+-----+
|  Client C |            |  Client D |
+-----------+            +-----------+
```

Example request:

```http
POST /cart/items
Cookie: session_id=abc123
Content-Type: application/json

{
  "productId": "book-1",
  "quantity": 2
}
```

Example output:

```json
{
  "sessionId": "abc123",
  "cart": {
    "items": [
      {
        "productId": "book-1",
        "quantity": 2
      }
    ],
    "totalItems": 2
  }
}
```

In this example, the client sends a request that includes a session identifier. The server uses that session identifier to find the user’s existing cart state, updates it, and returns the new cart information. The next request from the same session can continue from this updated state.

The server updates shared or session-specific state and returns new information to each client. This enables more cohesive workflows because the server can remember previous actions and maintain continuity across requests.

#### Advantages of Stateful Applications

Stateful applications can make certain workflows easier to build because the server keeps track of important context. Instead of requiring every request to include all information from previous steps, the server can remember it.

One advantage is that stateful applications can maintain logical continuity. This often leads to more intuitive code when designing multi-step processes. For example, a checkout process might include cart review, shipping information, payment details, and order confirmation. A stateful server can remember progress across those steps.

Another advantage is a smoother user experience. Users expect applications to remember data such as login sessions, shopping cart contents, preferences, recently viewed items, or draft work. Stateful systems make it easier to provide this kind of continuity.

Stateful applications can also handle complex, multi-stage workflows more easily because the server has the necessary context. This is useful for workflows such as booking travel, completing forms, processing transactions, or managing real-time collaboration.

Example stateful workflow:

```text
Step 1: User logs in
Step 2: Server creates session abc123
Step 3: User adds item to cart
Step 4: Server stores cart under session abc123
Step 5: User checks out
Step 6: Server uses stored session and cart data
```

Example output:

```json
{
  "sessionId": "abc123",
  "currentStep": "checkout",
  "cartItems": 3,
  "userLoggedIn": true
}
```

This output shows that the server remembers the user’s session, cart, and current workflow step. The client does not need to resend the full cart or login context with every request.

#### Disadvantages of Stateful Applications

Stateful applications can be harder to scale because state must remain available and consistent across requests. If session data is stored on one server, future requests from the same user may need to reach that same server. This can complicate load balancing and deployment.

One disadvantage is that each application instance needs consistent access to session data. If there are multiple server instances, they must either share state through a central store, replicate state between servers, or rely on session affinity. Each option adds operational complexity.

Another disadvantage is the risk of data loss. If session state is stored only in memory and the server crashes, that state may disappear. This can log users out, clear shopping carts, interrupt workflows, or lose temporary progress unless proper failover or persistence is in place.

Load balancing can also become more complicated. Some systems use **session affinity**, also called sticky sessions, to route the same user to the same server instance. While this can work, it may reduce flexibility because traffic is no longer distributed purely based on current server capacity.

Example problem scenario:

```text
User session abc123 is stored in Server 1 memory.

Request 1 → Server 1 → Success
Request 2 → Server 2 → Session not found
```

Example error output:

```json
{
  "error": "Session not found",
  "code": "SESSION_MISSING"
}
```

In this example, the user’s session exists only on Server 1. If the load balancer sends the next request to Server 2, that server may not know anything about the session. To avoid this, teams often use shared session storage, distributed caches, databases, or sticky sessions.

Stateful applications are powerful, but they require careful planning. As traffic grows, teams need reliable ways to store, replicate, expire, and recover state so users do not lose important progress.

#### Example: Stateful Counter

A stateful counter is a simple example of how a server can remember information between requests. Instead of the client keeping track of the count, the server stores the current counter value in memory. Each time the user clicks a button, the client sends a request to the server, and the server increments its stored value.

This design means the server is responsible for remembering the current state. The client only needs to say that an increment happened. It does not need to calculate the new value itself or send the previous count back to the server.

```javascript id="t6r64k"
// Client-side
button.addEventListener("click", function() {
    // Just notify the server that the button was clicked
    fetch('/increment', { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        console.log(data.counter); // e.g., 5
      });
});

// Server-side
let counter = 0;

app.post("/increment", (req, res) => {
    counter++;
    res.json({ counter: counter });
});
```

Example request:

```http id="xr4rxx"
POST /increment
```

Example output after the first click:

```json id="kc4crc"
{
  "counter": 1
}
```

Example output after the fifth click:

```json id="bje5ur"
{
  "counter": 5
}
```

In this example, the `counter` variable lives in the server’s memory. Every time the `/increment` endpoint is called, the server increases the stored value by one and sends the updated total back to the client.

The important detail is that the client does not send the current count. It only sends a request saying that the button was clicked. The server remembers the previous value and uses it to calculate the next value.

This approach is easy to understand and works well for a single server running a small application. However, it becomes more complicated when the application runs on multiple servers.

Example multi-server problem:

```text id="yewnxa"
Request 1 → Server A → counter = 1
Request 2 → Server B → counter = 1
Request 3 → Server A → counter = 2
```

Example inconsistent output:

```json id="bt2ppn"
{
  "serverA_counter": 2,
  "serverB_counter": 1
}
```

If each server keeps its own counter in memory, the count can become inconsistent. One server may think the counter is `2`, while another server thinks it is `1`. To avoid this, multiple servers must share or synchronize the count using a shared database, distributed cache, or another centralized state store.

A more scalable version might store the counter in Redis or a database instead of keeping it only in local memory. That way, every server reads and updates the same counter value, regardless of which server receives the request.

### Stateless Applications

Stateless applications process each request independently. This means the server does not remember previous interactions, session data, or user-specific progress between requests. Each request must include all the information the server needs to complete the operation.

In a stateless design, the server treats every request as a new and complete unit of work. It does not depend on local memory from earlier requests. This makes the system easier to scale because any server instance can handle any request.

For example, if an application has five identical server instances, a stateless request can go to any one of them. The server does not need to know what happened in the previous request because the client provides the required context each time.

The main tradeoff is that the client or request must carry more information. This can make client-side code more responsible for storing temporary state, such as tokens, form progress, selected options, or the current value of a counter.

#### Advantages of Stateless Applications

Stateless applications are often easier to scale horizontally. Since the server does not store session-specific information in memory, new server instances can be added behind a load balancer without needing to copy or synchronize user state.

This makes stateless systems especially useful for cloud environments, containerized deployments, and APIs that receive high traffic. If one server becomes overloaded, requests can be routed to another server without worrying about whether that server has the user’s session data.

Another advantage is simpler failure handling. If a server crashes, another server can handle the next request because no important session state was stored only on the failed machine. This reduces the risk of users losing progress due to server-side memory loss.

Requests are also often easier to retry because they include the information needed for processing. While not every stateless request is automatically idempotent, stateless designs often encourage clearer request boundaries and more predictable behavior.

Example stateless request flow:

```text
Request 1 → Server A → Success
Request 2 → Server B → Success
Request 3 → Server C → Success
```

Example output:

```json
{
  "status": "success",
  "message": "Any available server can process the request."
}
```

In this example, each request can be handled by a different server. No special routing is required because the servers do not depend on locally stored session state.

#### Disadvantages of Stateless Applications

Stateless applications can make complex multi-step workflows harder to implement. Since the server does not remember previous steps, the client must send enough information for the server to understand the current request.

For example, a checkout process may require cart contents, shipping details, payment information, and user identity. In a purely stateless design, the server needs that context to be included with each relevant request or retrieved from external storage.

Code can also become more verbose because the client may need to repeatedly send the same information. This can increase request size and make client-side logic more complicated.

Client overhead increases as well. The client may need to store temporary data locally, manage tokens, track progress through a workflow, and provide the correct context on every request. If the client loses that information, the server may not be able to continue the process.

Example missing-context problem:

```http
POST /checkout/confirm
Content-Type: application/json

{
  "paymentToken": "tok_123"
}
```

Example error output:

```json
{
  "error": "Missing cart and shipping information",
  "code": "INSUFFICIENT_CONTEXT"
}
```

In this example, the server cannot complete the checkout confirmation because the request does not include enough information. Since the server is not storing session context, the client must provide the missing details or reference data stored somewhere else.

#### Example: Stateless Counter

In a stateless version of a counter, the server does not remember the current count. Instead, the client keeps track of the count and sends the current value with each request. The server receives that value, increments it, and returns the new result.

This design keeps the server simple. The server only performs a calculation based on the input it receives. It does not store the updated counter in memory after the response is sent.

```javascript
// Client-side
let counter = 0;

button.addEventListener("click", function() {
    fetch('/increment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentCount: counter })
    })
    .then(response => response.json())
    .then(data => {
        counter = data.counter;
        console.log(counter); // e.g., 5
    });
});

// Server-side
app.post("/increment", (req, res) => {
    let newCount = req.body.currentCount + 1;
    // No server storage of newCount
    res.json({ counter: newCount });
});
```

Example request:

```http
POST /increment
Content-Type: application/json

{
  "currentCount": 4
}
```

Example output:

```json
{
  "counter": 5
}
```

In this example, the client sends `currentCount: 4`. The server adds `1` and returns `counter: 5`. After sending the response, the server does not remember that the counter is now `5`.

The client is responsible for storing the updated value:

```javascript
counter = data.counter;
```

This design makes scaling simple because every server can process the request in the same way. If the next request goes to a different server, it does not matter because the current count is included in the request.

Example multi-server flow:

```text
Request 1 with currentCount = 0 → Server A → returns 1
Request 2 with currentCount = 1 → Server B → returns 2
Request 3 with currentCount = 2 → Server C → returns 3
```

Example output:

```json
{
  "counter": 3,
  "stateStoredOn": "client"
}
```

This works because the state is not stored inside any one server. The client carries the current counter value from request to request.

The main limitation is trust and consistency. If the client sends the wrong count, the server has no internal value to compare against. For important data, such as account balances, inventory, or payment totals, the server should not rely only on client-provided state. Stateless designs often use signed tokens, databases, or validation checks when correctness and security matter.

### Common Considerations

There are several universal factors that affect both stateful and stateless applications. Even if an application does not store session state on the server, it still has to deal with networking, storage, databases, authentication, errors, and scaling.

Networking plays a major role because distributed applications must handle timeouts, dropped connections, retries, and partial failures. Storage and filesystem changes also need consistent practices to avoid corruption or conflicting writes. Database interactions must be reliable whether the server itself is holding session data or relying on external storage.

A short formula can help illustrate the overhead difference between stateful and stateless request handling:

```text
T_stateful = T_processing + T_sessionOverhead
T_stateless = T_processing
```

Example calculation:

```text
T_processing = 40ms
T_sessionOverhead = 15ms

T_stateful = 40ms + 15ms
T_stateful = 55ms

T_stateless = 40ms
```

Example output:

```text
Stateful average request time: 55ms
Stateless average request time: 40ms
```

In this simplified example, the stateful request takes longer because the server must load, update, or save session information. In smaller systems, this overhead may not matter much. In high-traffic systems, even a small amount of extra latency can become significant when multiplied across thousands or millions of requests.

### Identifying Stateful vs Stateless Designs

A good way to identify whether a system is stateful or stateless is to ask whether the server remembers user-specific data between requests. If the server stores information such as sessions, shopping carts, user progress, or temporary workflow data, the system is likely stateful. If each request contains everything needed for processing, the system is closer to stateless.

A stateful server might keep a session object or memory of user interactions. A stateless server usually expects the client to provide the necessary data every time. Both approaches can be valid, but they create different scaling and reliability trade-offs.

Below is an illustration of a web application that implements a simple counter, with the server either remembering or forgetting the current count between requests:

```text
+-----------------------------+
|                             |
|       Web Application       |
|        (Counter App)        |
|                             |
+-----------------------------+
              ||
              || User Interface
              \/
+-----------------------------+
|                             |
|        +------------+       |
|        |   Button   |       |
|        +------------+       |
|                             |
|        Count Display        |
|          [  0  ]            |
|                             |
+-----------------------------+
              ||
              || Button Click
              \/
+-----------------------------+
|                             |
|       Server Handling       |
|                             |
|   Increment & Store Count   |
|   (Stateful) or Respond     |
|   with Increment (Stateless)|
|                             |
+-----------------------------+
              ||
              || Update & Display
              || New Count
              \/
+-----------------------------+
|                             |
|        Count Display        |
|          [  1  ]            |
|                             |
+-----------------------------+
```

Example stateful request:

```http
POST /increment
Cookie: session_id=abc123
```

Example stateful output:

```json
{
  "counter": 1,
  "storedOn": "server",
  "sessionId": "abc123"
}
```

In the stateful version, the server uses the session ID to find the stored counter value. It increments the value, saves the updated count, and returns the new result.

Example stateless request:

```http
POST /increment
Content-Type: application/json

{
  "currentCount": 0
}
```

Example stateless output:

```json
{
  "counter": 1,
  "storedOn": "client"
}
```

In the stateless version, the client sends the current count with the request. The server increments the number and returns the result, but it does not remember the updated value after the response is sent.

A stateful approach has the server track the count internally. A stateless approach relies on the client to send the current count with every interaction. The best choice depends on scalability requirements, workflow complexity, reliability needs, and overall system design.

### Token-Based Authentication vs Server-Side Sessions

One of the most common decisions related to state is how to handle authentication. After a user logs in, the application needs a way to identify that user on later requests. The two common approaches are **server-side sessions** and **token-based authentication**, often using JWTs.

Server-side sessions are stateful because the server stores session information after login. Token-based authentication is usually considered stateless because the client stores a signed token and sends it with every request.

Both approaches are widely used. Server-side sessions are often simpler to revoke and control centrally. Token-based authentication is often easier to scale across many server instances because the server can validate the token without looking up a session record.

#### Server-Side Sessions — Stateful

With server-side sessions, the server creates a session object after the user logs in. This session might be stored in memory, a database, or a cache such as Redis. The client receives a session ID, usually as a cookie, and sends that session ID with future requests.

The session ID itself does not usually contain all user data. Instead, it acts like a key. The server uses that key to look up the actual session information.

```text
Client                              Server
  |   POST /login                    |
  |   {user, password}               |
  | -------------------------------->|
  |                                  | Creates session in memory/store
  |   Set-Cookie: session_id=abc123  |
  | <--------------------------------|
  |                                  |
  |   GET /profile                   |
  |   Cookie: session_id=abc123      |
  | -------------------------------->|
  |                                  | Looks up session abc123
  |   {name: "Alice", role: "admin"} |
  | <--------------------------------|
```

Example login request:

```http
POST /login
Content-Type: application/json

{
  "user": "alice",
  "password": "correct-password"
}
```

Example login output:

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; HttpOnly; Secure

{
  "message": "Login successful"
}
```

Example profile request:

```http
GET /profile
Cookie: session_id=abc123
```

Example profile output:

```json
{
  "name": "Alice",
  "role": "admin"
}
```

In this example, the server uses `session_id=abc123` to look up Alice’s session. If Alice logs out, the server can delete that session, immediately revoking access.

This approach makes revocation straightforward because the server controls the session record. The trade-off is that all server instances need access to the same session storage. Without shared storage, a request routed to a different server may fail because that server does not know about the session.

#### Token-Based Authentication — Stateless

With token-based authentication, the server issues a signed token after login. A common format is a JWT, or JSON Web Token. The token contains claims such as the user ID, role, and expiration time. The client stores the token and sends it in the `Authorization` header on future requests.

The server validates the token signature to confirm that it was issued by a trusted source and has not been modified. Because the token is self-contained, the server usually does not need to look up session data.

```text
Client                              Server
  |   POST /login                    |
  |   {user, password}               |
  | -------------------------------->|
  |                                  | Signs JWT with secret key
  |   {token: "eyJhbG..."}           |
  | <--------------------------------|
  |                                  |
  |   GET /profile                   |
  |   Authorization: Bearer eyJhbG...|
  | -------------------------------->|
  |                                  | Verifies JWT signature
  |   {name: "Alice", role: "admin"} |
  | <--------------------------------|
```

Example login request:

```http
POST /login
Content-Type: application/json

{
  "user": "alice",
  "password": "correct-password"
}
```

Example login output:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Example profile request:

```http
GET /profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Example profile output:

```json
{
  "name": "Alice",
  "role": "admin"
}
```

In this example, the server does not need to find a session record. It verifies the token signature and reads the claims inside the token. This makes horizontal scaling easier because any server instance with the correct verification key can process the request.

The main drawback is revocation. If a token is valid until a future expiration time, the server may continue accepting it unless additional infrastructure is used. Common solutions include short-lived access tokens, refresh tokens, token blocklists, or rotating signing keys.

| Aspect             | Server-Side Sessions                             | Token-Based Authentication                          |
| ------------------ | ------------------------------------------------ | --------------------------------------------------- |
| State storage      | Server, memory, database, or cache               | Client stores the token                             |
| Scalability        | Requires shared session store                    | Scales easily across instances                      |
| Revocation         | Simple because the server can delete the session | Requires blocklist, short expiry, or token rotation |
| Payload size       | Small cookie containing a session ID             | Larger header because the token carries claims      |
| Offline validation | Not possible without session lookup              | Server can verify token without a session store     |

### Distributed State Management

When stateful behavior is necessary in a distributed system, state must be accessible to all instances that may handle a request. This is important because modern applications often run multiple copies of the same service behind a load balancer.

If state is stored only in one server’s memory, users may experience inconsistent behavior when requests are routed to different instances. Distributed state management solves this by moving important state into shared systems such as databases, caches, queues, or event logs.

Several strategies can address this problem, including external session stores, sticky sessions, and designing microservices to keep state in dedicated data stores.

#### External Session Stores

An external session store keeps session data outside the application server. Common choices include Redis, Memcached, or a database. This allows any server instance to read or update the same session.

```text
+----------+      +----------+      +----------+
| Server 1 |      | Server 2 |      | Server 3 |
+-----+----+      +-----+----+      +-----+----+
      |                 |                 |
      +--------+--------+--------+--------+
               |                 |
         +-----+-----+    +-----+------+
         |   Redis   |    |  Database  |
         | Sessions  |    | Persistent |
         +-----------+    +------------+
```

Example request:

```http
GET /cart
Cookie: session_id=abc123
```

Example session lookup in Redis:

```text
GET session:abc123
```

Example session data:

```json
{
  "userId": "user-1",
  "cartItems": [
    {
      "productId": "book-1",
      "quantity": 2
    }
  ],
  "expiresAt": "2026-04-25T18:00:00Z"
}
```

Example API output:

```json
{
  "cartItems": [
    {
      "productId": "book-1",
      "quantity": 2
    }
  ],
  "totalItems": 2
}
```

Redis provides fast reads and writes with built-in expiration, making it a popular choice for session storage. The trade-off is that the system now depends on additional infrastructure. If Redis becomes unavailable, session-based features may fail unless the system has replication, fallback behavior, or graceful degradation.

#### Sticky Sessions

Sticky sessions, also called session affinity, tell the load balancer to route requests from the same client to the same server instance. This allows the server to keep session data locally without using a shared session store.

Example routing flow:

```text
Request 1 from Client A → Load Balancer → Server 1
Request 2 from Client A → Load Balancer → Server 1
Request 3 from Client A → Load Balancer → Server 1
```

Example output:

```json
{
  "client": "Client A",
  "routedTo": "Server 1",
  "sessionFound": true
}
```

Sticky sessions can be simple to implement, but they reduce flexibility. If Server 1 becomes overloaded, the load balancer may still need to keep sending Client A’s requests to it. If Server 1 crashes, any sessions stored only in its memory may be lost.

Example failure scenario:

```text
Client A session stored on Server 1
Server 1 crashes
Client A routed to Server 2
Server 2 cannot find session
```

Example error output:

```json
{
  "error": "Session not found",
  "code": "SESSION_LOST"
}
```

Sticky sessions can work for smaller systems, but they are usually less resilient than using a shared session store. They avoid one kind of complexity but introduce another: the health and capacity of individual servers become more tightly tied to specific users.

#### State in Microservices

Microservice architectures often mix stateful and stateless patterns. API gateways and edge services are often designed to be stateless, especially when they use token-based authentication. Domain services, such as order services, payment services, or inventory services, may be stateful because they manage important business data.

The key principle is to keep application services as stateless as possible and place durable state in dedicated data stores. This makes services easier to deploy, scale, restart, and replace. If a service crashes, another instance can continue processing requests using the same database, cache, or event stream.

Example microservices layout:

```text
Client
  |
  v
API Gateway
  |
  +--> User Service --------> User Database
  |
  +--> Order Service -------> Order Database
  |
  +--> Inventory Service ---> Inventory Database
  |
  +--> Notification Service -> Message Queue
```

Example order request:

```http
POST /orders
Authorization: Bearer eyJhbG...
Content-Type: application/json

{
  "userId": "user-1",
  "items": [
    {
      "productId": "book-1",
      "quantity": 2
    }
  ]
}
```

Example order output:

```json
{
  "orderId": "order-789",
  "status": "created",
  "items": [
    {
      "productId": "book-1",
      "quantity": 2
    }
  ]
}
```

In this example, the API gateway can remain stateless by validating the token and forwarding the request. The order service stores durable order state in the order database. The inventory service may update stock levels in its own database. The notification service may publish messages to a queue.

Important design principles include:

* Stateless services are easier to deploy, scale, and replace.
* State that must persist belongs in a dedicated data store with proper replication and backups.
* Event-driven patterns, such as event sourcing and CQRS, can reduce the need for shared mutable state by recording changes as immutable events.

Example event-driven output:

```json
{
  "eventType": "OrderCreated",
  "orderId": "order-789",
  "userId": "user-1",
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Instead of relying on many services to share the same mutable state, an event-driven system records what happened. Other services can react to those events and build their own views of the data. This can improve scalability and reliability, but it also introduces complexity around event ordering, retries, and eventual consistency.
