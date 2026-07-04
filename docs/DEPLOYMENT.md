# Kindered – Deployment Guide

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                     VPS (Existing Server)                    │
│                                                              │
│  ┌─────────────────────────┐                                │
│  │     Nginx (Reverse      │                                │
│  │       Proxy + SSL)      │                                │
│  │                         │                                │
│  │ *.enorviaglobal.com ────┼──► existing services           │
│  │ kindered.enorviaglobal  │                                │
│  │    .com ────────────────┼──► :8901 (Kindered Docker)     │
│  └─────────────────────────┘                                │
│                                                              │
│  ┌─────────────────────────┐                                │
│  │  Docker: kindered-app   │                                │
│  │  ┌───────────────────┐  │                                │
│  │  │  FastAPI (Uvicorn) │  │                                │
│  │  │  Port 8000 → 8901 │  │                                │
│  │  └───────────────────┘  │                                │
│  │  ┌───────────────────┐  │                                │
│  │  │  SQLite DB         │  │  ← Volume: kindered_data      │
│  │  └───────────────────┘  │                                │
│  │  ┌───────────────────┐  │                                │
│  │  │  PDF Reports       │  │  ← Volume: kindered_reports   │
│  │  └───────────────────┘  │                                │
│  └─────────────────────────┘                                │
│                                                              │
│              │                                                │
│              ▼                                                │
│     AWS Bedrock (Claude)                                     │
│     (External API call)                                      │
└──────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Docker & Docker Compose installed on VPS
- Nginx installed with sites-available/sites-enabled pattern
- Certbot for SSL
- DNS A record for `kindered.enorviaglobal.com` pointing to VPS IP
- AWS credentials with Bedrock access

## Deployment Steps

### 1. Server Preparation

```bash
# SSH into VPS
ssh user@your-vps-ip

# Verify Docker
docker --version
docker compose version

# Verify Nginx
nginx -v
ls /etc/nginx/sites-enabled/
```

### 2. Clone and Configure

```bash
# Clone to /opt/kindered
sudo mkdir -p /opt/kindered
sudo chown $USER:$USER /opt/kindered
git clone <repo-url> /opt/kindered

# Configure environment
cd /opt/kindered
cp .env.example .env
nano .env
# Fill in:
#   AWS_REGION=us-east-1
#   AWS_ACCESS_KEY_ID=your-key
#   AWS_SECRET_ACCESS_KEY=your-secret
#   BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 3. Deploy

```bash
# Run deployment script (handles everything)
sudo bash deploy/deploy.sh
```

Or manually:

```bash
# Build and start
docker compose up -d --build

# Verify health
curl http://127.0.0.1:8901/health

# Install Nginx config
sudo cp deploy/nginx/kindered.enorviaglobal.com.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/kindered.enorviaglobal.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL (if not already present)
sudo certbot certonly --webroot -w /var/www/html -d kindered.enorviaglobal.com
sudo systemctl reload nginx
```

### 4. Verify

```bash
curl https://kindered.enorviaglobal.com/health
# {"status":"healthy","service":"Kindered"}
```

## Rollback

```bash
sudo bash /opt/kindered/deploy/rollback.sh
```

Or manually:

```bash
cd /opt/kindered
docker compose down
# Restore previous nginx config from backup
sudo nginx -t && sudo systemctl reload nginx
```

## Complete Removal (Without Affecting Other Services)

```bash
# Stop container
cd /opt/kindered && docker compose down -v

# Remove Nginx config
sudo rm /etc/nginx/sites-enabled/kindered.enorviaglobal.com
sudo rm /etc/nginx/sites-available/kindered.enorviaglobal.com
sudo nginx -t && sudo systemctl reload nginx

# Remove application
sudo rm -rf /opt/kindered
```

## Monitoring

```bash
# View logs
docker logs kindered-app -f --tail=100

# Check container status
docker ps | grep kindered

# Resource usage
docker stats kindered-app --no-stream
```

## Isolation Guarantees

- **Port isolation**: Uses port 8901 (checked for conflicts before deploy)
- **Container isolation**: Runs in dedicated Docker container `kindered-app`
- **Volume isolation**: Uses named Docker volumes (`kindered_data`, `kindered_reports`)
- **Nginx isolation**: Separate server block, only handles `kindered.enorviaglobal.com`
- **No shared dependencies**: All Python deps inside Docker image
- **No systemd conflicts**: Uses Docker's restart policy, not systemd services
- **Config backup**: Every deploy backs up existing configs before changes
- **Nginx validated**: `nginx -t` runs before any reload
