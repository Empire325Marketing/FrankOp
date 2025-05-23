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
