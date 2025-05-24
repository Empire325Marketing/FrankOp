#!/usr/bin/env bash
set -euo pipefail

# Launch the production Trinity AI API using Gunicorn.
BIND_ADDR="${BIND_ADDR:-0.0.0.0}" 
BIND_PORT="${BIND_PORT:-5001}"
exec gunicorn --bind "${BIND_ADDR}:${BIND_PORT}" --workers 4 app:app
