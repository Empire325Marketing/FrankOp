# FrankOp

Automation utilities for deployment and monitoring of Fluent Bit and Filebeat across multiple nodes.

## Directory overview
- `fluent-bit/` – Fluent Bit configuration files.
- `filebeat/` – Filebeat configuration files.
- `scripts/` – Automation scripts for deployment, rollback, health checks, testing and Filebeat setup.

## Usage

Run automated tests:
```bash
scripts/run_tests.sh
```

Install Fluent Bit on the central VPS:
```bash
scripts/install_fluentbit.sh
```

Deploy configuration to all nodes:
```bash
scripts/deploy.sh
```

Deploy Filebeat configuration and configure Fluent Bit HTTP input:
```bash
scripts/deploy_filebeat.py
```

Recover Filebeat registry corruption and redeploy across all nodes:
```bash
scripts/recover_and_deploy.py
```

Run a one-shot health check and rotate the combined log if it grows too large:
```bash
scripts/monitor.py
```

Check health of each node and the core VPS:
```bash
scripts/healthcheck.sh
```

If deployment fails, rollback to previous configuration:
```bash
scripts/rollback.sh
```

Run an end-to-end test to confirm log forwarding:
```bash
scripts/e2e_test.py
```

## Reverse SSH tunnel setup

To aggregate logs from remote VPS nodes using reverse SSH tunnels:

1. On the RunPod container, start the tunnel manager which listens on
   ports 5045-5049 and aggregates all logs to `/tmp/vps_combined.log`:

```bash
scripts/runpod_tunnel_manager.sh
```

2. On each VPS node, establish a persistent tunnel using `autossh`.
   Specify the remote port assigned to the node when invoking the
   setup script. Example for port 5045:

```bash
scripts/vps_tunnel_setup.sh 5045
```

Filebeat on the VPS should be configured with
`filebeat/filebeat_tunnel.yml` so that logs are sent through the local
port `5044` into the SSH tunnel.

## Trinity AI Integration

`trinity_ai.py` provides a unified Python interface to three AI backends:

- **ChatGPT** via the standard OpenAI API.
- **Gemini** via an OpenAI-compatible endpoint (`https://generativelanguage.googleapis.com/v1beta/openai/`).
- **OpenEvolve** for GitHub workflow automation (placeholder implementation).

Example usage:

```bash
python3 trinity_ai.py
```

The script will read API keys from the environment variables `OPENAI_API_KEY`,
`GEMINI_API_KEY`, and `OPENEVOLVE_TOKEN`.

## Enabling External Access

The `scripts/enable_external_access.sh` helper configures firewall rules and updates the default Nginx site so the Trinity AI web interface can be reached from the internet.
Run it on the target VPS with root privileges after deployment:

```bash
sudo scripts/enable_external_access.sh
```

This script enables ports 80 and 443 via `ufw` and `iptables`, ensures Nginx listens on all interfaces, and reloads the server.

## Trinity AI Web Interface

A minimal web interface is provided as a starting point for the future
"ultimate" Trinity AI UI. The backend API is implemented with Flask in
`app.py` and exposes a `/api/chat` endpoint. A Next.js 14 frontend lives in
`frontend/`.

### Running locally

1. Install the Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Start the production API using Gunicorn:
   ```bash
   scripts/start_trinity_server.sh
   ```
3. In the `frontend/` directory install dependencies and run the dev server:
   ```bash
   npm install
   npm run dev
   ```

The frontend will send chat prompts to `http://localhost:5001/api/chat` and
display the result.
