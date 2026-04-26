## Web Server Overview

Backend engineers are responsible for setting up and maintaining servers that host web applications, APIs, background jobs, and databases. A web server is not just a machine that returns files. In modern systems, it may also route traffic, terminate HTTPS, proxy requests to application services, enforce security rules, cache responses, and collect logs or metrics.

A solid understanding of server management helps backend engineers build systems that are reliable, secure, and scalable. Good server design affects how quickly users receive responses, how safely data is protected, how easily applications can grow, and how quickly teams can recover from failures.

### Client-Server Architecture

Client-server architecture is the foundation of most modern networked systems. In this model, a **client** requests a service, and a **server** provides that service. The client might be a web browser, mobile app, command-line tool, IoT device, or another backend service. The server listens for requests, processes them, and returns responses.

This model separates responsibilities. The client focuses on user interaction or request initiation, while the server manages business logic, storage, authentication, and communication with other systems.

```text
          +-----------+            +-----------+
          |  Client 1 |            |  Client 2 |
          +-----+-----+            +-----+-----+
                ^                        ^
                |                        |
                |  Request/Response      |  Request/Response
                |                        |
                v                        ^
          +-----+-----+            +-----+-----+
          |           |            |           |
          |           +------------>           |
          |  Server   <------------+  Server   |
          |           |            |           |
          |           |            |           |
          +-----+-----+            +-----+-----+
                ^                        ^
                |                        |
                v                        ^
          +-----+-----+            +-----+-----+
          |  Client 3 |            |  Client 4 |
          +-----------+            +-----------+
```

Example request:

```http
GET /products/123 HTTP/1.1
Host: api.example.com
Accept: application/json
```

Example output:

```json
{
  "id": 123,
  "name": "Wireless Keyboard",
  "price": 49.99,
  "inStock": true
}
```

In this example, the client asks the server for product data. The server processes the request, retrieves the product, and returns a JSON response.

#### 1. Client

A client sends requests for data or services. In a web application, the client is often a browser. In a mobile application, the client may be an iOS or Android app. In backend systems, one service can also act as a client when it calls another service.

Clients typically communicate with servers using protocols such as HTTP, HTTPS, FTP, SMTP, WebSockets, or gRPC. The protocol determines how requests and responses are structured.

Example client types:

```text
Browser → requests HTML, CSS, JavaScript, and API data
Mobile App → requests API data
Backend Service → requests data from another service
IoT Device → sends sensor readings to a server
```

Example output:

```json
{
  "clientTypes": ["browser", "mobile_app", "backend_service", "iot_device"],
  "commonProtocol": "HTTPS"
}
```

#### 2. Server

A server receives and processes client requests. It may return a static file, execute application logic, query a database, validate authentication, or forward the request to another service.

Different types of servers perform different roles. A web server may serve pages or proxy API requests. A database server stores and retrieves structured data. A mail server sends and receives email. A cache server stores frequently accessed data for faster retrieval.

Example server response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Request processed successfully"
}
```

This shows the server returning a successful response after handling the client request.

#### 3. Communication

Communication between clients and servers relies on a network, often the internet. The request travels from the client through routers, proxies, load balancers, and firewalls before reaching the server.

Common protocols include:

* **HTTP/HTTPS** for web traffic and APIs.
* **FTP/SFTP** for file transfer.
* **SMTP** for sending email.
* **WebSockets** for real-time bidirectional communication.
* **gRPC** for efficient service-to-service communication.

Example communication flow:

```text
Client → DNS Lookup → Load Balancer → Web Server → App Server → Database
```

Example output:

```json
{
  "requestPath": [
    "client",
    "dns",
    "load_balancer",
    "web_server",
    "application_server",
    "database"
  ],
  "status": "completed"
}
```

### Architecture Patterns

Applications can be organized in different architectural patterns. The right pattern depends on system size, traffic, security requirements, team structure, and complexity.

Simple applications may use two tiers. More complex applications often use three-tier or multi-tier architectures so that each part of the system can scale and evolve independently.

#### Two-Tier Architecture

In a two-tier architecture, the client communicates directly with the server or database layer. This pattern is simple and can work well for small systems, internal tools, or early prototypes.

```text
+--------+       +------------------+
| Client |  <--> |    Server (DB)   |
+--------+       +------------------+
```

Example request:

```text
Client sends query directly to server/database layer.
```

Example output:

```json
{
  "architecture": "two-tier",
  "benefit": "simple setup",
  "limitation": "harder to scale and secure as complexity grows"
}
```

The main advantage is simplicity. The main drawback is that business logic, data access, and presentation concerns may become tightly coupled.

#### Three-Tier Architecture

A three-tier architecture separates the system into presentation, application, and data layers. The client handles presentation. The application server handles business logic. The database stores and retrieves data.

```text
+--------+       +------------------+       +------------------+
| Client |  <--> |   App Server     | <-->  |   Database       |
+--------+       +------------------+       +------------------+
```

Example flow:

```text
Client requests order details.
App server validates the request.
Database returns order records.
App server formats the response.
Client receives JSON data.
```

Example output:

```json
{
  "orderId": "order-789",
  "status": "shipped",
  "source": "three-tier architecture"
}
```

This pattern improves organization and security. The database does not need to be exposed directly to clients, and the application layer can enforce business rules.

#### N-Tier or Multi-Tier Architecture

N-tier architecture adds more layers, such as API gateways, caching systems, message queues, microservices, search services, and specialized business logic services.

```text
          +--------+
          | Client |
          +---+----+
              |
              v
   +-------------------+        +-------------------+
   |  Web Tier (API)   |  <-->  |  Business Logic   |
   +--------+----------+        +---------+---------+
             |                          |
             v                          v
   +-------------------+       +--------------------+
   |  Caching / Queue  |       |  Database / Storage|
   +-------------------+       +--------------------+
