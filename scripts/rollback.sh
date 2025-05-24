#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/etc/addresses.env"
if [ -f "$CONFIG_FILE" ]; then
  # shellcheck source=/dev/null
  source "$CONFIG_FILE"
fi

if [ -z "${NODES:-}" ] || [ -z "${CORE_VPS:-}" ]; then
  echo "NODES and CORE_VPS must be set via environment or $CONFIG_FILE" >&2
  exit 1
fi
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
