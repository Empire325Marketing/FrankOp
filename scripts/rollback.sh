#!/usr/bin/env bash
set -euo pipefail

NODES=(srv803495 srv832635 srv832638 srv832660 srv832662)
CORE_VPS=104.255.9.187
CONTAINER=d82c6a1a4730
BACKUP_DIR=/var/backups/fluent-bit

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

for NODE in "${NODES[@]}"; do
  log "Rolling back configuration on ${NODE}"
  LATEST=$(ssh "$NODE" "ls -t ${BACKUP_DIR}/fluent-bit.conf.* 2>/dev/null | head -n 1")
  if [[ -z "$LATEST" ]]; then
    log "ERROR: no backup found on ${NODE}" && continue
  fi
  ssh "$NODE" "sudo cp ${LATEST} /etc/fluent-bit/fluent-bit.conf && sudo systemctl restart fluent-bit"
  log "Rollback completed on ${NODE}"
done

log "Rolling back configuration on core container"
ssh "$CORE_VPS" "docker cp ${CONTAINER}:${BACKUP_DIR}/fluent-bit.conf /tmp/fluent-bit.conf && docker exec ${CONTAINER} /fluent-bit/bin/fluent-bit -c /tmp/fluent-bit.conf"
log "Rollback finished"
