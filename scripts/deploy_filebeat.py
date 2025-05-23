#!/usr/bin/env python3
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "SDAasdsa23..dsS")
FILEBEAT_CONFIG = Path(__file__).resolve().parents[1] / "filebeat" / "corrected_filebeat.yml"
FLUENT_BIT_CONFIG = Path(__file__).resolve().parents[1] / "fluent-bit" / "fluent-bit.conf"

# Worker nodes only; logs are forwarded to 145.223.73.4
NODES = [
    "31.97.13.92",
    "31.97.13.95",
    "31.97.13.100",
    "31.97.13.102",
]
CORE_VPS = "104.255.9.187"
CONTAINER = "d82c6a1a4730"


def log(msg: str):
    print(f"[{os.getpid()}] {msg}")


def run_cmd(cmd: list):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {' '.join(cmd)}\n{e.stderr}")
        raise


def ssh_cmd(host: str, command: str):
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


def scp_file(host: str, source: Path, dest: str):
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
    return run_cmd(cmd)


def deploy_filebeat(node: str):
    log(f"Deploying Filebeat to {node}")
    ssh_cmd(node, "systemctl stop filebeat || true")
    ssh_cmd(node, "rm -rf /var/lib/filebeat/registry")
    backup_cmd = "cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.bak.$(date +%s) || true"
    ssh_cmd(node, backup_cmd)
    scp_file(node, FILEBEAT_CONFIG, "/tmp/filebeat.yml")
    ssh_cmd(node, "mv /tmp/filebeat.yml /etc/filebeat/filebeat.yml")
    ssh_cmd(node, "systemctl daemon-reload")
    ssh_cmd(node, "systemctl start filebeat")
    status = ssh_cmd(node, "systemctl is-active filebeat")
    log(f"Filebeat status on {node}: {status.strip()}")


def configure_fluentbit():
    log("Configuring Fluent Bit on core VPS")
    backup_cmd = "cp /fluent-bit/etc/fluent-bit.conf /fluent-bit/etc/fluent-bit.conf.bak.$(date +%s)"
    ssh_cmd(CORE_VPS, backup_cmd)
    scp_file(CORE_VPS, FLUENT_BIT_CONFIG, "/tmp/fluent-bit.conf")
    ssh_cmd(CORE_VPS, f"docker cp /tmp/fluent-bit.conf {CONTAINER}:/fluent-bit/etc/fluent-bit.conf")
    ssh_cmd(CORE_VPS, f"docker exec {CONTAINER} pkill -f fluent-bit || true")
    ssh_cmd(CORE_VPS, f"docker exec -d {CONTAINER} /fluent-bit/bin/fluent-bit -c /fluent-bit/etc/fluent-bit.conf")
    log("Fluent Bit configuration updated")


def main():
    if not FILEBEAT_CONFIG.exists():
        log(f"Filebeat configuration not found: {FILEBEAT_CONFIG}")
        sys.exit(1)

    with ThreadPoolExecutor(max_workers=len(NODES)) as executor:
        futures = [executor.submit(deploy_filebeat, node) for node in NODES]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                log(f"Error: {exc}")
                sys.exit(1)

    configure_fluentbit()
    log("Deployment complete")


if __name__ == "__main__":
    main()