```

Example output:

```json
{
  "architecture": "n-tier",
  "components": [
    "api_gateway",
    "application_service",
    "cache",
    "message_queue",
    "database"
  ],
  "benefit": "each layer can scale independently"
}
```

Multi-tier systems are more flexible and scalable, but they also introduce more operational complexity. Teams must monitor more components, handle network failures between services, and keep deployments coordinated.

### Advantages

Client-server architecture offers several important benefits for modern applications.

1. **Scalability** Servers can be scaled vertically with more CPU and memory or horizontally by adding more server instances.
2. **Maintenance** Backend services can be updated without requiring every client to be reinstalled, especially when clients communicate through stable APIs.
3. **Security** Data, authentication, and access control can be managed centrally on the server.
4. **Resource Sharing** Server hardware, databases, caches, and application logic can be shared by many clients.

Example output:

```json
{
  "advantages": {
    "scalability": "multiple clients can be served concurrently",
    "maintenance": "backend updates can be centralized",
    "security": "access control can be enforced server-side",
    "resourceSharing": "shared infrastructure improves efficiency"
  }
}
```

### Disadvantages

Client-server architecture also introduces risks and trade-offs.

1. **Dependency** If the server is down, clients may not be able to use the application.
2. **Network Dependency** Clients need stable network connections to communicate with the server.
3. **Congestion** High traffic can overwhelm the server if it is not scaled properly.

Example failure output:

```json
{
  "error": "Service unavailable",
  "code": "SERVER_OVERLOADED",
  "suggestion": "retry later"
}
```

This type of error can happen when too many clients send requests and the server does not have enough capacity to process them.

### Server Types

Servers can be provisioned in different ways depending on performance requirements, budget, control, scalability, and operational responsibility.

The three common options are dedicated servers, virtual private servers, and cloud servers.

#### 1. Dedicated Servers

A dedicated server is a physical machine assigned to one application, organization, or customer. It provides strong performance isolation because the hardware is not shared with unrelated workloads.

Dedicated servers are useful when an application needs predictable performance, full hardware control, or specialized configurations. The trade-off is cost and maintenance responsibility.

Example output:

```json
{
  "serverType": "dedicated",
  "control": "high",
  "cost": "high",
  "bestFor": "performance-sensitive or specialized workloads"
}
```

#### 2. Virtual Private Servers

A VPS is a virtualized portion of a physical server. Multiple VPS instances may run on the same physical hardware, but each has its own operating system, resources, and configuration.

A VPS is often more affordable than a dedicated server while still giving developers control over the environment. It is a common choice for small to medium applications.

Example output:

```json
{
  "serverType": "vps",
  "control": "moderate",
  "cost": "moderate",
  "bestFor": "small to medium applications"
}
```

#### 3. Cloud Servers

Cloud servers are provided by platforms such as AWS, Azure, Google Cloud, DigitalOcean, or similar providers. They can be created, resized, replicated, and removed through dashboards, APIs, or infrastructure-as-code tools.

Cloud servers are flexible and scalable. They support pay-as-you-go pricing, managed databases, load balancers, autoscaling, object storage, monitoring, and many other services. The trade-off is that costs can grow quickly if usage is not monitored.

```text
      +-----------+
      |  Client 1 |
      +-----+-----+
            |
            | HTTP Request
            v
