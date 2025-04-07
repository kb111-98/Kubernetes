# Kubernetes Resource Optimizer - Backend

A backend service that analyzes Kubernetes deployments, collects resource usage metrics from Prometheus, and provides optimization recommendations.

## Features

- Connects to Kubernetes cluster to analyze deployment configurations
- Collects and analyzes Prometheus metrics to determine actual resource usage
- Provides optimized CPU and memory recommendations
- Monitors Out-of-Memory (OOM) events
- Tracks HPA (Horizontal Pod Autoscaler) configurations
- Automates resource adjustment Pull Requests to GitHub repositories
- Implements Redis/Valkey caching to reduce expensive Prometheus queries

## Tech Stack

- Python 3.9
- FastAPI
- Kubernetes Python Client
- Redis/Valkey for caching
- Prometheus for metrics
- GitHub API for PR automation

## Configuration

The application is configured using environment variables:

### Kubernetes & AWS Settings
```
KUBERNETES_CONTEXT   # Kubernetes context (ARN for AWS EKS)
NAMESPACE            # Namespace to analyze (default: "default")
```

### Prometheus Configuration
```
PROMETHEUS_URL       # Prometheus API endpoint URL
MAX_WORKERS          # Maximum number of concurrent workers (default: 10)
BUFFER_FACTOR        # Safety margin for recommendations (default: 1.1)
LOOKBACK_PERIOD      # Historical data period to analyze (default: "8d")
```

### Redis/Valkey Cache
```
REDIS_HOST           # Redis/Valkey host address
REDIS_PORT           # Redis/Valkey port (default: 6379)
REDIS_PASSWORD       # Password for Redis/Valkey (if required)
REDIS_USE_SSL        # Whether to use SSL for Redis connection (default: true)
```

### GitHub Configuration
```
GITHUB_TOKEN         # GitHub token for PR automation
```

## API Endpoints

- `GET /` - Welcome message and API health check
- `GET /health` - Server and cache health status
- `GET /api/optimize` - Get optimization data for deployments
- `GET /api/pr-links` - Get mapping of deployments to PR URLs
- `GET /api/pr-history/{deployment_name}/{container_name}` - Get PR history
- `POST /api/create-pr` - Create automated PR for resource adjustments
- `POST /api/clear-cache` - Clear cached data

## Prometheus Queries

### CPU Usage Metrics
```
rate(container_cpu_usage_seconds_total{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[1m])
min_over_time(rate(container_cpu_usage_seconds_total{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[1m])[<lookback-period>:])
avg_over_time(rate(container_cpu_usage_seconds_total{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[1m])[<lookback-period>:])
max_over_time(rate(container_cpu_usage_seconds_total{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[1m])[<lookback-period>:])
```

### Memory Usage Metrics
```
container_memory_working_set_bytes{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}
min_over_time(container_memory_working_set_bytes{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[<lookback-period>:])
avg_over_time(container_memory_working_set_bytes{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[<lookback-period>:])
max_over_time(container_memory_working_set_bytes{namespace="<namespace>",pod=~"<deployment-name>-.*",container="<container-name>"}[<lookback-period>:])
```

### OOM (Out-of-Memory) Detection
```
kube_pod_container_status_last_terminated_reason{reason="OOMKilled", namespace="<namespace>", pod=~"<deployment-name>-.*"}
kube_pod_container_status_restarts_total{container="<container-name>", namespace="<namespace>", pod=~"<deployment-name>-.*"}
```

### Replica Information
```
max_over_time(kube_deployment_status_replicas{namespace="<namespace>", deployment="<deployment-name>"}[<lookback-period>:])
min_over_time(kube_deployment_status_replicas{namespace="<namespace>", deployment="<deployment-name>"}[<lookback-period>:])
kube_deployment_spec_replicas{namespace="<namespace>", deployment="<deployment-name>"}
```

## Caching Strategy

The application uses Redis/Valkey to cache:

1. Optimization data (24-hour TTL)
2. PR information (30-day TTL for latest PRs)
3. PR history (30-day TTL, up to 10 entries per deployment/container)

This reduces the load on Prometheus and GitHub API, especially important for AWS Managed Prometheus which charges per query.

## Running Locally

1. Set up environment variables
2. Start SSM port forwarding for Redis/Valkey (if in private subnet)
3. Run the FastAPI application: `uvicorn main:app --reload`

## Docker

Build the Docker image:
```
docker build -t resource-optimizer-backend .
```

Run with Docker:
```
docker run -p 8000:8000 --env-file .env resource-optimizer-backend
```

