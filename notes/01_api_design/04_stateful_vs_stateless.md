## Stateful vs Stateless Applications

The terms stateful and stateless pertain to the architecture of an application, specifically regarding how it handles and stores data over time or across interactions.

## Stateful Applications

Stateful applications maintain a record of previous interactions or events that can affect the behaviour of future requests. This stored data, or "state", can be used to keep track of user interactions, transactions, configurations, etc.

### Pros of Stateful Applications

- They are often more intuitive to program, as stateful applications can leverage stored data to provide context to an incoming request.
- Capable of managing complex states across various interactions, making them suitable for complex workflows.
- The user experience is generally more cohesive, as the application can maintain context across multiple requests.

### Cons of Stateful Applications

- Scaling is challenging as every instance of the application needs to share and maintain the same state information.
- If a crash occurs, the recovery can be difficult or impossible without the saved state, leading to potential data loss and inconsistent behaviour.

### Example
In a stateful application, the server remembers the counter's state. Each time the button is clicked, the client does not need to send the current count because the server, already aware of the current count, increments it and sends back the new value. This process represents a stateful approach as the server retains information about the current state of the counter between requests.

Here is a pseudo-code example for a stateful application:

```javascript
// Client-side
button.addEventListener("click", function() {
    sendToServer();
});

// Server-side
let counter = 0;
server.on("request", function(request) {
    counter++;
    response.send({counter: counter});
});
```

In the first scenario, the server does not hold any data between requests and treats each request as an isolated transaction, making it a stateless application. In contrast, in the second scenario, the server maintains the counter's state across requests, making it a stateful application

## Stateless Applications

Stateless applications, in contrast, do not retain information from one request to another. Each request is processed independently of others.

### Pros of Stateless Applications

- Highly scalable as each request is handled independently. This makes it easy to distribute the load across multiple servers.
- They can recover from failures more gracefully, as there's no dependency on previous states or sessions. If a server fails, a request can simply be redirected to another server.
- Stateless applications are idempotent, meaning that making the same request multiple times will yield the same result.

### Cons of Stateless Applications

- Managing complex workflows can be difficult as stateless applications cannot inherently maintain context across requests.
- Coding can be more challenging since each request must carry all the information needed for its processing.

## Common Issues and Considerations

Regardless of whether an application is stateful or stateless, there are a few universal considerations:

- **Network connections**: Both stateful and stateless applications often rely on network connections for communication and data transfer.
- **Filesystem changes**: Modifications to the filesystem are common in many applications for storing or retrieving data.
- **Database tasks**: Most applications interact with databases to persist and fetch data.

### Example

In a stateless application, the server doesn't keep track of the counter's state (its current value). Every time the button is clicked, the client (browser) sends the current count along with the request to increment it. The server increments the received value and sends it back. This process represents a stateless approach as the server doesn't retain any information about previous interactions.

Here is a pseudo-code example for a stateless application:

```javascript
// Client-side
button.addEventListener("click", function() {
    sendToServer(counter);
});

// Server-side
server.on("request", function(request) {
    let newCount = request.body.counter + 1;
    response.send({counter: newCount});
});
```

## Identifying Stateful vs Stateless Applications

To understand the concept of stateful and stateless applications, let's consider a straightforward example: a web-based counter application with a button. Each time a user clicks this button, a counter increases by one, and the webpage displays the updated count.

```
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

### Stateful Application Scenario
In a stateful version of this counter application, the server remembers the count between different requests from the same user. Here's how it works:
1. **User Interaction**: The user clicks the button on the webpage.
2. **Server Processing**: The server receives the click request, increments the counter specific to that user, and stores this updated count in a session or database.
3. **Response**: The server then sends the updated count back to the user's webpage, where it's displayed.
4. **State Management**: The next time the same user clicks the button, the server retrieves the previously stored count, increments it, and continues the cycle.

In this scenario, the application is stateful because the server keeps track of the state (the count) between different interactions with the same user.

### Stateless Application Scenario
Contrast this with a stateless version of the same application:
1. **User Interaction**: The user clicks the button on the webpage.
2. **Server Processing**: The server receives the click request but does not store any state between requests. Instead, it relies on the client to send the current count with each request.
3. **Response**: The server increments the received count and sends it back, but doesn’t store it.
4. **No State Management**: Every time the button is clicked, the client must send the current count along with the request. The server treats each request independently, without knowledge of previous interactions.

In the stateless scenario, the server does not remember the count between requests. Each request is treated as a new, standalone transaction.
