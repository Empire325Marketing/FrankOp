# FrankOp

Automation utilities for deployment and monitoring of Fluent Bit across multiple nodes.

## Directory overview
- `fluent-bit/` – Fluent Bit configuration files.
- `scripts/` – Automation scripts for deployment, rollback, health checks and testing.

## Usage

Run automated tests:
```bash
scripts/run_tests.sh
```

Deploy configuration to all nodes:
```bash
scripts/deploy.sh
```

Check health of each node and the core container:
```bash
scripts/healthcheck.sh
```

If deployment fails, rollback to previous configuration:
```bash
scripts/rollback.sh
```
