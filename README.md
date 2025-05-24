# FrankOp

Automation utilities for deployment and monitoring of Fluent Bit and Filebeat across multiple nodes.

## Required Environment Variables

Before running the utilities or the web application, set the following environment variables:

- `SSH_PASSWORD` – password used by the deployment and monitoring scripts when connecting to the VPS nodes.
- `PINARCH_TOKEN` – secret token checked by `app.py` when clients authenticate via `/api/login`.

Example:

```bash
export SSH_PASSWORD="<your_ssh_password>"
export PINARCH_TOKEN="<your_pinarch_token>"
scripts/start_trinity_frontend.sh
```

`start_trinity_frontend.sh` builds and starts the Next.js app located in
`var/www/html/james/ultimate_ui`.

## Directory overview
- `fluent-bit/` – Fluent Bit configuration files.
- `filebeat/` – Filebeat configuration files.
- `scripts/` – Automation scripts for deployment, rollback, health checks, testing and Filebeat setup.
- `etc/addresses.env` – Example environment file providing IP addresses for all scripts.

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

## Configuring IP addresses

All deployment and monitoring scripts read the list of VPS nodes and the
address of the core aggregator from environment variables. An example
file `etc/addresses.env` is provided. Source this file (or define the
variables manually) before running any script:

```bash
source etc/addresses.env
export NODES   # comma separated list of node IPs
export CORE_VPS
```

Nginx and Fluent Bit configuration files use the variables `UI_HOST`,
`UI_PORT`, `API_HOST`, `API_PORT` and `FLUENT_LISTEN_ADDR`. When deploying
these configs you can apply `envsubst` to substitute the values:

```bash
envsubst < etc/nginx/sites-available/trinity-complete > /etc/nginx/sites-available/trinity-complete
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

## Fixing Missing SSL Configuration

If Nginx fails to start because the LetsEncrypt files referenced in
`/etc/nginx/sites-available/trinity-final.conf` are absent, run:

```bash
sudo scripts/fix_nginx_ssl.sh [domain]
```

Pass the domain as an argument or via the `DOMAIN` environment variable to control which
certificate directory under `/etc/letsencrypt/live` is checked. If omitted, it defaults to
`325automations.com`. The script backs up the configuration, comments out the missing include
lines and any SSL directives if the certificate is absent, tests the configuration and reloads Nginx.

## Trinity AI Web Interface

A minimal web interface is provided as a starting point for the future
"ultimate" Trinity AI UI. The backend API is implemented with Flask in
`app.py` and exposes a `/api/chat` endpoint. The production Next.js 14 frontend
resides in `var/www/html/james/ultimate_ui/`.

### Running locally

1. Install the Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Start the production API using Gunicorn:
   ```bash
   scripts/start_trinity_server.sh
   ```
3. In the `var/www/html/james/ultimate_ui/` directory install the frontend dependencies:
   ```bash
   npm install
   ```
   To start the development server run:
   ```bash
   npm run dev
   ```
4. Build and launch the production UI inside the same directory:
   ```bash
   NODE_OPTIONS=--max-old-space-size=4096 npm run build
   npm run start
   ```
   Alternatively, execute `scripts/start_trinity_frontend.sh` from the project
   root which performs these steps automatically.

The frontend will send chat prompts to `http://localhost:5001/api/chat` and
display the result.
