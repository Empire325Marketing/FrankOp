#!/usr/bin/env bash
set -euo pipefail

NODES=(srv803495 srv832635 srv832638 srv832660 srv832662)
CORE_VPS=104.255.9.187
CONTAINER=d82c6a1a4730
PORT=8000

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

for NODE in "${NODES[@]}"; do
  if nc -z "$NODE" "$PORT"; then
    log "${NODE} Fluent Bit port ${PORT} reachable"
  else
    log "ERROR: ${NODE} Fluent Bit port ${PORT} unreachable"
  fi
 done

log "Checking container health"
ssh "$CORE_VPS" "docker exec ${CONTAINER} curl -sf http://localhost:${PORT}/health" && log "Container healthy" || log "ERROR: Container health check failed"
