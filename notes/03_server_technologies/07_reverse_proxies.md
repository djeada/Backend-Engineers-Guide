## Reverse Proxies

A reverse proxy is a special server that receives incoming requests from external clients and forwards them to one or more internal web servers. By acting as an intermediary, it hides the details of the internal network, providing a single entry point that can improve load balancing, security, caching, and overall performance of the back-end servers.

```
ASCII DIAGRAM: Reverse Proxy in Action

          +----------------------+
          |      Internet       |
          +---------+-----------+
                    |
             (Incoming Requests)
                    v
             +------+------+
             | Reverse     |
             |  Proxy      |
             +------+------+ 
                    |
   (Traffic routed to appropriate server)
     +------+--------+--------+------+
     |      |        |        |      |
     v      v        v        v      v
 +---------+--+  +----------+--+  +----------+--+
 | Web Server 1 |  | Web Server 2 |  | Web Server 3 |
 +--------------+  +--------------+  +--------------+
```

1. **Client**: Makes an HTTP/HTTPS request to a domain or IP, not knowing there are multiple servers behind a reverse proxy.  
2. **Reverse Proxy**: Decides which internal server handles the request, often based on load-balancing rules or caching policies.  
3. **Internal Servers**: Process the request and send a response back through the proxy, which then returns it to the client.

### Comparing Forward and Reverse Proxies

| **Forward Proxy**                                         | **Reverse Proxy**                                             |
|-----------------------------------------------------------|----------------------------------------------------------------|
| Sits between **clients** and the **internet**.            | Positioned between **external users** and **internal servers**.|
| **Primarily** used for client anonymity, caching, or content filtering on outbound connections. | **Primarily** used for load balancing, security, caching, and controlling inbound connections. |
| Often used to bypass **geographic restrictions** or apply organizational policies for outbound traffic. | Often used to protect internal servers from direct exposure, enhance performance, and handle SSL offloading. |


### How a Reverse Proxy Works

1. **Request to Proxy**: A client sends a request (e.g., `GET /index.html`) to the reverse proxy’s IP or domain.  
2. **Server Selection**: The proxy checks its rules (like load balancing or caching).  
3. **Forwarding**: The request is routed to a suitable **backend** server (e.g., one with the smallest load).  
4. **Response Return**: The chosen server responds back to the proxy.  
5. **Final Delivery**: The proxy sends the server’s response to the client as if it were from the proxy itself.

```
Client -> Reverse Proxy -> Web Server -> Reverse Proxy -> Client
```

### Common Use Cases

I. Load Balancing

- **Distributes** incoming requests across multiple servers to avoid overloading any one host.  
- Improves **availability** by detecting offline servers and redirecting traffic to healthy ones.

II. Web Acceleration

- **Caching**: Frequently accessed pages or resources can be saved at the proxy for faster delivery.  
- **Compression**: Compresses responses to reduce bandwidth and speed up transmissions.  
- **SSL/TLS Termination**: Proxy handles encryption/decryption, easing the CPU load on web servers.

III. Security and Observability

- **Shielding**: Hides the internal structure and IPs of your server farm.  
- **Attack Mitigation**: Can filter suspicious traffic or block malicious payloads before they reach back-end servers.  
- **Logging and Monitoring**: Consolidates logging and tracking of requests at the proxy level.

IV. SSL Encryption

- **SSL Offloading**: The proxy handles certificate details and SSL encryption, letting back-end servers communicate via plain HTTP.  
- **Easier Certificate Management**: Central place to manage SSL certificates for multiple services.

### Preserving Client and Request Metadata

Without additional headers, the backend usually sees the reverse proxy as the immediate client. That is often desirable for network isolation, but application code still needs a safe way to learn the original request details.

- **`X-Forwarded-For`**: Carries the client IP chain.
- **`X-Forwarded-Proto`**: Indicates whether the original request used HTTP or HTTPS.
- **`X-Forwarded-Host`**: Preserves the public hostname the client used.
- **`Forwarded`**: Standardized alternative to the `X-Forwarded-*` family.

Backends should trust these headers only when requests come from known proxies or load balancers; otherwise, clients can spoof them.

### Example Nginx Configuration

```nginx
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

This setup terminates TLS at the proxy, forwards requests to an internal service, and preserves the metadata that the backend commonly needs for redirects, logging, and audit trails.

### Operational Considerations

- **Health Checks and Failover**: Reverse proxies often probe backends and stop routing traffic to unhealthy instances.
- **Retries and Timeouts**: Conservative retry rules reduce user-facing failures but must avoid replaying unsafe operations such as non-idempotent `POST` requests.
- **Caching**: A proxy can cache static or slowly changing responses, which reduces latency and shields backends from spikes.
- **WebSockets and Streaming**: Long-lived connections require explicit configuration so the proxy does not close them prematurely.
- **High Availability**: Because the proxy is a critical entry point, production systems often run multiple proxy instances behind DNS failover or another load balancer.

### Types of Reverse Proxies

I. Software-Based

- **Examples**: Nginx, Apache HTTP Server, HAProxy, Envoy.  
- **Characteristics**:
  - **Flexible**: Highly configurable via modules or directives.  
  - **Open Source**: Large community support and extensive documentation.  
  - **Scalable**: Can handle small to medium sites as well as high-traffic applications.

II. Hardware-Based

- **Appliances** from F5, Citrix, or Cisco.  
- **Specialized**: Dedicated hardware with optimized chips for SSL acceleration or content switching.  
- **High Performance**: Suited to enterprise data centers needing ultra-low latency and high throughput.  
- **Costly**: More expensive than software solutions but provides advanced feature sets and reliability.

III. Cloud-Based Reverse Proxies

- **Managed Solutions**: Services like AWS Elastic Load Balancing (ALB/ELB), Cloudflare, or Akamai.  
- **Advantages**:
  - **Scalable**: Instantly add more capacity.  
  - **Global**: Edge locations reduce latency for users worldwide.  
  - **Low Maintenance**: Offload management of hardware and updates to the provider.

### Security Implications

I. Security Benefits

- **Hides Backend Servers**: Attackers only see the reverse proxy’s address, reducing attack surface on internal servers.  
- **Traffic Filtering**: Built-in Web Application Firewalls (WAFs) can block SQL injection, XSS, or suspicious patterns.  
- **DDoS Mitigation**: Can throttle or blacklist offending IPs, and help absorb volumetric attacks.

II. Potential Risks

- **Single Point of Failure**: If the proxy itself goes down without redundancy, the entire site may be inaccessible.  
- **Misconfiguration**: Complex rules or incomplete SSL setups can create vulnerabilities.  
- **Trust Issues**: The proxy has access to unencrypted data if SSL is terminated at the proxy. Proper security measures are essential.

III. Integrating with Other Security Tools

- **Firewalls**: Combine with perimeter firewalls or intrusion prevention systems (IPS).  
- **WAF (Web Application Firewall)**: Deploy on or alongside the proxy to inspect HTTP traffic in detail.  
- **Regular Updates**: Keep proxy software current with security patches, ensuring known exploits are mitigated.
