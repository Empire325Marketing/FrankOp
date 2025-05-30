#!/usr/bin/env python3
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
if not SSH_PASSWORD:
    raise RuntimeError("SSH_PASSWORD environment variable not set")
FILEBEAT_CONFIG = Path(__file__).resolve().parents[1] / "filebeat" / "corrected_filebeat.yml"
FLUENT_BIT_CONFIG = Path(__file__).resolve().parents[1] / "fluent-bit" / "fluent-bit.conf"

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
    backup_cmd = "cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.bak.$(date +%s) || true"
    ssh_cmd(node, backup_cmd)
    scp_file(node, FILEBEAT_CONFIG, "/tmp/filebeat.yml")
    ssh_cmd(node, "mv /tmp/filebeat.yml /etc/filebeat/filebeat.yml")
    ssh_cmd(node, "systemctl restart filebeat")
    status = ssh_cmd(node, "systemctl is-active filebeat")
    log(f"Filebeat status on {node}: {status.strip()}")


def configure_fluentbit():
    log("Configuring Fluent Bit on core VPS")
    backup_cmd = "cp /etc/fluent-bit/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf.bak.$(date +%s) || true"
    ssh_cmd(CORE_VPS, backup_cmd)
    scp_file(CORE_VPS, FLUENT_BIT_CONFIG, "/tmp/fluent-bit.conf")
    ssh_cmd(CORE_VPS, "mv /tmp/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf")
    ssh_cmd(CORE_VPS, "systemctl daemon-reload")
    ssh_cmd(CORE_VPS, "systemctl enable fluent-bit")
    ssh_cmd(CORE_VPS, "systemctl restart fluent-bit")
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
