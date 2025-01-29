## Web Server Overview

Backend engineers are responsible for setting up and maintaining servers that host web applications, APIs, and databases. A solid understanding of server management principles is crucial for delivering robust, high-performing, and secure systems.

### Client-Server Architecture

Client-server architecture underpins most modern networked systems and the internet. It describes how clients (which request services) interact with servers (which provide these services).

```
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

1. **Client**  
   - Sends requests for data or services, typically through protocols like HTTP, FTP, or SMTP.  
   - Can be anything from a web browser to a mobile app or IoT device.

2. **Server**  
   - Receives and processes client requests, then returns appropriate responses.  
   - Could be a web server, database server, mail server, etc.

3. **Communication**  
   - Relies on a network (often the internet).  
   - Common protocols include HTTP for web traffic, FTP for file transfer, and SMTP for email.

#### Architecture Patterns

- **Two-Tier Architecture**  
  - Direct communication between client and server.  
  - Suitable for simple setups or smaller user bases.

  ```
  +--------+       +------------------+
  | Client |  <--> |    Server (DB)   |
  +--------+       +------------------+
  ```

- **Three-Tier Architecture**  
  - Separates presentation (client), application (middle layer), and data (database) layers.  
  - Helps in organizing complex applications, enhancing security, and scaling individual layers independently.

  ```
  +--------+       +------------------+       +------------------+
  | Client |  <--> |   App Server     | <-->  |   Database       |
  +--------+       +------------------+       +------------------+
  ```

- **N-Tier (Multi-Tier) Architecture**  
  - Adds more layers, such as separate microservices, caching servers, or specialized business logic layers.  
  - Offers enhanced scalability, flexibility, and maintainability.

  ```
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

#### Advantages

- **Scalability**: Servers can handle many clients concurrently.  
- **Maintenance**: Upgrading back-end services does not disrupt client applications.  
- **Security**: Central control over data and authentication.  
- **Resource Sharing**: Efficient usage of server hardware and software resources.

#### Disadvantages

- **Dependency**: Clients rely on server uptime.  
- **Network Dependency**: Requires stable network connections.  
- **Congestion**: High load can overwhelm the server if not scaled properly.

### Server Types

Servers can be provisioned in different ways depending on performance requirements, budget, and desired control:

1. **Dedicated Servers**  
   - A single physical machine dedicated to one application or client.  
   - High performance, maximum control, but often costlier.

2. **Virtual Private Servers (VPS)**  
   - A virtualized portion of a physical server.  
   - More affordable than dedicated servers, offering reasonable performance and control.

3. **Cloud Servers**  
   - Managed by cloud providers like AWS, Azure, or Google Cloud.  
   - Highly scalable and flexible, pay-as-you-go model.  
   - Cost can vary based on usage and resource consumption.

```
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

### Operating Systems

- **Linux (Ubuntu, CentOS, Debian, etc.)**  
  - Popular in server environments for stability, security, and open-source ecosystem.  
  - Powerful command-line tools, extensive community support.

- **Windows Server**  
  - Chosen for .NET environments or for integrating with other Microsoft services.  
  - Graphical interfaces and Windows-centric tools.

### Server Configuration

To run services effectively, servers require careful setup:

- **Web Server Software**: Apache, Nginx, IIS, or others.  
- **Database Servers**: MySQL, PostgreSQL, MongoDB, etc.  
- **Caching Systems**: Redis or Memcached for faster data retrieval.  
- **Language Runtimes/Frameworks**: Node.js, Python, Ruby, Java, PHP.

#### Example Setup (Ubuntu + Nginx + Node.js + MongoDB)

1. **Install OS**: Start with Ubuntu as the server operating system.  
2. **Install Nginx**: Configure it to serve static files and proxy requests to Node.js.  
3. **Install Node.js**: Run the application logic or API.  
4. **Install MongoDB**: Store and manage application data.  
5. **Configure Firewalls**: Secure traffic, allowing only HTTP/HTTPS and SSH as needed.

### Security

Securing a server is crucial to prevent unauthorized access and data breaches:

- **Firewalls**: Configure iptables or ufw to control network traffic.  
- **SSL/TLS Certificates**: Use HTTPS for secure client-server communication.  
- **User Access Control**: Implement key-based SSH authentication, minimal open ports.  
- **Regular Updates**: Keep system packages and software patched.  
- **Intrusion Detection**: Tools like fail2ban or tripwire to monitor malicious activity.

### Performance Tuning

Optimizing server performance involves balancing resource usage and application demands:

- **Load Balancing**: Use reverse proxies (e.g., HAProxy, Nginx) or load balancers to distribute requests.  
- **Caching**: Implement in-memory caches or content caching to reduce repeated computation.  
- **Resource Monitoring**: Tools like `top`, `htop`, or `nmon` help identify CPU, RAM, or I/O bottlenecks.  
- **Database Indexing**: Proper indexes and query optimization for better query performance.

### Backup and Disaster Recovery

A robust strategy ensures minimal downtime and data loss:

- **Regular Backups**: Automate database snapshots and file backups (daily, weekly).  
- **Redundancy**: Set up replicas or high-availability clusters (e.g., MySQL replication).  
- **Recovery Testing**: Regularly test restoring backups to validate the process.

### Automation and CI/CD

Streamlined development and deployment pipelines keep the server environment consistent and reliable:

- **Scripting**: Use Bash, Python, or Ansible for repetitive admin tasks.  
- **Continuous Integration**: Tools like Jenkins, GitLab CI automate building and testing code changes.  
- **Continuous Deployment**: Deploy updates quickly and safely to staging or production.

### Monitoring and Alerts

Detecting and responding to issues quickly is essential:

- **Monitoring Tools**: Nagios, Prometheus, Grafana for real-time metrics and alerting.  
- **Log Management**: ELK Stack (Elasticsearch, Logstash, Kibana) for centralizing and analyzing logs.  
- **Alerts**: Configure email/SMS/Slack alerts for system anomalies, such as high CPU usage or downtime.
