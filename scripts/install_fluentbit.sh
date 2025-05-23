#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/fluent-bit"
FLUENT_CONF="${CONFIG_DIR}/fluent-bit.conf"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Installing Fluent Bit"
apt-get update
apt-get install -y fluent-bit

log "Deploying configuration"
cp "${FLUENT_CONF}" /etc/fluent-bit/fluent-bit.conf
systemctl enable fluent-bit
systemctl restart fluent-bit

log "Fluent Bit setup complete"

