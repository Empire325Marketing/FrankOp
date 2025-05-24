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

NGINX_SITE=/etc/nginx/sites-available/trinity
REPO_SITE="$(dirname "$0")/../etc/nginx/sites-available/trinity-nuclear"
if [ -f "$REPO_SITE" ]; then
  log "Installing Trinity Nginx configuration"
  sudo cp "$REPO_SITE" "$NGINX_SITE"
  sudo ln -sf "$NGINX_SITE" /etc/nginx/sites-enabled/trinity
  sudo rm -f /etc/nginx/sites-enabled/default
  sudo nginx -t
  sudo systemctl reload nginx
else
  log "Trinity Nginx configuration not found in repository"
fi

log "External access configuration completed"
