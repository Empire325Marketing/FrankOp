#!/usr/bin/env python3
"""End-to-end test for Filebeat to Fluent Bit pipeline."""
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

SSH_USER = os.getenv("SSH_USER", "root")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
if not SSH_PASSWORD:
    raise RuntimeError("SSH_PASSWORD environment variable not set")

def load_addresses() -> None:
    """Populate NODES and CORE_VPS from a config file if unset."""
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
LOG_PATH = "/tmp/fb_combined.log"


def log(msg: str) -> None:
    ts = datetime.utcnow().isoformat()
    print(f"[{ts}] {msg}")


def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
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


def send_test_log(node: str, tag: str) -> None:
    msg = f"$(date -u +%Y-%m-%dT%H:%M:%SZ) {tag}"
    ssh_cmd(node, f"echo {msg} >> /var/log/test.log")


def aggregator_has_tag(tag: str) -> bool:
    check_cmd = f"grep -q {tag} {LOG_PATH} && echo found || echo missing"
    result = ssh_cmd(CORE_VPS, check_cmd)
    return result.strip() == "found"


def main() -> None:
    tags: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(NODES)) as exe:
        futures = {}
        for node in NODES:
            tag = f"e2e-{node}-{int(time.time() * 1000)}"
            futures[exe.submit(send_test_log, node, tag)] = node
            tags[node] = tag
        for fut in as_completed(futures):
            node = futures[fut]
            try:
                fut.result()
                log(f"Log generated on {node}")
            except Exception as exc:
                log(f"Failed to generate log on {node}: {exc}")
                return

    log("Waiting for logs to propagate")
    time.sleep(5)

    success = True
    for node, tag in tags.items():
        if aggregator_has_tag(tag):
            log(f"Log from {node} received")
        else:
            log(f"Log from {node} missing")
            success = False

    if success:
        log("E2E test successful")
    else:
        log("E2E test failed")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
