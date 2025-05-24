#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/etc/addresses.env"
if [ -f "$CONFIG_FILE" ]; then
  # shellcheck source=/dev/null
  source "$CONFIG_FILE"
fi

: "${NODES:=31.97.13.92,31.97.13.95,31.97.13.100,31.97.13.102,31.97.13.104,31.97.13.108}"
: "${CORE_VPS:=145.223.73.4}"
IFS=',' read -r -a NODES <<< "$NODES"
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/fluent-bit"
BACKUP_DIR=/var/backups/fluent-bit

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

for NODE in "${NODES[@]}"; do
  log "Backing up Fluent Bit config on ${NODE}"
  ssh "$NODE" "sudo mkdir -p ${BACKUP_DIR} && sudo cp /etc/fluent-bit/fluent-bit.conf ${BACKUP_DIR}/fluent-bit.conf.$(date +%s)"
  log "Deploying new config to ${NODE}"
  scp "${CONFIG_DIR}/fluent-bit.conf" "$NODE:/tmp/fluent-bit.conf"
  ssh "$NODE" "sudo mv /tmp/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf && sudo systemctl restart fluent-bit"
  log "Deployment complete on ${NODE}"
done

log "Deploying configuration to core VPS"
scp "${CONFIG_DIR}/fluent-bit.conf" "${CORE_VPS}:/tmp/fluent-bit.conf"
ssh "${CORE_VPS}" "sudo mv /tmp/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf && sudo systemctl restart fluent-bit"
log "Deployment finished"
