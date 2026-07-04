#!/bin/bash
set -euo pipefail

# ============================================================
# Kindered Rollback Script
# Rolls back deployment to a previous state
# ============================================================

APP_DIR="/opt/kindered"
NGINX_CONF="/etc/nginx/sites-available/kindered.enorviaglobal.com"
NGINX_ENABLED="/etc/nginx/sites-enabled/kindered.enorviaglobal.com"

echo "================================================"
echo "  Kindered Rollback - $(date)"
echo "================================================"

# Find latest backup
BACKUP_DIR=$(ls -dt "$APP_DIR/backups/"*/ 2>/dev/null | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "No backups found. Cannot rollback."
    echo "To fully remove Kindered:"
    echo "  1. docker compose -f $APP_DIR/docker-compose.yml down"
    echo "  2. rm -f $NGINX_CONF $NGINX_ENABLED"
    echo "  3. nginx -t && systemctl reload nginx"
    exit 1
fi

echo "Rolling back using backup: $BACKUP_DIR"

# Stop current container
echo "[1/4] Stopping current container..."
cd "$APP_DIR"
docker compose down 2>/dev/null || true

# Restore Nginx config
echo "[2/4] Restoring Nginx configuration..."
if [ -f "${BACKUP_DIR}/nginx.conf.bak" ]; then
    cp "${BACKUP_DIR}/nginx.conf.bak" "$NGINX_CONF"
    nginx -t && systemctl reload nginx
    echo "  - Nginx config restored and reloaded"
else
    echo "  - No Nginx backup found. Removing config..."
    rm -f "$NGINX_CONF" "$NGINX_ENABLED"
    nginx -t && systemctl reload nginx
fi

# Restore environment
echo "[3/4] Restoring environment..."
if [ -f "${BACKUP_DIR}/.env.bak" ]; then
    cp "${BACKUP_DIR}/.env.bak" "$APP_DIR/.env"
    echo "  - .env restored"
fi

# Rebuild previous version
echo "[4/4] Rebuilding previous container..."
docker compose build
docker compose up -d

echo ""
echo "================================================"
echo "  Rollback Complete!"
echo "  Verify: curl http://127.0.0.1:8901/health"
echo "================================================"
