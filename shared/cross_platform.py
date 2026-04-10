"""Cross-platform utilities for subprocess execution and atomic file I/O.

Provides:
- run_command(): wrapper around subprocess.run that returns (exit_code, stdout, stderr)
- atomic_write_json(): writes JSON to a file atomically via temp-file + rename
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run_command(
    cmd: list[str],
    *,
    cwd: str | Path | None = None,
    timeout: int = 120,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr).

    Does NOT raise on non-zero exit — callers inspect the exit code.
    """
    merged_env = None
    if env is not None:
        merged_env = {**os.environ, **env}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
            timeout=timeout,
            env=merged_env,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"command timed out after {timeout}s: {' '.join(cmd)}"


def atomic_write_json(data: Any, path: str | Path, *, indent: int = 2) -> None:
    """Write JSON to *path* atomically.

    Writes to a temporary file in the same directory, then renames.
    On POSIX, rename is atomic within the same filesystem. On Windows,
    os.replace provides the same guarantee.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(target.parent), suffix=".tmp", prefix=target.stem + "_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, str(target))
    except BaseException:
        # Clean up on failure — don't leave temp files around
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
