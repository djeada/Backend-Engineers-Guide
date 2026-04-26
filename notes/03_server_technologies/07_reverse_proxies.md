## Reverse Proxies

A reverse proxy is a server that receives incoming requests from external clients and forwards them to one or more internal servers. To the client, the reverse proxy looks like the application server. Behind the scenes, the proxy decides where the request should go.

Reverse proxies are common in modern backend architectures because they provide a single controlled entry point into a system. They can improve load balancing, security, caching, SSL/TLS handling, compression, observability, and routing.

Instead of exposing every backend server directly to the internet, teams place a reverse proxy in front of them. This hides internal server details and allows traffic to be managed centrally.

```text id="axlmmq"
Reverse Proxy in Action

          +----------------------+
          |      Internet        |
          +---------+------------+
                    |
             Incoming Requests
                    v
             +------+------+
             | Reverse     |
             |  Proxy      |
             +------+------+ 
                    |
   Traffic routed to appropriate server
     +------+--------+--------+------+
     |      |        |        |      |
     v      v        v        v      v
 +--------------+  +--------------+  +--------------+
 | Web Server 1 |  | Web Server 2 |  | Web Server 3 |
 +--------------+  +--------------+  +--------------+
```

Example request to the reverse proxy:

```http id="7mc6yp"
GET /dashboard HTTP/1.1
Host: app.example.com
```

Example backend routing result:

```json id="8vh99f"
{
  "clientRequested": "app.example.com/dashboard",
  "reverseProxyRoutedTo": "web-server-2:3000",
  "status": "success"
}
```

The client does not need to know that `web-server-2` handled the request. It only communicates with `app.example.com`.

---

## Comparing Forward and Reverse Proxies

Forward proxies and reverse proxies both sit between two network participants, but they serve different sides of the connection.

A **forward proxy** acts on behalf of clients. It is often used by organizations to filter outbound traffic, cache external resources, or hide client identity from the internet.

A **reverse proxy** acts on behalf of servers. It receives inbound traffic from the internet and forwards it to internal application servers.

| Forward Proxy                                                                | Reverse Proxy                                                                           |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Sits between **clients** and the **internet**.                               | Sits between **external users** and **internal servers**.                               |
| Primarily used for client anonymity, outbound caching, or content filtering. | Primarily used for load balancing, security, caching, and inbound traffic control.      |
| Often used to apply organizational policies or route outbound traffic.       | Often used to protect internal servers, improve performance, and handle SSL offloading. |

Example forward proxy flow:

```text id="wwptqp"
Employee Laptop → Corporate Proxy → Internet Website
```

Example reverse proxy flow:

```text id="91u1iz"
Internet User → Reverse Proxy → Internal App Server
```

Example output:

```json id="spc5hu"
{
  "forwardProxyProtects": "client side",
  "reverseProxyProtects": "server side"
}
```

The key difference is who the proxy represents. A forward proxy represents the client. A reverse proxy represents the server infrastructure.

---

## How a Reverse Proxy Works

A reverse proxy receives client requests, applies routing or policy rules, forwards the request to a backend server, receives the backend response, and returns that response to the client.

The backend server usually sees the reverse proxy as the immediate network peer. The client usually sees only the reverse proxy.

Basic flow:

1. **Request to Proxy**
   The client sends a request, such as `GET /index.html`, to the reverse proxy’s public domain or IP address.

2. **Server Selection**
   The proxy checks its rules, such as path routing, host routing, load balancing, caching, or health status.

3. **Forwarding**
   The proxy forwards the request to a suitable backend server.

4. **Response Return**
   The backend server processes the request and sends the response back to the proxy.

5. **Final Delivery**
   The proxy returns the response to the client.

```text id="n6el9s"
Client -> Reverse Proxy -> Web Server -> Reverse Proxy -> Client
```

Example routing rule:

```text id="gqozpz"
/api/*      -> api-service:3000
/static/*   -> static-server:8080
/admin/*    -> admin-service:4000
```

Example output:

```json id="ak9a77"
{
  "requestPath": "/api/users",
  "selectedBackend": "api-service:3000",
  "proxyAction": "forwarded"
}
```

This allows one public domain to route different paths to different internal services.

---

## Common Use Cases

Reverse proxies are useful because they sit at a strategic point in the request path. Since all inbound traffic passes through them, they can apply performance, security, and routing policies before requests reach backend servers.

---

