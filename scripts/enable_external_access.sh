#!/usr/bin/env bash
# Configure firewall and Nginx for external access to the Trinity AI interface

set -euo pipefail

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Configuring firewall rules"
if command -v ufw >/dev/null 2>&1; then
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw allow ssh
  sudo ufw --force enable
else
  log "ufw not installed; skipping"
fi

if command -v iptables >/dev/null 2>&1; then
  sudo iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || \
    sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
  sudo iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || \
    sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
fi

NGINX_CONF=/etc/nginx/sites-available/default
if [ -f "$NGINX_CONF" ]; then
  log "Updating Nginx configuration"
  sudo sed -i 's/server_name _;/server_name 325automations.com;/' "$NGINX_CONF"
  sudo sed -i '/listen 80 default_server;/a \\tlisten [::]:80 default_server;' "$NGINX_CONF"
  sudo nginx -t
  sudo systemctl reload nginx
else
  log "Nginx configuration not found; skipping"
fi

log "External access configuration completed"
