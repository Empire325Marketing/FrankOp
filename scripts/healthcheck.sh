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
