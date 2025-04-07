# Kubernetes Resource Optimizer - Backend

A backend service that analyzes Kubernetes deployments, collects resource usage metrics from Prometheus, and provides optimization recommendations.

## 🚀 Features

- Connects to a Kubernetes cluster to analyze deployment configurations
- Pulls resource metrics from Prometheus for containers
- Calculates recommended CPU and memory requests
- Detects OOM (Out-Of-Memory) events
- Tracks HPA (Horizontal Pod Autoscaler) settings
- Creates automated GitHub PRs to update resource specs
- Implements Redis/Valkey caching to reduce expensive Prometheus queries

## 🧰 Tech Stack

- Python 3.9
- FastAPI
- Kubernetes Python Client
- Redis/Valkey (as cache)
- Prometheus (metrics source)
- GitHub API (PR automation)

## ⚙️ Configuration

Set via environment variables:

### Kubernetes & AWS Settings
```env
KUBERNETES_CONTEXT   # Kubernetes context (e.g., EKS ARN)
NAMESPACE            # Namespace to analyze (default: "default")
```

### Prometheus Configuration
```env
PROMETHEUS_URL       # URL of Prometheus server
MAX_WORKERS          # Concurrent workers (default: 10)
BUFFER_FACTOR        # Multiplier for safe margins (default: 1.1)
LOOKBACK_PERIOD      # Historical range (e.g., "8d" for 8 days)
```

### Redis/Valkey Cache
```env
REDIS_HOST           # Redis/Valkey hostname
REDIS_PORT           # Port (default: 6379)
REDIS_PASSWORD       # Password (if required)
REDIS_USE_SSL        # true/false - Use SSL connection
```

### GitHub Configuration
```env
GITHUB_TOKEN         # Personal access token for creating PRs
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`                     | Welcome message & health check |
| GET    | `/health`              | Backend & cache health info |
| GET    | `/api/optimize`        | Fetch optimization recommendations |
| GET    | `/api/pr-links`        | Get PR link mappings |
| GET    | `/api/pr-history/{deployment}/{container}` | Get PR history for a container |
| POST   | `/api/create-pr`       | Trigger GitHub PR creation |
| POST   | `/api/clear-cache`     | Clear Redis cache manually |

## 📈 Prometheus Query Reference

### 🧠 CPU Usage Metrics
```promql
# 1-min CPU usage rate
rate(container_cpu_usage_seconds_total{namespace="<namespace>", pod=~"<deployment>-.*", container="<container>"}[1m])

# Minimum usage during lookback
min_over_time(rate(...)[<lookback-period>:])

# Average usage
avg_over_time(rate(...)[<lookback-period>:])

# Peak usage
max_over_time(rate(...)[<lookback-period>:])
```
These help estimate how much CPU the container actually uses vs. what’s requested.

### 💾 Memory Usage Metrics
```promql
# Current memory consumption
container_memory_working_set_bytes{namespace="<namespace>", pod=~"<deployment>-.*", container="<container>"}

# Historical minimum/avg/max
min_over_time(...), avg_over_time(...), max_over_time(...)
```
Shows trends in memory usage to prevent OOMs.

### 🔥 OOMKill & Restarts
```promql
# Containers killed due to memory
kube_pod_container_status_last_terminated_reason{reason="OOMKilled", ...}

# Container restart count
kube_pod_container_status_restarts_total{container="<container>", ...}
```
Useful for identifying unstable containers.

### 📊 Replica Info (HPA Insight)
```promql
# Historical replica scaling
max_over_time(kube_deployment_status_replicas{...}[<lookback-period>:])
min_over_time(kube_deployment_status_replicas{...}[<lookback-period>:])

# Current replica spec
kube_deployment_spec_replicas{...}
```
Helps correlate resource usage with autoscaling.

## 🧠 Caching Strategy

Redis/Valkey is used to cache expensive API calls:

| Data Type         | TTL         |
|------------------|-------------|
| Optimization Data | 24 hours    |
| PR Links          | 30 days     |
| PR History        | 30 days     |

This reduces Prometheus queries (especially important for AWS Managed Prometheus which is billed per request).

## 🧪 Running Locally

1. Export environment variables or use a `.env` file
2. (Optional) Use SSM port forwarding for Redis if in a private subnet
3. Launch FastAPI server:
```bash
uvicorn main:app --reload
```

## 🐳 Docker

### Build Image
```bash
docker build -t resource-optimizer-backend .
```

### Run Container
```bash
docker run -p 8000:8000 --env-file .env resource-optimizer-backend
```

