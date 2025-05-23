#!/usr/bin/env bash
set -euo pipefail

NODES=(srv803495 srv832635 srv832638 srv832660 srv832662)
CORE_VPS=104.255.9.187
CONTAINER=d82c6a1a4730
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

log "Deploying configuration to core container"
scp "${CONFIG_DIR}/fluent-bit.conf" "${CORE_VPS}:/tmp/fluent-bit.conf"
ssh "${CORE_VPS}" "docker cp /tmp/fluent-bit.conf ${CONTAINER}:/fluent-bit/etc/fluent-bit.conf && docker exec ${CONTAINER} /fluent-bit/bin/fluent-bit -c /fluent-bit/etc/fluent-bit.conf"
log "Deployment finished"
