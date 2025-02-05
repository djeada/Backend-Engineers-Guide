## Nginx  
Nginx is a high-performance web server, reverse proxy, and load balancer that has grown popular for its speed, scalability, and flexibility. It can serve static files extremely quickly, proxy requests to application servers, balance traffic across multiple backends, terminate SSL/TLS connections, and more. This makes it a powerful tool in modern web architectures. These notes delve into the conceptual underpinnings of Nginx, explore common use cases, show how to configure it, and provide ASCII diagrams to illustrate how data flows through it.

### Core Concepts of Nginx  
Nginx uses an event-driven, asynchronous model to handle connections, in contrast to the thread-based or process-based designs of some other servers. This architecture enables high concurrency with relatively low resource usage.  

Requests pass through phases, such as parsing the incoming request, matching it against configuration blocks, and deciding whether to serve static content or pass the request upstream to application servers. Nginx’s configuration is file-based, typically located in `/etc/nginx/nginx.conf` and optional site-specific files under `/etc/nginx/conf.d` or similar directories.

Below is an ASCII diagram showing how a client request might flow through Nginx when it is acting as a reverse proxy:

```
   +---------------+
   |   Internet    |
   | (Clients)     |
   +-------+-------+
           |
           | HTTP/HTTPS Requests
           v
    +---------------+    +------------------+
    |   Nginx       |----|  Upstream App 1  |
    |(Reverse Proxy)|    +------------------+
    +-------+-------+    +------------------+
           |             |  Upstream App 2  |
           |             +------------------+
           v
    +---------------+
    |  Static Files |
    | or local data |
    +---------------+
```

In this diagram, Nginx listens for incoming requests, checks if the request should be served with a local static file, or forwards it to an upstream application server (App 1 or App 2). It then collects the response and sends it back to the client.

### Installation and Basic Configuration  
Package managers often provide recent Nginx versions. On Debian-based systems, install it by running:

```bash
sudo apt-get update
sudo apt-get install nginx
```

Once installed, the default main configuration file is typically located at `/etc/nginx/nginx.conf`. It references additional configuration blocks in `/etc/nginx/sites-enabled/` or `/etc/nginx/conf.d/`.

A very minimal nginx.conf might look like this:

```nginx
worker_processes  1;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    server {
        listen 80;
        server_name example.com;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }
    }
}
```

This configuration runs a single worker process, handles up to 1024 connections, and serves static files from `/usr/share/nginx/html`. It listens on port 80 and responds to the hostname `example.com`.

### Serving Static Files  
Nginx excels at serving static assets like HTML, CSS, JavaScript, and images. The `location` directive tells Nginx how to handle requests for a given path. If `root` points to a directory, Nginx looks for the requested file there, returning a 404 if it is missing.  

A typical block might look like this:

```nginx
server {
    listen 80;
    server_name mysite.com;

    location / {
        root /var/www/html;
        index index.html;
    }

    location /images/ {
        root /var/www/html;
    }
}
```

Requests to `http://mysite.com/images/logo.png` map to the file `/var/www/html/images/logo.png`, which is served directly.

### Acting as a Reverse Proxy  
When Nginx proxies requests to another server, the configuration usually sets `proxy_pass` in a `location` block. This is especially useful for Node.js, Python, Ruby, or other web app servers that run on internal ports or behind the main web server.  

Below is a sample configuration that passes everything under `/api/` to a backend running on port 3000:

```nginx
server {
    listen 80;
    server_name myapp.com;

    location / {
        root /var/www/html;
        index index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

When a user calls `http://myapp.com/api/users`, Nginx strips the `/api/` prefix (unless otherwise configured) and forwards requests to `http://127.0.0.1:3000/`. It adds headers like `Host` and `X-Real-IP` to help the backend know the original request details.

### Load Balancing  
Nginx provides multiple load-balancing strategies, such as round-robin, IP hash, or least connections. By defining an `upstream` block, you can list multiple backend servers, and Nginx will distribute requests among them:

