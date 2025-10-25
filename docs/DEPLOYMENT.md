# Deployment Guide

This guide covers different deployment options for the Virtual Council Assistant.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)

## Local Development

### Prerequisites
- Python 3.11+
- pip or poetry
- Telegram Bot Token
- OpenAI or Gemini API Key

### Setup
```bash
# Clone repository
git clone https://github.com/inesusvet/virt-council-iaac.git
cd virt-council-iaac

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python setup.py

# Run the bot
python -m app.main
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. **Build and run**:
```bash
docker-compose up -d
```

3. **View logs**:
```bash
docker-compose logs -f bot
```

4. **Stop**:
```bash
docker-compose down
```

### Using Docker directly

1. **Build image**:
```bash
docker build -t virt-council-bot .
```

2. **Run container**:
```bash
docker run -d \
  --name virt-council-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  virt-council-bot
```

3. **View logs**:
```bash
docker logs -f virt-council-bot
```

## Cloud Deployment

### AWS Deployment (ECS/Fargate)

1. **Build and push Docker image**:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t virt-council-bot .
docker tag virt-council-bot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/virt-council-bot:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/virt-council-bot:latest
```

2. **Create ECS Task Definition**:
- Use the Docker image from ECR
- Set environment variables or use AWS Secrets Manager
- Configure volume for persistent data (EFS)

3. **Create ECS Service**:
- Use Fargate for serverless deployment
- Configure auto-scaling if needed
- Set up CloudWatch for logging

### Google Cloud Run

1. **Build and push image**:
```bash
# Configure gcloud
gcloud auth configure-docker

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/virt-council-bot

# Or use Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy virt-council-bot \
  --image gcr.io/YOUR_PROJECT_ID/virt-council-bot \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY \
  --allow-unauthenticated
```

### Azure Container Instances

1. **Build and push to ACR**:
```bash
# Login to ACR
az acr login --name yourregistry

# Build and push
az acr build --registry yourregistry --image virt-council-bot .
```

2. **Deploy to ACI**:
```bash
az container create \
  --resource-group myResourceGroup \
  --name virt-council-bot \
  --image yourregistry.azurecr.io/virt-council-bot:latest \
  --registry-login-server yourregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --environment-variables \
    TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN \
    OPENAI_API_KEY=$OPENAI_API_KEY
```

### DigitalOcean App Platform

1. **Create app.yaml**:
```yaml
name: virt-council-bot
services:
- name: bot
  github:
    repo: inesusvet/virt-council-iaac
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile
  envs:
  - key: TELEGRAM_BOT_TOKEN
    value: ${TELEGRAM_BOT_TOKEN}
  - key: OPENAI_API_KEY
    value: ${OPENAI_API_KEY}
  - key: LLM_PROVIDER
    value: openai
```

2. **Deploy**:
```bash
doctl apps create --spec app.yaml
```

### Railway

1. **Create railway.json**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python -m app.main"
  }
}
```

2. **Deploy via Railway CLI or GitHub integration**

## Production Considerations

### Security

1. **Environment Variables**:
   - Never commit .env file
   - Use secrets management (AWS Secrets Manager, GCP Secret Manager)
   - Rotate API keys regularly

2. **Database**:
   - Use PostgreSQL instead of SQLite for production
   - Enable SSL/TLS connections
   - Regular backups
   - Implement connection pooling

3. **Network**:
   - Use VPC/Private networks
   - Implement rate limiting
   - Use firewalls and security groups

### Monitoring

1. **Logging**:
```python
# Configure structured logging
import logging
import json_logging

json_logging.init_non_web(enable_json=True)
logger = logging.getLogger(__name__)
```

2. **Metrics**:
   - Track message processing time
   - Monitor API rate limits
   - Track error rates
   - Monitor database connections

3. **Alerting**:
   - Set up alerts for errors
   - Monitor bot uptime
   - Track API quota usage

### Performance

1. **Database Optimization**:
   - Add indexes for frequently queried fields
   - Use connection pooling
   - Implement caching for static data

2. **Async Operations**:
   - Use async/await throughout (already implemented)
   - Implement task queues for heavy operations
   - Use background workers if needed

3. **Resource Management**:
   - Set memory limits
   - Configure CPU limits
   - Monitor resource usage

### Scalability

1. **Horizontal Scaling**:
   - Use multiple bot instances
   - Implement message queue (RabbitMQ, Redis)
   - Share database across instances

2. **Database Scaling**:
   - Use read replicas
   - Implement database sharding if needed
   - Use managed database services

3. **Caching**:
   - Cache frequent queries
   - Use Redis for session storage
   - Cache LLM responses when appropriate

### Backup Strategy

1. **Database Backups**:
```bash
# SQLite backup
sqlite3 data/virt_council.db ".backup data/backup.db"

# PostgreSQL backup
pg_dump -U username -d virt_council > backup.sql
```

2. **Automated Backups**:
   - Daily database backups
   - Keep backups for 30 days
   - Test restore procedures regularly

### Updates and Maintenance

1. **Zero-Downtime Deployments**:
   - Use blue-green deployment
   - Implement health checks
   - Graceful shutdown handling

2. **Database Migrations**:
```bash
# Using Alembic
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

3. **Dependency Updates**:
```bash
# Check for outdated packages
pip list --outdated

# Update requirements
pip-compile --upgrade requirements.in
```

### Cost Optimization

1. **Compute**:
   - Use spot instances where applicable
   - Right-size containers
   - Use auto-scaling

2. **Storage**:
   - Clean old data regularly
   - Compress backups
   - Use appropriate storage tiers

3. **API Costs**:
   - Monitor LLM API usage
   - Implement caching
   - Use cheaper models when possible

## Health Checks

Add health check endpoint (optional):

```python
# app/health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Environment Variables Reference

```env
# Required
TELEGRAM_BOT_TOKEN=          # Telegram bot token
LLM_PROVIDER=                # openai or gemini
OPENAI_API_KEY=              # OpenAI API key (if using OpenAI)
GEMINI_API_KEY=              # Gemini API key (if using Gemini)

# Optional
DATABASE_URL=                # Database connection string
LOG_LEVEL=                   # INFO, DEBUG, WARNING, ERROR
DEBUG=                       # true or false
OPENAI_MODEL=                # gpt-4o-mini, gpt-4, etc.
GEMINI_MODEL=                # gemini-1.5-flash, etc.
```

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check bot token is correct
   - Verify bot is running (check logs)
   - Check network connectivity

2. **LLM API errors**:
   - Verify API key is valid
   - Check API quota/credits
   - Monitor rate limits

3. **Database errors**:
   - Check database connection string
   - Verify database is accessible
   - Check disk space

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
DEBUG=true
```

View detailed logs:
```bash
tail -f app.log
```

## Support

For deployment issues:
- Check application logs
- Review this deployment guide
- Open an issue on GitHub
