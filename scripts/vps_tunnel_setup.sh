#!/usr/bin/env bash
# vps_tunnel_setup.sh - Create a persistent SSH tunnel from a VPS node to RunPod
#
# Usage: vps_tunnel_setup.sh <remote_port>
# Each VPS is assigned a unique remote_port. Example mapping:
#   198.51.100.5 -> 5045
#   192.0.2.10   -> 5046
#   192.0.2.11   -> 5047
#   192.0.2.12   -> 5048
#   192.0.2.13   -> 5049
#   192.0.2.14   -> 5050
#   192.0.2.15   -> 5051
#
# The script configures autossh to expose local Filebeat (localhost:5044)
# to RunPod on the given remote port. autossh automatically restarts the
# tunnel if the connection drops.

set -euo pipefail

RUNPOD_HOST="root@d82c6a1a4730"
RUNPOD_PORT=22
SSH_PASSWORD="${SSH_PASSWORD:?SSH_PASSWORD environment variable not set}"
LOCAL_PORT=5044

usage() {
  echo "Usage: $0 <remote_port>" >&2
  exit 1
}

check_dependency() {
  command -v "$1" >/dev/null 2>&1 || { echo "$1 is required" >&2; exit 1; }
}

if [ $# -ne 1 ]; then
  usage
fi
REMOTE_PORT=$1

main() {
  check_dependency autossh
  check_dependency sshpass

  export AUTOSSH_GATETIME=0
  export AUTOSSH_POLL=30

  sshpass -p "$SSH_PASSWORD" \
    autossh -M 0 -N \
    -o "ServerAliveInterval=60" \
    -o "ServerAliveCountMax=3" \
    -o "ExitOnForwardFailure=yes" \
    -o "StrictHostKeyChecking=no" \
    -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" \
    -p "$RUNPOD_PORT" "$RUNPOD_HOST"
}

main "$@"