```nginx
upstream backend_cluster {
    server 192.168.0.101:3000;
    server 192.168.0.102:3000;
    server 192.168.0.103:3000;
}

server {
    listen 80;
    server_name cluster.example.com;

    location / {
        proxy_pass http://backend_cluster;
    }
}
```

Requests to `http://cluster.example.com/` are balanced across the three specified servers by default round-robin. Additional parameters like `weight`, `max_fails`, or `fail_timeout` fine-tune behavior.

### SSL/TLS Termination  
Securing traffic with HTTPS is essential. Nginx can terminate TLS (formerly SSL) connections by presenting certificates to the client. Inside the server block, configure certificates and keys:

```nginx
server {
    listen 443 ssl;
    server_name secure.example.com;

    ssl_certificate     /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;

    location / {
        proxy_pass http://127.0.0.1:3000;
    }
}
```

Nginx offloads the encryption from the backend. This is especially useful in microservice architectures where internal traffic doesn’t need to be encrypted again, though best practices vary based on security requirements.

### Common Tasks and Directives  

#### Gzip Compression  
Nginx can compress text-based responses (HTML, JSON, CSS, JavaScript) before sending them. Enabling gzip:

```nginx
http {
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    ...
}
```

#### Redirects  
To redirect traffic from one domain or path to another, use directives like `return` or `rewrite`. For instance, redirect HTTP to HTTPS:

```nginx
server {
    listen 80;
    server_name mysite.com;
    return 301 https://$host$request_uri;
}
```

#### Access Control  
Set `allow` and `deny` within a location block to limit access by IP:

```nginx
location /admin {
    allow 192.168.0.0/24;
    deny all;
    ...
}
```

#### Rate Limiting  
Prevent abuse by limiting requests per IP:

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=5r/s;

    server {
        location /api/ {
            limit_req zone=mylimit burst=10 nodelay;
            proxy_pass http://127.0.0.1:3000;
        }
    }
}
```

In this example, each IP can make 5 requests per second to the `/api/` location, with a burst of 10.

### Logging and Monitoring  
Nginx logs request details to the access log and errors to the error log. The default location might be `/var/log/nginx/`. Monitoring solutions can parse these logs to track metrics like request rates, response times, or error frequencies.  

A custom log format in your nginx.conf could look like:

```nginx
log_format  main  '$remote_addr - $remote_user [$time_local] '
                  '"$request" $status $body_bytes_sent '
                  '"$http_referer" "$http_user_agent" '
                  '$request_time';

access_log /var/log/nginx/access.log main;
```

This records additional details, such as `$request_time`, which can help detect slow endpoints.

### Performance Tuning  
Nginx can handle thousands of simultaneous connections using a small number of worker processes. Some important settings:

- **worker_processes**: Typically set to the number of CPU cores.  
- **worker_connections**: How many connections each worker can handle; set according to system limits.  
- **sendfile on**: Enables efficient file transfers from OS buffers.  
- **keepalive_timeout**: How long idle connections remain open.

A simplified concurrency formula might look like:

```
Max_Connections = worker_processes * worker_connections
```

Adjusting the OS limits (like `ulimit -n` for open files) also matters when scaling to many connections.

### Advanced Use Cases  

#### HTTP/2 Support  
Enabling HTTP/2 helps with multiplexing. Add `http2` to the listen directive:

```nginx
server {
    listen 443 ssl http2;
    ...
}
```

#### Caching  
Nginx can act as a caching proxy for upstream servers. Define a cache path and use `proxy_cache` settings:

```nginx
http {
    proxy_cache_path /var/cache/nginx keys_zone=mycache:10m;

    server {
        location / {
            proxy_cache mycache;
            proxy_pass http://backend;
        }
    }
}
```

#### WebSocket Proxy  
For WebSocket applications, ensure the upgrade headers are preserved:

```nginx
location /socket/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://127.0.0.1:4000;
}
```

This allows WebSocket connections to pass through Nginx without being broken.
