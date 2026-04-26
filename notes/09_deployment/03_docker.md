
## Docker and Containerization

Docker packages an application and all of its dependencies into a lightweight, portable unit called a container. Containers share the host OS kernel but run in isolated namespaces, so they start in milliseconds and consume far less memory than virtual machines.

```
  +------------------------------- Host OS -------------------------------+
  |  +-----------+  +-----------+  +-----------+                         |
  |  | Container |  | Container |  | Container |   <-- isolated processes |
  |  |  App + Libs  |  App + Libs  |  App + Libs  |                         |
  |  +-----------+  +-----------+  +-----------+                         |
  |  +-----------------------------------------------------------+        |
  |  |                  Docker Engine / containerd               |        |
  |  +-----------------------------------------------------------+        |
  |  +-----------------------------------------------------------+        |
  |  |                  Host OS Kernel                           |        |
  |  +-----------------------------------------------------------+        |
  +-----------------------------------------------------------------------+
```

- **Image** is a read-only template built from a `Dockerfile`; images are stored in a registry.
- **Container** is a running instance of an image with its own writable layer.
- **Registry** (Docker Hub, GitHub Container Registry, ECR) stores and distributes images.

### Installing Docker

```bash
# Debian / Ubuntu
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Add current user to the docker group so you can run without sudo
sudo usermod -aG docker $USER
newgrp docker
```

### Writing a Dockerfile

A `Dockerfile` is a text file that describes how to build an image layer by layer.

```dockerfile
# Use a minimal base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies first (layer cache optimisation)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose the port the app listens on
EXPOSE 8000

# Non-root user for security
RUN adduser --disabled-password appuser
USER appuser

# Default command
CMD ["python", "main.py"]
```

Key best practices:

- **Order layers** from least to most frequently changed to maximise cache hits.
- **Use specific base image tags** (e.g., `python:3.11-slim`) instead of `latest` to keep builds reproducible.
- **Run as a non-root user** to limit the blast radius of a container escape.
- **Combine `RUN` instructions** with `&&` to reduce the number of layers.

### Building and Tagging Images

```bash
# Build an image from the current directory
docker build -t myapp:1.0.0 .

# Tag the same image for a registry
docker tag myapp:1.0.0 ghcr.io/myorg/myapp:1.0.0

# Push to the registry
docker push ghcr.io/myorg/myapp:1.0.0
```

### Running Containers

```bash
# Run in the foreground (Ctrl-C to stop)
docker run --rm -p 8000:8000 myapp:1.0.0

# Run detached, name the container, and pass environment variables
docker run -d \
  --name myapp \
  -p 8000:8000 \
  -e DATABASE_URL=postgres://user:pass@db:5432/mydb \
  myapp:1.0.0

# Tail logs
docker logs -f myapp

# Open a shell inside a running container
docker exec -it myapp /bin/bash

# Stop and remove
docker stop myapp && docker rm myapp
```

### Docker Compose

Compose defines and runs multi-container applications with a single YAML file.

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      retries: 5

volumes:
  db_data:
```

```bash
# Start all services
docker compose up -d

# View logs across all services
docker compose logs -f

# Stop and remove containers (keep volumes)
docker compose down

# Stop and remove containers and volumes
docker compose down -v
```

### Image Layers and Caching

Docker builds images by executing each `Dockerfile` instruction and saving the result as a new layer. Layers are content-addressed and cached; if a layer's instruction and its inputs are unchanged, Docker reuses the cached layer.

```
Dockerfile instruction      Layer (cached if unchanged)
────────────────────────    ───────────────────────────
FROM python:3.11-slim    →  base layer
COPY requirements.txt    →  deps layer
RUN pip install …        →  install layer   ← cache invalidated when requirements.txt changes
COPY . .                 →  source layer    ← always invalidated on code change
CMD …                    →  metadata only
```

### Multi-Stage Builds

Multi-stage builds produce a small production image by discarding build-time tools:

```dockerfile
# Stage 1: build
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN go build -o /app ./cmd/server

# Stage 2: minimal runtime
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /app
ENTRYPOINT ["/app"]
```

The final image contains only the compiled binary and the distroless runtime — no compiler, shell, or package manager.

### Volumes and Networking

```bash
# Named volume – data survives container removal
docker run -v db_data:/var/lib/postgresql/data postgres:16

# Bind mount – mounts a host directory into the container (useful for development)
docker run -v $(pwd)/src:/app/src myapp:1.0.0

# Create a user-defined bridge network for container-to-container communication
docker network create mynet
docker run --network mynet --name db postgres:16
docker run --network mynet --name app myapp:1.0.0
# "app" can now reach "db" by hostname
```

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

- **interval** – how often Docker runs the check.
- **timeout** – how long Docker waits for a response.
- **retries** – how many consecutive failures mark the container as unhealthy.

### Security Considerations

- **Scan images** for known CVEs with tools like `docker scout` or `trivy`.
- **Use read-only filesystems** where possible: `docker run --read-only`.
- **Drop Linux capabilities** that are not needed: `--cap-drop ALL --cap-add NET_BIND_SERVICE`.
- **Set resource limits** to prevent a runaway container from starving the host: `--memory 512m --cpus 1`.
- **Never bake secrets** into images; inject them at runtime through environment variables or secret stores.
