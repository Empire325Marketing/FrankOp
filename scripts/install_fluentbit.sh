#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

if command -v fluent-bit >/dev/null 2>&1; then
  log "Fluent Bit already installed"
  exit 0
fi

log "Adding Fluent Bit repository (Ubuntu 24.04 compatibility)"
if [ ! -f /usr/share/keyrings/fluentbit-keyring.gpg ]; then
  curl -fsSL https://packages.fluentbit.io/fluentbit.key | sudo gpg --dearmor -o /usr/share/keyrings/fluentbit-keyring.gpg
fi

echo "deb [signed-by=/usr/share/keyrings/fluentbit-keyring.gpg] https://packages.fluentbit.io/ubuntu/noble noble main" | sudo tee /etc/apt/sources.list.d/fluent-bit.list >/dev/null
sudo apt-get update

if ! sudo apt-get install -y fluent-bit; then
  log "apt install failed, falling back to snap"
  sudo snap install fluent-bit --classic
fi

sudo systemctl enable fluent-bit
sudo systemctl restart fluent-bit
log "Fluent Bit installation complete"