### I. Load Balancing

Load balancing distributes incoming requests across multiple backend servers. This prevents one server from receiving all traffic while others sit idle.

A reverse proxy can choose a backend using strategies such as round-robin, least connections, random selection, weighted routing, or consistent hashing. It can also remove unhealthy servers from rotation.

Example backend pool:

```text id="1hvimo"
Backend servers:
- web-1: healthy
- web-2: healthy
- web-3: unhealthy
```

Example output:

```json id="vv8i92"
{
  "request": "/api/products",
  "selectedBackend": "web-2",
  "excludedBackends": ["web-3"],
  "reason": "health check failed"
}
```

This improves availability. If one backend fails, the reverse proxy can continue sending traffic to healthy instances.

---

### II. Web Acceleration

Reverse proxies can improve performance by caching, compressing, and optimizing responses before they reach the client.

**Caching** stores frequently requested responses at the proxy. If many users request the same static file or public page, the proxy can serve it directly without contacting the backend.

Example cached response:

```http id="3m0kqd"
HTTP/1.1 200 OK
Content-Type: text/css
X-Cache: HIT

body {
  font-family: Arial;
}
```

**Compression** reduces payload size, lowering bandwidth usage and improving load time.

Example compression header:

```http id="03w0jf"
Content-Encoding: br
```

**SSL/TLS termination** lets the proxy handle HTTPS encryption and decryption. This centralizes certificate management and can reduce work on backend servers.

Example output:

```json id="h6u77i"
{
  "tlsTerminatedAt": "reverse-proxy",
  "backendConnection": "http://api-service:3000",
  "compression": "brotli",
  "cache": "enabled"
}
```

---

### III. Security and Observability

A reverse proxy can hide the internal network structure from external users. Attackers see only the proxy address, not the private IPs of backend servers.

It can also enforce security policies before traffic reaches application code. These policies may include IP blocking, rate limiting, request size limits, WAF rules, bot detection, header validation, and TLS enforcement.

Example blocked request:

```json id="f2eadt"
{
  "clientIp": "203.0.113.50",
  "path": "/login",
  "action": "blocked",
  "reason": "too many failed requests"
}
```

Reverse proxies also centralize logs. Since all requests pass through the proxy, teams can capture request IDs, latency, status codes, client IPs, user agents, and routing decisions in one place.

Example access log:

```json id="n03tl9"
{
  "requestId": "req-123",
  "clientIp": "198.51.100.20",
  "method": "GET",
  "path": "/api/orders",
  "status": 200,
  "upstream": "orders-service:3000",
  "durationMs": 42
}
```

This observability helps teams debug errors, trace traffic, and monitor service health.

---

### IV. SSL Encryption

Reverse proxies often handle SSL/TLS termination. This means the client connects to the proxy over HTTPS, and the proxy forwards the request to the backend using HTTP or HTTPS.

Centralized TLS termination simplifies certificate renewal and configuration. Instead of installing certificates on every backend service, teams can manage them at the proxy layer.

Example HTTPS request:

```http id="2bsuri"
GET /profile HTTP/1.1
Host: app.example.com
Protocol: HTTPS
```

Example proxy behavior:

```json id="u5nhax"
{
  "clientToProxy": "HTTPS",
  "proxyToBackend": "HTTP",
  "certificateManagedAt": "reverse-proxy"
}
```

In higher-security environments, the proxy-to-backend connection may also use HTTPS or mutual TLS.

Example stricter setup:

```json id="0guf6d"
{
  "clientToProxy": "HTTPS",
  "proxyToBackend": "mTLS",
  "backendAuthentication": "required"
}
```

SSL offloading can improve operational simplicity, but teams must ensure internal network traffic is protected according to the sensitivity of the system.

---

## Preserving Client and Request Metadata

Without extra headers, the backend usually sees the reverse proxy as the immediate client. This is useful for network isolation, but application code may still need the original client IP, public host, or original protocol.

Reverse proxies commonly add forwarding headers to preserve this metadata.

* **`X-Forwarded-For`** carries the original client IP chain.
* **`X-Forwarded-Proto`** indicates whether the original request used HTTP or HTTPS.
* **`X-Forwarded-Host`** preserves the public hostname the client used.
* **`Forwarded`** is the standardized alternative to the `X-Forwarded-*` headers.

Example proxied request:

