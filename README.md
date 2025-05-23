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

Deploy configuration to all nodes:
```bash
scripts/deploy.sh
```

Deploy Filebeat configuration and configure Fluent Bit HTTP input:
```bash
scripts/deploy_filebeat.py
```

Check health of each node and the core container:
```bash
scripts/healthcheck.sh
```

If deployment fails, rollback to previous configuration:
```bash
scripts/rollback.sh
```
