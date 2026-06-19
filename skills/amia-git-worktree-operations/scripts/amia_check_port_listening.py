#!/usr/bin/env python3
"""
Check whether a process is listening on a TCP port.

Cross-platform: on macOS/Linux it shells out to `lsof`, on Windows to
`netstat`. Use this as a "level 2" health check after starting a service and
before stopping one.

Usage:
    python amia_check_port_listening.py --port 8080
"""

import argparse
import platform
import subprocess


def check_port_listening_unix(port: int) -> bool:
    """Return True if a process is listening on the port (macOS/Linux)."""
    result = subprocess.run(
        ["lsof", "-i", f":{port}", "-t"],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def check_port_listening_windows(port: int) -> bool:
    """Return True if a process is listening on the port (Windows)."""
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True,
        check=False,
    )
    return f":{port}" in result.stdout


def check_port_listening(port: int) -> bool:
    """Dispatch to the platform-appropriate listening check."""
    if platform.system() == "Windows":
        return check_port_listening_windows(port)
    return check_port_listening_unix(port)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True, help="TCP port to check")
    args = parser.parse_args()
    listening = check_port_listening(args.port)
    print(f"port {args.port}: {'listening' if listening else 'free'}")


if __name__ == "__main__":
    main()
