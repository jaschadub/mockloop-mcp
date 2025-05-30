# Docker Integration

MockLoop provides comprehensive Docker support for containerizing your mock servers, making deployment and scaling easier across different environments.

## Overview

Docker integration in MockLoop includes:

- **Automatic Dockerfile generation** for mock servers
- **Docker Compose configurations** for multi-service setups
- **Container orchestration** support
- **Environment-specific configurations**
- **Scaling and load balancing** capabilities

## Quick Start with Docker

### Generating Docker-Enabled Mock Servers

When generating a mock server, Docker support is included by default:

```python
from mockloop_mcp import generate_mock_api

# Generate mock server with Docker support
generate_mock_api(
    spec_url_or_path="openapi.yaml",
    output_dir_name="my_mock_server"
)
```

This creates:
- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-service orchestration
- `.dockerignore` - Optimized build context
- `requirements.txt` - Python dependencies

### Building the Docker Image

```bash
cd my_mock_server

# Build the Docker image
docker build -t my-mock-server .

# Run the container
docker run -p 8000:8000 my-mock-server
```

### Using Docker Compose

For more complex setups with databases and additional services:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Docker Configuration

### Dockerfile Structure

The generated Dockerfile follows best practices:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mockloop && chown -R mockloop:mockloop /app
USER mockloop

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the server
CMD ["python", "main.py"]
```

### Environment Variables

Configure your mock server using environment variables:

```bash
# Basic configuration
docker run -p 8000:8000 \
  -e MOCK_PORT=8000 \
  -e MOCK_HOST=0.0.0.0 \
  -e LOG_LEVEL=INFO \
  my-mock-server

# Database configuration
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/mockloop \
  -e REDIS_URL=redis://redis:6379/0 \
  my-mock-server
```

### Docker Compose Configuration

The generated `docker-compose.yml` includes all necessary services:

```yaml
version: '3.8'

services:
  mock-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/mockloop
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=mockloop
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mock-server
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## Production Deployment

### Multi-Stage Builds

For optimized production images:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mockloop && chown -R mockloop:mockloop /app
USER mockloop

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
CMD ["python", "main.py"]
```

### Health Checks and Monitoring

Configure comprehensive health monitoring:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mock-server:
    build: .
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Load Balancing

Use nginx for load balancing multiple instances:

```nginx
# nginx.conf
upstream mock_servers {
    server mock-server-1:8000;
    server mock-server-2:8000;
    server mock-server-3:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://mock_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        proxy_pass http://mock_servers;
    }
}
```

## Container Orchestration

### Kubernetes Deployment

Deploy to Kubernetes with proper configurations:

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mockloop-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mockloop-server
  template:
    metadata:
      labels:
        app: mockloop-server
    spec:
      containers:
      - name: mockloop
        image: my-mock-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mockloop-secrets
              key: database-url
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: mockloop-service
spec:
  selector:
    app: mockloop-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Docker Swarm

Deploy using Docker Swarm:

```yaml
# docker-stack.yml
version: '3.8'

services:
  mock-server:
    image: my-mock-server:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    networks:
      - mockloop-network
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/mockloop

  postgres:
    image: postgres:15
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    environment:
      - POSTGRES_DB=mockloop
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mockloop-network

networks:
  mockloop-network:
    driver: overlay

volumes:
  postgres_data:
```

## Development Workflows

### Development with Docker

Use Docker for consistent development environments:

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  mock-server:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /app/__pycache__
    environment:
      - FLASK_ENV=development
      - LOG_LEVEL=DEBUG
    command: python main.py --reload
```

### Hot Reloading

Enable hot reloading for development:

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install development dependencies
COPY requirements.dev.txt .
RUN pip install -r requirements.dev.txt

# Copy source code
COPY . .

# Enable hot reloading
CMD ["python", "main.py", "--reload", "--host", "0.0.0.0"]
```

### Testing in Containers

Run tests in isolated containers:

```bash
# Run tests in container
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.11-slim \
  bash -c "pip install -r requirements.txt && python -m pytest"

# Integration tests with docker-compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Performance Optimization

### Image Size Optimization

Minimize Docker image size:

```dockerfile
# Use alpine base image
FROM python:3.11-alpine

# Install only necessary packages
RUN apk add --no-cache \
    curl \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/cache/apk/*

# Use .dockerignore to exclude unnecessary files
```

### Caching Strategies

Optimize build caching:

```dockerfile
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code last
COPY . .
```

### Resource Limits

Set appropriate resource limits:

```yaml
services:
  mock-server:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Security Best Practices

### Non-Root User

Always run containers as non-root:

```dockerfile
RUN useradd -m -u 1000 mockloop
USER mockloop
```

### Secret Management

Use Docker secrets for sensitive data:

```yaml
services:
  mock-server:
    secrets:
      - db_password
      - api_key
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    external: true
  api_key:
    external: true
```

### Network Security

Isolate services with custom networks:

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

services:
  mock-server:
    networks:
      - frontend
      - backend
  
  postgres:
    networks:
      - backend
```

## Monitoring and Logging

### Centralized Logging

Configure centralized logging:

```yaml
services:
  mock-server:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=mockloop"
```

### Metrics Collection

Integrate with monitoring systems:

```yaml
services:
  mock-server:
    environment:
      - PROMETHEUS_ENABLED=true
      - METRICS_PORT=9090
    ports:
      - "9090:9090"  # Metrics endpoint
```

## Troubleshooting

### Common Docker Issues

1. **Port conflicts**: Use different ports or stop conflicting services
2. **Permission issues**: Check user permissions and volume mounts
3. **Memory issues**: Increase Docker memory limits
4. **Network connectivity**: Verify network configurations

### Debugging Containers

```bash
# Check container logs
docker logs mockloop-server

# Execute commands in running container
docker exec -it mockloop-server bash

# Inspect container configuration
docker inspect mockloop-server

# Check resource usage
docker stats mockloop-server
```

## Next Steps

- [Performance Monitoring](performance-monitoring.md) - Monitor containerized services
- [Scenario Management](scenario-management.md) - Manage scenarios in containers
- [Advanced Features](advanced-features.md) - Explore advanced Docker features