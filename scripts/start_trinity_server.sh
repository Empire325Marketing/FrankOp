#!/usr/bin/env bash
set -euo pipefail

# Launch the production Trinity AI API using Gunicorn.
exec gunicorn --bind 0.0.0.0:5001 --workers 4 app:app
