#!/usr/bin/env bash
set -euo pipefail

# Build and launch the Trinity UI Next.js app.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT/var/www/html/james/ultimate_ui"
cd "$APP_DIR"

if [ ! -d .next ]; then
  npm install
  NODE_OPTIONS=--max-old-space-size=4096 npm run build
fi

exec npm run start

