#!/usr/bin/env bash
# fix_nginx_ssl.sh - Disable missing LetsEncrypt includes and SSL directives

set -euo pipefail

usage() {
  echo "Usage: $0 [DOMAIN]" >&2
  echo "Disable SSL directives when LetsEncrypt files are missing." >&2
  echo "DOMAIN specifies the certificate directory under /etc/letsencrypt/live." >&2
  echo "It can also be provided via the DOMAIN environment variable." >&2
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

CONFIG_FILE="/etc/nginx/sites-available/trinity-final.conf"
# Domain used to locate LetsEncrypt certificates. Can be overridden via the
# DOMAIN environment variable or passed as the first argument.
DOMAIN="${1:-${DOMAIN:-325automations.com}}"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
BACKUP_FILE="${CONFIG_FILE}.backup_${TIMESTAMP}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run this script with sudo or as root." >&2
  exit 1
fi

log "Backing up ${CONFIG_FILE} to ${BACKUP_FILE}"
cp "$CONFIG_FILE" "$BACKUP_FILE"

log "Commenting out missing SSL include lines"
sed -i \
  -e 's@^\( *\)include /etc/letsencrypt/options-ssl-nginx.conf;@#&@' \
  -e 's@^\( *\)ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;@#&@' \
  "$CONFIG_FILE"

if [ ! -f "${CERT_DIR}/fullchain.pem" ] || [ ! -f "${CERT_DIR}/privkey.pem" ]; then
  log "Certificate files not found; disabling SSL directives"
  sed -i \
    -e 's@^\( *\)ssl_certificate .*;@#&@' \
    -e 's@^\( *\)ssl_certificate_key .*;@#&@' \
    -e 's@^\( *\)listen \([^ ]*\) ssl;@#&@' \
    "$CONFIG_FILE"
fi

log "Testing new Nginx configuration"
if nginx -t; then
  log "Configuration test succeeded. Reloading Nginx"
  if nginx -s reload 2>/dev/null; then
    log "Nginx reloaded successfully"
  else
    log "Reload failed. Trying 'service nginx restart'"
    if service nginx restart; then
      log "Nginx restarted successfully"
    else
      log "Failed to restart Nginx. Please investigate further"
      exit 1
    fi
  fi
  log "Check Nginx: sudo ss -tlnp | grep nginx"
else
  log "Configuration test failed! Restore the backup with:"
  log "sudo cp \"$BACKUP_FILE\" \"$CONFIG_FILE\""
  exit 1
fi

log "Script completed"
