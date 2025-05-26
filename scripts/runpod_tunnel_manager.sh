#!/usr/bin/env bash
# runpod_tunnel_manager.sh - Accepts reverse SSH tunnels and aggregates logs
#
# This script runs on the RunPod container. It starts Fluent Bit to
# collect logs on port 5044 and forwards ports 5045-5051 to this
# internal collector. Each VPS (six in total) establishes an SSH
# tunnel to one of these ports. Logs from all VPS nodes are combined into a single
# /tmp/vps_combined.log file.

set -euo pipefail

# Ports assigned to incoming tunnels
TUNNEL_PORTS=(5045 5046 5047 5048 5049 5050 5051)

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

check_dependency() {
  command -v "$1" >/dev/null 2>&1 || { echo "$1 is required" >&2; exit 1; }
}

main() {
  check_dependency fluent-bit
  check_dependency socat

  # Allow overriding the listen address for the Fluent Bit HTTP input
  # Default to 0.0.0.0 so it accepts connections from all forwarded ports
  : "${FLUENT_LISTEN_ADDR:=0.0.0.0}"
  export FLUENT_LISTEN_ADDR

  log "Starting Fluent Bit aggregator"
  fluent-bit -c fluent-bit/fluent-bit.conf &
  FLUENT_PID=$!

  log "Forwarding tunnel ports to local collector"
  for port in "${TUNNEL_PORTS[@]}"; do
    socat TCP-LISTEN:"$port",reuseaddr,fork TCP:localhost:5044 &
  done

  trap 'log "Stopping"; kill $FLUENT_PID; pkill -P $$ socat' INT TERM
  wait
}

main "$@"