+-----------------------+
|      Web Server       |
|-----------------------|
| - Hosts Web Pages     |
| - Processes Requests  |
| - Sends Responses     |
+-----------------------+
            ^
            | HTTP Response
            |
      +-----+-----+
      |  Client 2 |
      +-----------+
```

Example output:

```json
{
  "serverType": "cloud",
  "scalability": "high",
  "pricing": "usage-based",
  "bestFor": "applications that need flexible capacity"
}
```

### Operating Systems

A server operating system provides the base environment for running applications, managing files, controlling users, securing network access, and installing software.

The two most common categories are Linux-based server operating systems and Windows Server.

#### Linux

Linux distributions such as Ubuntu, Debian, Rocky Linux, AlmaLinux, and CentOS Stream are widely used in server environments. Linux is popular because it is stable, secure, scriptable, and supported by a large open-source ecosystem.

Linux servers are often managed through the command line. Tools such as `ssh`, `systemctl`, `journalctl`, `ufw`, `nginx`, `docker`, and package managers are common in day-to-day operations.

Example command:

```bash
sudo systemctl status nginx
```

Example output:

```text
nginx.service - A high performance web server
   Active: active (running)
```

This output indicates that the Nginx service is running successfully.

#### Windows Server

Windows Server is often used for applications built around the Microsoft ecosystem, such as .NET applications, Active Directory, Microsoft SQL Server, IIS, and Windows-based enterprise tools.

It provides graphical administration tools as well as PowerShell automation. It is a strong choice when organizations already rely heavily on Microsoft infrastructure.

Example PowerShell command:

```powershell
Get-Service W3SVC
```

Example output:

```text
Status   Name    DisplayName
------   ----    -----------
Running  W3SVC   World Wide Web Publishing Service
```

This output shows that the IIS web service is running.

### Server Configuration

A server needs careful configuration before it can reliably host applications. Configuration includes installing required software, opening only necessary ports, setting environment variables, configuring reverse proxies, connecting databases, and enabling logging.

Common server components include:

* **Web Server Software**: Apache, Nginx, Caddy, IIS, or similar tools.
* **Database Servers**: PostgreSQL, MySQL, MongoDB, SQL Server, or others.
* **Caching Systems**: Redis or Memcached for faster data retrieval.
* **Language Runtimes and Frameworks**: Node.js, Python, Ruby, Java, PHP, Go, or .NET.

#### Example Setup: Ubuntu + Nginx + Node.js + MongoDB

This example describes a common deployment pattern for a JavaScript backend application.

1. **Install Ubuntu** Ubuntu provides the operating system and package management tools.
2. **Install Nginx** Nginx serves static files and proxies API requests to the Node.js application.
3. **Install Node.js** Node.js runs the backend application logic or API.
4. **Install MongoDB** MongoDB stores application data.
5. **Configure Firewalls** The firewall allows only required traffic, such as SSH, HTTP, and HTTPS.

Example Nginx reverse proxy configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Example output after testing Nginx configuration:

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

This confirms that the Nginx configuration is valid. After reloading Nginx, requests to `example.com` can be forwarded to the Node.js app running on port `3000`.

### Security

Securing a server is critical because servers are exposed to networks and often handle sensitive data. A misconfigured server can lead to unauthorized access, data leaks, malware installation, service outages, or privilege escalation.

Security should be layered. No single control is enough by itself. Firewalls, encryption, user permissions, updates, monitoring, and intrusion detection all work together.

Common server security practices include:

* **Firewalls**: Use `ufw`, `iptables`, cloud security groups, or network ACLs to restrict traffic.
* **SSL/TLS Certificates**: Use HTTPS to secure client-server communication.
* **User Access Control**: Prefer SSH keys, disable password login where appropriate, and limit administrative access.
* **Regular Updates**: Keep operating system packages and application dependencies patched.
* **Intrusion Detection**: Use tools such as fail2ban, audit logs, or file integrity monitoring.

Example firewall commands:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Example output:

```text
Firewall is active and enabled on system startup
```

Example firewall status:

```text
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

This configuration allows SSH, HTTP, and HTTPS while blocking other unsolicited inbound traffic.

### Performance Tuning

Performance tuning focuses on making the server respond quickly and use resources efficiently. A slow server may be caused by CPU pressure, memory exhaustion, disk I/O bottlenecks, inefficient queries, poor caching, network latency, or overloaded application workers.

