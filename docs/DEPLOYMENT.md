# Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- Git repository access
- Python 3.8+ (for local deployment)
- 4GB+ available disk space
- 2GB+ available RAM

## Deployment Environments

### **Local Development**

**Quick Start:**
```bash
# 1. Clone repository
git clone https://github.com/your-repo/job-application-agent.git
cd job-application-agent

# 2. Run setup
bash scripts/setup_environment.sh

# 3. Activate environment
source venv/bin/activate

# 4. Start application
python app.py

# Access at: http://localhost:7860
```

**Requirements:**
- ~500MB disk space
- 1GB RAM
- Virtual environment

---

### **Docker Development**

**Setup:**
```bash
# Build image
docker build -t job-agent:latest .

# Run container
docker run -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  job-agent:latest

# Access at: http://localhost:7860
```

**Dockerfile Highlights:**
- Python 3.9 slim base image
- Multi-stage build for optimization
- Security scanning
- Health checks included

---

### **Staging Deployment**

**Using Docker Compose:**
```bash
# Start services
docker-compose -f docker-compose.staging.yml up -d

# Services:
# - Web API (port 7860)
# - PostgreSQL (port 5432)
# - Redis (port 6379)

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

**Staging Configuration:**
- Test environment setup
- Sample data loaded
- Debug logging enabled
- Monitoring active

---

### **Production Deployment**

#### **Option 1: Docker Swarm**

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml job-agent

# Scale services
docker service scale job-agent_web=3

# Monitor
docker service ls
docker stack ps job-agent
```

#### **Option 2: Kubernetes**

```bash
# Create namespace
kubectl create namespace job-agent

# Deploy
kubectl apply -f kubernetes/ -n job-agent

# Check deployment
kubectl get pods -n job-agent
kubectl get services -n job-agent

# Scale replicas
kubectl scale deployment job-agent --replicas=5 -n job-agent

# Monitor logs
kubectl logs -f deployment/job-agent -n job-agent
```

**Kubernetes Resources:**
- Deployment (3+ replicas)
- Service (LoadBalancer)
- ConfigMap (configuration)
- Secret (credentials)
- PVC (persistent storage)
- HPA (auto-scaling)

---

## Configuration for Deployment

### **Environment Variables**

Create `.env` file:
```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Database
DATABASE_URL=postgresql://user:pass@db:5432/job_agent
REDIS_URL=redis://cache:6379/0

# API
API_HOST=0.0.0.0
API_PORT=7860
API_WORKERS=4

# Model
MODEL_PATH=/app/models/model_latest.pt
VOCAB_SIZE=5000

# Cloud Storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=job-agent-bucket
```

### **Secrets Management**

**GitHub Actions:**
1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `DATABASE_URL`
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `DEPLOY_KEY`
   - `SLACK_WEBHOOK_URL`

**Using AWS Secrets Manager:**
```bash
# Store secret
aws secretsmanager create-secret \
  --name job-agent/db-password \
  --secret-string "your-password"

# Retrieve in app
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='job-agent/db-password')
```

---

## CI/CD Pipeline

### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: bash scripts/run_tests.sh

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t job-agent:${{ github.sha }} .
      - name: Push to registry
        run: |
          docker tag job-agent:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/job-agent:latest
          docker push ${{ secrets.DOCKER_REGISTRY }}/job-agent:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/job-agent \
            job-agent=${{ secrets.DOCKER_REGISTRY }}/job-agent:latest
```

---

## Database Setup

### **PostgreSQL**

```bash
# Create database
createdb job_agent

# Initialize schema
psql job_agent < scripts/schema.sql

# Create user
createuser job_agent_user
ALTER USER job_agent_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE job_agent TO job_agent_user;
```

### **Redis**

```bash
# Start Redis
redis-server

# Verify
redis-cli ping
# Output: PONG
```

---

## Health Checks & Monitoring

### **Liveness Probe**
```bash
curl http://localhost:7860/health
```

### **Readiness Probe**
```bash
curl http://localhost:7860/ready
```

### **Monitoring Stack**

```bash
# Prometheus metrics
curl http://localhost:9090/metrics

# Grafana dashboard
# Access: http://localhost:3000
# Credentials: admin/admin

# Alert rules configured:
# - High CPU usage (>80%)
# - High memory usage (>85%)
# - API errors (>5%)
# - Response time (>1s)
```

---

## Scaling & Load Balancing

### **Horizontal Scaling**

```bash
# Using Docker Swarm
docker service update --replicas 5 job-agent_web

# Using Kubernetes
kubectl scale deployment job-agent --replicas=5
```

### **Load Balancer Configuration**

```nginx
upstream job_agent {
    server app1:7860;
    server app2:7860;
    server app3:7860;
}

server {
    listen 80;
    server_name api.job-agent.com;
    
    location / {
        proxy_pass http://job_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Backup & Recovery

### **Backup Database**

```bash
# Full backup
pg_dump job_agent > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump job_agent | gzip > backup.sql.gz

# S3 backup
aws s3 cp backup.sql.gz s3://backups/job-agent/
```

### **Restore Database**

```bash
# From file
psql job_agent < backup.sql

# From compressed
gunzip -c backup.sql.gz | psql job_agent
```

---

## Troubleshooting Deployment

### **Container won't start**
```bash
# Check logs
docker logs container-name

# Inspect configuration
docker inspect container-name
```

### **Database connection failed**
```bash
# Test connection
psql -h localhost -U user -d job_agent

# Check network
docker network ls
docker network inspect bridge
```

### **Performance issues**
```bash
# Monitor resources
docker stats

# Check application logs
tail -f logs/app.log
```

---

## Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set strong database passwords
- [ ] Enable API authentication
- [ ] Configure rate limiting
- [ ] Enable logging and monitoring
- [ ] Set up automatic backups
- [ ] Configure secure secrets storage
- [ ] Enable health checks
- [ ] Set up alerts

---

## Rollback Procedure

### **Kubernetes Rollback**
```bash
# Check rollout history
kubectl rollout history deployment/job-agent

# Rollback to previous version
kubectl rollout undo deployment/job-agent

# Rollback to specific revision
kubectl rollout undo deployment/job-agent --to-revision=2
```

### **Docker Swarm Rollback**
```bash
# Revert service to previous image
docker service update --image previous-image job-agent_web
```

---

## Performance Tuning

### **Application Settings**
```yaml
# config/config.yaml
training:
  batch_size: 64  # Increase for better performance
  num_workers: 4  # Parallel data loading

cache:
  enabled: true
  ttl: 3600  # 1 hour cache

server:
  workers: 4  # Gunicorn workers
  timeout: 60
```

### **Database Optimization**
```sql
-- Create indexes
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_applications_status ON applications(status);

-- Analyze performance
ANALYZE;
```

---

## Cost Optimization

- Use spot instances for non-critical workloads
- Implement auto-scaling based on metrics
- Use CDN for static assets
- Compress database backups
- Archive old logs

---

## Support & Maintenance

- **Status Page**: https://status.job-agent.com
- **Incident Report**: File at `issues/deployment-issues`
- **Maintenance Window**: Every Sunday 2-4 AM UTC
- **SLA**: 99.9% uptime

---

For detailed deployment scripts, see: `scripts/deploy.sh`
