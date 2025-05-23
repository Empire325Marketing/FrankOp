#!/usr/bin/env bash
set -euo pipefail

NODES=(31.97.13.92 31.97.13.95 31.97.13.100 31.97.13.102)
CORE_VPS=145.223.73.4
PORT=5044

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

for NODE in "${NODES[@]}"; do
  if ssh "$NODE" "systemctl is-active filebeat >/dev/null"; then
    log "${NODE} filebeat active"
  else
    log "ERROR: ${NODE} filebeat inactive"
  fi
done

log "Checking Fluent Bit port on core VPS"
if nc -z "$CORE_VPS" "$PORT"; then
  log "Core VPS port ${PORT} reachable"
else
  log "ERROR: Core VPS port ${PORT} unreachable"
fi
