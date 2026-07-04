#!/bin/bash
set -euo pipefail

# ============================================================
# Kindered Deployment Script
# Deploys kindered.enorviaglobal.com on isolated Docker stack
# ============================================================

APP_NAME="kindered"
APP_DIR="/opt/kindered"
NGINX_CONF="/etc/nginx/sites-available/kindered.enorviaglobal.com"
NGINX_ENABLED="/etc/nginx/sites-enabled/kindered.enorviaglobal.com"
DOMAIN="kindered.enorviaglobal.com"
PORT=8901

echo "================================================"
echo "  Kindered Deployment - $(date)"
echo "================================================"

# Pre-flight checks
echo ""
echo "[1/8] Pre-flight checks..."
echo "  - Checking Docker..."
docker --version || { echo "ERROR: Docker not installed"; exit 1; }
docker compose version || { echo "ERROR: Docker Compose not available"; exit 1; }

echo "  - Checking port ${PORT} availability..."
if ss -tlnp | grep -q ":${PORT} "; then
    echo "WARNING: Port ${PORT} is already in use. Checking if it's our container..."
    if docker ps --format '{{.Names}}' | grep -q "kindered-app"; then
        echo "  - Existing Kindered container found. Will be replaced."
    else
        echo "ERROR: Port ${PORT} is in use by another service!"
        exit 1
    fi
fi

# Backup existing configs
echo ""
echo "[2/8] Backing up existing configurations..."
BACKUP_DIR="/opt/kindered/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -f "$NGINX_CONF" ]; then
    cp "$NGINX_CONF" "$BACKUP_DIR/nginx.conf.bak"
    echo "  - Backed up existing Nginx config"
fi
if [ -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env" "$BACKUP_DIR/.env.bak"
    echo "  - Backed up existing .env"
fi

# Deploy application
echo ""
echo "[3/8] Deploying application to ${APP_DIR}..."
mkdir -p "$APP_DIR"
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.db' \
    --exclude='.env' --exclude='.venv' --exclude='venv' \
    "$(dirname "$(dirname "$(readlink -f "$0")")")/" "$APP_DIR/"

# Environment configuration
echo ""
echo "[4/8] Checking environment configuration..."
if [ ! -f "$APP_DIR/.env" ]; then
    echo "  - Creating .env from template..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "  WARNING: Please edit $APP_DIR/.env with your AWS credentials!"
    echo "  Then re-run this script."
    exit 1
else
    echo "  - .env file exists"
fi

# Build and start Docker container
echo ""
echo "[5/8] Building and starting Docker container..."
cd "$APP_DIR"
docker compose down --remove-orphans 2>/dev/null || true
docker compose build --no-cache
docker compose up -d

echo "  - Waiting for container to be healthy..."
sleep 5
for i in {1..30}; do
    if curl -sf http://127.0.0.1:${PORT}/health > /dev/null 2>&1; then
        echo "  - Container healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: Container failed to start. Checking logs..."
        docker compose logs --tail=50
        exit 1
    fi
    sleep 2
done

# Nginx configuration
echo ""
echo "[6/8] Configuring Nginx..."
cp "$APP_DIR/deploy/nginx/kindered.enorviaglobal.com.conf" "$NGINX_CONF"

if [ ! -L "$NGINX_ENABLED" ]; then
    ln -s "$NGINX_CONF" "$NGINX_ENABLED"
fi

echo "  - Testing Nginx configuration..."
nginx -t || {
    echo "ERROR: Nginx configuration test failed!"
    echo "  Restoring backup..."
    if [ -f "$BACKUP_DIR/nginx.conf.bak" ]; then
        cp "$BACKUP_DIR/nginx.conf.bak" "$NGINX_CONF"
    else
        rm -f "$NGINX_CONF" "$NGINX_ENABLED"
    fi
    exit 1
}

# SSL Certificate
echo ""
echo "[7/8] SSL Certificate..."
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "  - Obtaining SSL certificate..."
    # Temporarily use HTTP-only config for certbot
    cat > "$NGINX_CONF" <<TMPCONF
server {
    listen 80;
    server_name $DOMAIN;
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
TMPCONF
    nginx -t && systemctl reload nginx
    certbot certonly --webroot -w /var/www/html -d "$DOMAIN" --non-interactive --agree-tos --email admin@enorviaglobal.com || {
        echo "WARNING: SSL cert failed. App is available on HTTP only."
    }
    # Restore full config with SSL
    cp "$APP_DIR/deploy/nginx/kindered.enorviaglobal.com.conf" "$NGINX_CONF"
    nginx -t && systemctl reload nginx
else
    echo "  - SSL certificate already exists"
    systemctl reload nginx
fi

# Final verification
echo ""
echo "[8/8] Final verification..."
echo "  - Docker status:"
docker compose ps
echo ""
echo "  - Health check:"
curl -sf http://127.0.0.1:${PORT}/health && echo ""

echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "  URL: https://${DOMAIN}"
echo "  Health: https://${DOMAIN}/health"
echo "  Backup: ${BACKUP_DIR}"
echo "================================================"
