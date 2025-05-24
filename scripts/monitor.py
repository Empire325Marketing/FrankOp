#!/usr/bin/env python3
"""Simple monitoring script for Filebeat services and log forwarding."""
import os
import subprocess
from datetime import datetime
from pathlib import Path

SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
if not SSH_PASSWORD:
    raise RuntimeError("SSH_PASSWORD environment variable not set")

NODES = os.getenv(
    "NODES",
    "31.97.13.92,31.97.13.95,31.97.13.100,31.97.13.102,31.97.13.104,31.97.13.108",
).split(",")
CORE_VPS = os.getenv("CORE_VPS", "145.223.73.4")
LOG_PATH = "/tmp/vps_combined.log"
THRESHOLD = 5_000_000  # rotate log above 5MB


def log(msg: str) -> None:
    ts = datetime.utcnow().isoformat()
    print(f"[{ts}] {msg}")


def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


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


def check_nodes() -> None:
    for node in NODES:
        status = ssh_cmd(node, "systemctl is-active filebeat || true")
        log(f"{node} filebeat status: {status}")


def check_log() -> None:
    size_str = ssh_cmd(CORE_VPS, f"stat -c %s {LOG_PATH} 2>/dev/null || echo 0")
    try:
        size = int(size_str)
    except ValueError:
        size = 0
    log(f"combined log size: {size} bytes")
    if size > THRESHOLD:
        ts = run_cmd(["date", "+%s"])
        ssh_cmd(CORE_VPS, f"mv {LOG_PATH} {LOG_PATH}.{ts} && touch {LOG_PATH}")
        log("log rotated on core VPS")


def main() -> None:
    check_nodes()
    check_log()


if __name__ == "__main__":
    main()