```http id="sgdw45"
GET /profile HTTP/1.1
Host: internal-app:3000
X-Forwarded-For: 198.51.100.20, 10.0.0.5
X-Forwarded-Proto: https
X-Forwarded-Host: app.example.com
```

Example backend interpretation:

```json id="tyfid8"
{
  "originalClientIp": "198.51.100.20",
  "originalProtocol": "https",
  "originalHost": "app.example.com"
}
```

Backends should trust these headers only when the request comes from known proxies or load balancers. If the backend accepts these headers from any client, attackers can spoof IP addresses or protocols.

Example spoofing risk:

```http id="ddtuhm"
X-Forwarded-For: 127.0.0.1
```

Example safe policy:

```json id="o5w1gj"
{
  "trustForwardedHeadersOnlyFrom": ["10.0.0.5", "10.0.0.6"],
  "publicClientsCannotSetTrustedForwardedHeaders": true
}
```

---

## Example Nginx Configuration

Nginx is commonly used as a reverse proxy. The following configuration listens on HTTPS, terminates TLS, forwards requests to an internal service, and preserves useful request metadata.

```nginx id="g0a2o0"
server {
    listen 443 ssl;
    server_name app.example.com;

    ssl_certificate     /etc/ssl/certs/app.crt;
    ssl_certificate_key /etc/ssl/private/app.key;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

Example request:

```http id="ohgngb"
GET /api/status HTTP/1.1
Host: app.example.com
```

Example backend response:

```json id="sd4ba7"
{
  "status": "ok",
  "service": "node-api"
}
```

Example proxy access log:

```text id="4s6uy3"
198.51.100.20 - GET /api/status 200 upstream=127.0.0.1:3000 time=12ms
```

This setup terminates TLS at the proxy, forwards requests to an internal service, and preserves metadata that the backend may need for redirects, logging, and audit trails.

---

## Operational Considerations

Running a reverse proxy in production requires careful attention to health checks, retries, timeouts, caching, long-lived connections, and high availability.

### Health Checks and Failover

Reverse proxies often check whether backend servers are healthy. If a backend fails, the proxy stops sending traffic to it.

Example health check output:

```json id="nqsyd0"
{
  "backend": "api-3",
  "health": "unhealthy",
  "action": "removed_from_rotation"
}
```

### Retries and Timeouts

Timeouts prevent requests from waiting forever. Retries can reduce user-facing failures, but they must be used carefully. Retrying unsafe operations such as non-idempotent `POST` requests can accidentally create duplicate orders, payments, or records.

Example retry policy:

```json id="2ys9tv"
{
  "retryOn": ["connection_error", "timeout"],
  "retryMethods": ["GET", "HEAD"],
  "avoidRetryMethods": ["POST", "PATCH", "DELETE"]
}
```

### Caching

A reverse proxy can cache static or slowly changing responses. This reduces latency and protects backends during traffic spikes.

Example cache result:

```json id="66msw3"
{
  "path": "/assets/app.js",
  "cacheStatus": "HIT",
  "originContacted": false
}
```

### WebSockets and Streaming

WebSockets and streaming responses require explicit proxy configuration. Otherwise, the proxy may close long-lived connections too early.

Example WebSocket routing output:

```json id="3a3wq2"
{
  "path": "/socket",
  "upgrade": "websocket",
  "connection": "upgraded",
  "timeoutPolicy": "long-lived"
}
```

### High Availability

Because the reverse proxy is a critical entry point, production systems should not rely on only one proxy instance. Teams often run multiple proxy instances behind DNS failover, anycast, cloud load balancers, or another high-availability layer.

Example HA output:

```json id="84hd4r"
{
  "reverseProxyInstances": 3,
  "failover": "enabled",
  "singlePointOfFailure": false
}
```

---

## Types of Reverse Proxies

Reverse proxies can be software-based, hardware-based, or cloud-based. The right option depends on scale, budget, operational model, performance needs, and team expertise.

---

### I. Software-Based

Software reverse proxies are installed and configured on general-purpose servers or containers.

Examples include:

* Nginx
* Apache HTTP Server
* HAProxy
* Envoy
* Traefik
* Caddy

Characteristics:

* **Flexible**: Highly configurable through files, APIs, modules, or service discovery.
* **Open Source Options**: Many tools have large communities and strong documentation.
* **Scalable**: Suitable for small applications and high-traffic systems when configured correctly.

Example output:

```json id="ysot94"
{
  "type": "software_reverse_proxy",
  "example": "Nginx",
  "strength": "flexible and widely used"
}
```

---

### II. Hardware-Based

Hardware reverse proxies are dedicated appliances from vendors such as F5, Citrix, or Cisco. They are often used in enterprise data centers.

Characteristics:

* **Specialized**: Dedicated hardware and optimized features.
* **High Performance**: Useful for environments needing very high throughput or specialized networking.
* **Advanced Features**: May include SSL acceleration, content switching, WAF capabilities, and enterprise support.
* **Costly**: Usually more expensive than software-based options.

Example output:

```json id="kgijz1"
{
  "type": "hardware_reverse_proxy",
  "bestFor": "enterprise data centers with specialized performance or support requirements"
}
```

---

### III. Cloud-Based Reverse Proxies

Cloud-based reverse proxies are managed services that sit in front of applications. They often combine load balancing, TLS termination, CDN caching, DDoS protection, WAF features, and global routing.

Examples include:

* AWS Application Load Balancer or Elastic Load Balancing
* Google Cloud Load Balancing
* Azure Application Gateway or Front Door
* Cloudflare
* Akamai
* Fastly

Characteristics:

* **Scalable**: Capacity can grow without managing physical hardware.
* **Global**: Edge locations can reduce latency for users around the world.
* **Low Maintenance**: The provider handles much of the infrastructure, patching, and availability.

Example output:

```json id="ju24t7"
{
  "type": "cloud_reverse_proxy",
  "features": ["global edge routing", "TLS termination", "DDoS protection", "caching"],
  "maintenance": "managed by provider"
}
```

---

## Security Implications

Reverse proxies can improve security, but they also become highly sensitive infrastructure. If the proxy is misconfigured, unavailable, or compromised, the entire application may be affected.

---

### I. Security Benefits

Reverse proxies reduce direct exposure of backend servers. External clients connect to the proxy, while internal servers can remain on private networks.

Security benefits include:

* **Hides Backend Servers**: Attackers see only the proxy’s address, not private backend IPs.
* **Traffic Filtering**: WAF rules can block SQL injection, XSS attempts, suspicious paths, or malformed requests.
* **DDoS Mitigation**: Proxies can throttle, challenge, block, or absorb malicious traffic.
* **Centralized TLS Policy**: Strong TLS settings can be enforced at one entry point.
* **Rate Limiting**: Abusive clients can be slowed or blocked before reaching application servers.

Example WAF block:

```json id="q0nseo"
{
  "action": "blocked",
  "reason": "SQL injection pattern detected",
  "path": "/search",
  "clientIp": "203.0.113.50"
}
```

---

### II. Potential Risks

Reverse proxies also introduce risks.

* **Single Point of Failure**: If the proxy goes down and no redundancy exists, the whole site may become unavailable.
* **Misconfiguration**: Incorrect routing, weak TLS settings, open admin panels, or overly permissive headers can create vulnerabilities.
* **Trust Issues**: If TLS terminates at the proxy, the proxy can see unencrypted request data.
* **Header Spoofing**: Backends may incorrectly trust client-supplied `X-Forwarded-*` headers.
* **Cache Leaks**: Misconfigured caching may serve private data to the wrong user.

Example cache misconfiguration risk:

```json id="tjzxmz"
{
  "path": "/account",
  "problem": "private user page cached publicly",
  "impact": "one user may receive another user's data"
}
```

Careful configuration, testing, and monitoring are required to prevent these issues.

---

### III. Integrating with Other Security Tools

Reverse proxies work best as part of a layered security system. They should be combined with firewalls, WAFs, intrusion prevention, identity-aware access controls, logging, and regular patching.

Examples:

* **Firewalls** restrict which networks can reach the proxy and backend servers.
* **WAFs** inspect HTTP traffic and block common attack patterns.
* **Intrusion Prevention Systems** detect and block suspicious network behavior.
* **Regular Updates** ensure known vulnerabilities in proxy software are patched.
* **Centralized Logging** helps investigate incidents.

Example layered security output:

```json id="emd6af"
{
  "firewall": "enabled",
  "waf": "enabled",
  "reverseProxy": "nginx",
  "tls": "enforced",
  "logs": "centralized",
  "patching": "scheduled"
}
```

A reverse proxy is not a complete security solution by itself, but it is an important control point. When configured well, it improves performance, protects backend servers, and gives teams a powerful place to manage inbound traffic.
