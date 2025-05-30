#!/usr/bin/env python3
"""Recover Filebeat services and deploy configuration across all nodes."""
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
if not SSH_PASSWORD:
    raise RuntimeError("SSH_PASSWORD environment variable not set")

def load_addresses() -> None:
    if os.getenv("NODES") and os.getenv("CORE_VPS"):
        return
    env_file = Path(__file__).resolve().parents[1] / "etc" / "addresses.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("NODES=") and not os.getenv("NODES"):
                    os.environ["NODES"] = line.split("=", 1)[1].strip().strip('"')
                elif line.startswith("CORE_VPS=") and not os.getenv("CORE_VPS"):
                    os.environ["CORE_VPS"] = line.split("=", 1)[1].strip().strip('"')


load_addresses()

nodes_env = os.getenv("NODES")
core_vps = os.getenv("CORE_VPS")
if not nodes_env or not core_vps:
    raise RuntimeError("NODES and CORE_VPS must be set via environment or addresses.env")

NODES = nodes_env.split(",")
CORE_VPS = core_vps

FILEBEAT_CONFIG = Path(__file__).resolve().parents[1] / "filebeat" / "corrected_filebeat.yml"
FLUENT_BIT_CONFIG = Path(__file__).resolve().parents[1] / "fluent-bit" / "fluent-bit.conf"


def log(msg: str) -> None:
    ts = datetime.utcnow().isoformat()
    print(f"[{ts}] {msg}")


def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
        raise RuntimeError(result.stderr)
    return result.stdout


def ssh_cmd(host: str, command: str) -> str:
    cmd = [
        "sshpass",
        "-p",
        SSH_PASSWORD,
        "ssh",
        f"{SSH_USER}@{host}",
        "-o",
        "StrictHostKeyChecking=no",
        command,
    ]
    return run_cmd(cmd)


def scp_file(host: str, source: Path, dest: str) -> None:
    cmd = [
        "sshpass",
        "-p",
        SSH_PASSWORD,
        "scp",
        "-o",
        "StrictHostKeyChecking=no",
        str(source),
        f"{SSH_USER}@{host}:{dest}",
    ]
    run_cmd(cmd)


def recover_node(node: str) -> None:
    """Recover Filebeat on a single node and deploy configuration."""
    log(f"Starting recovery on {node}")
    # Stop service and disable to clear systemd throttling
    ssh_cmd(node, "systemctl stop filebeat || true")
    ssh_cmd(node, "systemctl disable filebeat || true")
    ssh_cmd(node, "systemctl reset-failed filebeat || true")

    # Remove registry and lock files
    ssh_cmd(node, "rm -rf /var/lib/filebeat/registry")
    ssh_cmd(node, "rm -f /var/lib/filebeat/filebeat.lock")

    # Recreate directory structure with root ownership
    ssh_cmd(node, "mkdir -p /var/lib/filebeat /var/log/filebeat")
    ssh_cmd(node, "chown -R root:root /var/lib/filebeat /var/log/filebeat")

    # Backup existing configuration before deploying new one
    ssh_cmd(node, "cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.bak.$(date +%s) || true")

    scp_file(node, FILEBEAT_CONFIG, "/tmp/filebeat.yml")
    ssh_cmd(node, "mv /tmp/filebeat.yml /etc/filebeat/filebeat.yml")
    ssh_cmd(node, "systemctl daemon-reload")
    ssh_cmd(node, "systemctl enable filebeat")
    ssh_cmd(node, "systemctl start filebeat")

    # Verify service health
    status = ssh_cmd(node, "systemctl is-active filebeat").strip()
    log(f"Filebeat status on {node}: {status}")

    # Generate a test log line to trigger forwarding
    ssh_cmd(node, f"echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) recovery test from {node}\" >> /var/log/test.log")


def configure_fluentbit() -> None:
    log("Configuring Fluent Bit on core VPS")
    ssh_cmd(CORE_VPS, "cp /etc/fluent-bit/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf.bak.$(date +%s) || true")
    scp_file(CORE_VPS, FLUENT_BIT_CONFIG, "/tmp/fluent-bit.conf")
    ssh_cmd(CORE_VPS, "mv /tmp/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf")
    ssh_cmd(CORE_VPS, "systemctl daemon-reload")
    ssh_cmd(CORE_VPS, "systemctl enable fluent-bit")
    ssh_cmd(CORE_VPS, "systemctl restart fluent-bit")
    log("Fluent Bit restarted")


def verify_logs() -> None:
    log("Verifying combined logs on core VPS")
    log_data = ssh_cmd(CORE_VPS, "cat /tmp/vps_combined.log || true")
    for node in NODES:
        if node in log_data:
            log(f"Log entry from {node} detected")
        else:
            log(f"WARNING: no log entry from {node}")


def main() -> None:
    if not FILEBEAT_CONFIG.exists():
        log(f"Missing Filebeat configuration: {FILEBEAT_CONFIG}")
        raise SystemExit(1)

    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(NODES)) as exe:
        futures = {exe.submit(recover_node, n): n for n in NODES}
        for fut in as_completed(futures):
            node = futures[fut]
            try:
                fut.result()
                results[node] = "success"
            except Exception as exc:
                results[node] = f"error: {exc}"

    configure_fluentbit()
    verify_logs()

    log("Summary:")
    for node, res in results.items():
        log(f"  {node}: {res}")

    log("Recovery and deployment complete")


if __name__ == "__main__":
    main()
