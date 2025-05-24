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

log "Rolling back configuration on core VPS"
ssh "$CORE_VPS" "LATEST=\$(ls -t ${BACKUP_DIR}/fluent-bit.conf.* 2>/dev/null | head -n 1); if [ -n \"$LATEST\" ]; then sudo cp \"$LATEST\" /etc/fluent-bit/fluent-bit.conf && sudo systemctl restart fluent-bit; fi"
log "Rollback finished"