Optimization should be guided by metrics rather than guesses. Teams usually monitor CPU, memory, disk, network, request latency, error rates, database query time, and cache hit rates.

Common performance strategies include:

* **Load Balancing**: Distribute requests across multiple servers.
* **Caching**: Store frequently requested data in memory or at the edge.
* **Resource Monitoring**: Use tools like `top`, `htop`, `nmon`, Prometheus, or Grafana.
* **Database Indexing**: Add indexes and optimize queries to reduce database latency.

Example monitoring output:

```text
CPU usage: 72%
Memory usage: 61%
Disk I/O wait: 4%
Requests per second: 850
p95 latency: 180ms
```

Example cache metrics:

```json
{
  "cacheHitRate": "82%",
  "averageResponseTimeBeforeCacheMs": 240,
  "averageResponseTimeAfterCacheMs": 75
}
```

This output suggests that caching is reducing response time significantly.

### Backup and Disaster Recovery

Backup and disaster recovery planning helps protect against data loss and downtime. Servers can fail, databases can become corrupted, files can be deleted accidentally, and deployments can introduce bugs. A recovery plan ensures the system can be restored.

A good backup strategy includes regular backups, secure storage, retention policies, encryption, and restore testing. A backup that has never been tested may not be reliable.

Important practices include:

* **Regular Backups**: Automate database snapshots and file backups.
* **Redundancy**: Use replicas, failover systems, or high-availability clusters.
* **Recovery Testing**: Regularly test restoring backups to verify they work.

Example backup command:

```bash
mongodump --uri="mongodb://localhost:27017/bookstore" --out=/backups/bookstore
```

Example output:

```text
done dumping bookstore.books
done dumping bookstore.users
done dumping bookstore.orders
```

Example restore test output:

```json
{
  "backup": "bookstore-2026-04-25",
  "restoreStatus": "success",
  "recordsVerified": 125000
}
```

This confirms that the backup can actually be restored and validated.

### Automation and CI/CD

Automation helps keep server environments consistent and reduces manual mistakes. Instead of manually repeating setup steps, teams can use scripts, configuration management tools, containers, and CI/CD pipelines.

CI/CD stands for Continuous Integration and Continuous Deployment or Delivery. It helps teams build, test, and deploy code safely and repeatedly.

Common automation approaches include:

* **Scripting**: Use Bash, Python, or PowerShell for routine tasks.
* **Configuration Management**: Use Ansible, Puppet, Chef, or similar tools.
* **Continuous Integration**: Run automated builds and tests with tools such as GitHub Actions, GitLab CI, Jenkins, or CircleCI.
* **Continuous Deployment**: Deploy tested changes to staging or production using controlled workflows.

Example CI pipeline output:

```text
Build: passed
Unit tests: passed
Security scan: passed
Docker image: built
Deployment to staging: successful
```

Example deployment result:

```json
{
  "version": "1.8.4",
  "environment": "staging",
  "status": "deployed",
  "healthCheck": "passing"
}
```

This shows a successful automated deployment where the application was built, tested, deployed, and verified.

### Monitoring and Alerts

Monitoring helps teams detect issues quickly. Alerts notify teams when something requires attention. Without monitoring, failures may only become visible after users complain.

Monitoring should include both infrastructure metrics and application metrics. Infrastructure metrics include CPU, memory, disk, network, and process health. Application metrics include request latency, error rates, throughput, queue depth, database latency, and cache hit rate.

Common tools include:

* **Monitoring Tools**: Prometheus, Grafana, Nagios, Datadog, New Relic, or CloudWatch.
* **Log Management**: ELK Stack, OpenSearch, Loki, Splunk, or centralized cloud logging.
* **Alerts**: Email, SMS, PagerDuty, Slack, or incident management tools.

Example alert rule:

```text
Trigger alert if:
p95 latency > 500ms for 5 minutes
OR
5xx error rate > 2% for 3 minutes
OR
CPU usage > 90% for 10 minutes
```

Example alert output:

```json
{
  "alert": "High API latency",
  "service": "orders-api",
  "p95LatencyMs": 760,
  "duration": "6 minutes",
  "severity": "warning"
}
```

Example log entry:

```json
{
  "timestamp": "2026-04-25T12:00:00Z",
  "level": "error",
  "service": "orders-api",
  "requestId": "req-123",
  "message": "Database timeout while creating order"
}
```

Monitoring and logs work best together. Metrics show that something is wrong, while logs and traces help explain why it is happening. Together, they help teams respond faster and maintain reliable web servers.
