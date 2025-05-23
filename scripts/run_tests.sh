#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Validating shell scripts"
find scripts -name '*.sh' -print0 | xargs -0 bash -n
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/*.sh
fi

if command -v fluent-bit >/dev/null 2>&1; then
  log "Validating Fluent Bit configuration"
  fluent-bit -c fluent-bit/fluent-bit.conf --dry-run
else
  log "Fluent Bit not installed; skipping configuration validation"
fi
log "Tests completed"
