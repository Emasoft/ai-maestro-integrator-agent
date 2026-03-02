#!/usr/bin/env python3
"""
gh-multiuser.py - Bulletproof Cross-Platform GitHub Multi-User Identity Management

This script provides robust, fail-proof management of multiple GitHub identities.
It automatically detects the platform, handles edge cases with heuristics, and
adapts to each system's configuration.

Features:
    - Automatic platform detection (Linux, macOS, Windows, WSL, Git Bash)
    - Automatic SSH agent management per platform
    - Robust error handling with retries and fallbacks
    - Configuration validation and auto-repair
    - Heuristics for common edge cases
    - Comprehensive diagnostics

Usage:
    python3 gh-multiuser.py setup <identity>    # Set up SSH and config
    python3 gh-multiuser.py test [identity]     # Test connections
    python3 gh-multiuser.py switch <identity>   # Switch identity
    python3 gh-multiuser.py repo <path> <id>    # Configure repository
    python3 gh-multiuser.py bulk-repo <dir> <id># Bulk configure repos
    python3 gh-multiuser.py status              # Show status
    python3 gh-multiuser.py list                # List identities
    python3 gh-multiuser.py add                 # Add new identity
    python3 gh-multiuser.py diagnose            # Run diagnostics
    python3 gh-multiuser.py fix                 # Auto-fix common issues

Requirements:
    - Python 3.7+ (uses only stdlib)
    - ssh-keygen (usually pre-installed)
    - git (for repository configuration)
    - gh CLI (optional, for account switching)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

# Type variable for retry decorator
T = TypeVar("T")


# =============================================================================
# Platform Detection
# =============================================================================


class Platform(Enum):
    """Detected platform types."""

    LINUX = auto()
    MACOS = auto()
    WINDOWS = auto()
    WSL = auto()  # Windows Subsystem for Linux
    GIT_BASH = auto()  # Git Bash on Windows
    CYGWIN = auto()  # Cygwin on Windows
    UNKNOWN = auto()


@dataclass
class PlatformInfo:
    """Detailed platform information."""

    platform: Platform
    is_windows_subsystem: bool = False  # WSL, Git Bash, Cygwin
    has_native_ssh: bool = True
    ssh_agent_type: str = "ssh-agent"
    shell_type: str = "bash"
    home_dir: Path = field(default_factory=Path.home)
    ssh_dir: Path = field(default_factory=lambda: Path.home() / ".ssh")

    @property
    def is_unix_like(self) -> bool:
        return self.platform in (
            Platform.LINUX,
            Platform.MACOS,
            Platform.WSL,
            Platform.GIT_BASH,
            Platform.CYGWIN,
        )

    @property
    def is_windows(self) -> bool:
        return self.platform == Platform.WINDOWS

    @property
    def uses_windows_paths(self) -> bool:
        return self.platform == Platform.WINDOWS


def detect_platform() -> PlatformInfo:
    """Detect the current platform with full details."""
    # WHY: Platform detection must happen at module load time (not lazily) because
    # SSH agent behavior, path handling, and command syntax differ fundamentally
    # across platforms. Early detection prevents runtime surprises and enables
    # platform-specific code paths throughout the entire script.
    import platform as plat

    system = plat.system().lower()

    # Check for WSL
    if system == "linux":
        # WSL detection methods
        wsl_indicators = [
            Path("/proc/version").exists()
            and "microsoft" in Path("/proc/version").read_text().lower(),
            Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists(),
            "WSL_DISTRO_NAME" in os.environ,
            "WSL_INTEROP" in os.environ,
        ]
        if any(wsl_indicators):
            return PlatformInfo(
                platform=Platform.WSL,
                is_windows_subsystem=True,
                shell_type=os.environ.get("SHELL", "/bin/bash").split("/")[-1],
            )
        return PlatformInfo(
            platform=Platform.LINUX,
            shell_type=os.environ.get("SHELL", "/bin/bash").split("/")[-1],
        )

    elif system == "darwin":
        return PlatformInfo(
            platform=Platform.MACOS,
            ssh_agent_type="keychain",
            shell_type=os.environ.get("SHELL", "/bin/zsh").split("/")[-1],
        )

    elif system == "windows":
        # Check for Git Bash
        if "MSYSTEM" in os.environ:
            return PlatformInfo(
                platform=Platform.GIT_BASH, is_windows_subsystem=True, shell_type="bash"
            )
        # Check for Cygwin
        if "CYGWIN" in os.environ.get("HOME", "").upper():
            return PlatformInfo(
                platform=Platform.CYGWIN, is_windows_subsystem=True, shell_type="bash"
            )
        # Native Windows
        return PlatformInfo(
            platform=Platform.WINDOWS,
            has_native_ssh="OpenSSH"
            in subprocess.run(
                ["ssh", "-V"], capture_output=True, text=True, timeout=5, check=False
            ).stderr
            if shutil.which("ssh")
            else False,
            ssh_agent_type="windows-openssh",
            shell_type="powershell",
        )

    return PlatformInfo(platform=Platform.UNKNOWN)


# Global platform info - detected once
PLATFORM = detect_platform()


# =============================================================================
# Logging and Output
# =============================================================================


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


CURRENT_LOG_LEVEL = LogLevel.INFO


def log(level: LogLevel, message: str, *args: Any) -> None:
    """Log a message with the specified level."""
    if level.value >= CURRENT_LOG_LEVEL.value:
        prefix = {
            LogLevel.DEBUG: "[DEBUG]",
            LogLevel.INFO: "[INFO]",
            LogLevel.WARN: "[WARN]",
            LogLevel.ERROR: "[ERROR]",
        }[level]
        formatted = message.format(*args) if args else message
        print(
            f"{prefix} {formatted}",
            file=sys.stderr if level == LogLevel.ERROR else sys.stdout,
        )


def debug(msg: str, *args: Any) -> None:
    log(LogLevel.DEBUG, msg, *args)


def info(msg: str, *args: Any) -> None:
    log(LogLevel.INFO, msg, *args)


def warn(msg: str, *args: Any) -> None:
    log(LogLevel.WARN, msg, *args)


def error(msg: str, *args: Any) -> None:
    log(LogLevel.ERROR, msg, *args)


# =============================================================================
# Retry and Error Handling
# =============================================================================


class RetryExhausted(Exception):
    """All retry attempts failed."""

    pass


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    on_retry: Optional[Callable[[BaseException, int], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry a function with exponential backoff."""

    # WHY: Exponential backoff (delay * backoff^attempt) prevents thundering herd
    # problems and respects rate limits. Network operations to GitHub often fail
    # transiently due to SSH agent hiccups, DNS resolution, or GitHub's own
    # rate limiting. Retrying with increasing delays gives systems time to recover.
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: BaseException | None = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        if on_retry:
                            on_retry(e, attempt)
                        debug(f"Retry {attempt}/{max_attempts} after error: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise RetryExhausted(
                f"Failed after {max_attempts} attempts: {last_exception}"
            )

        return wrapper

    return decorator


def safe_run(
    cmd: List[str],
    capture: bool = True,
    timeout: int = 30,
    check: bool = True,
    retries: int = 1,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    """Safely run a command with timeout and retries."""
    last_error: subprocess.TimeoutExpired | BaseException | None = None
    merged_env = {**os.environ, **(env or {})}

    for attempt in range(retries):
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=timeout,
                check=False,
                env=merged_env,
            )
            if check and result.returncode != 0:
                # SSH returns 1 even on success, handle specially
                if (
                    cmd[0] == "ssh"
                    and "successfully authenticated" in (result.stderr or "").lower()
                ):
                    return result
                if attempt < retries - 1:
                    debug(
                        f"Command failed (attempt {attempt + 1}), retrying: {' '.join(cmd)}"
                    )
                    time.sleep(1)
                    continue
                raise subprocess.CalledProcessError(
                    result.returncode, cmd, result.stdout, result.stderr
                )
            return result
        except subprocess.TimeoutExpired as e:
            last_error = e
            if attempt < retries - 1:
                debug(
                    f"Command timed out (attempt {attempt + 1}), retrying: {' '.join(cmd)}"
                )
                continue
        except FileNotFoundError as e:
            raise RuntimeError(
                f"Command not found: {cmd[0]}. Please install it first."
            ) from e
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                continue
            raise

    raise RuntimeError(f"Command failed after {retries} attempts: {last_error}")


def command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None


def require_command(cmd: str, install_hint: str = "") -> None:
    """Require a command to exist, exit with helpful message if not."""
    if not command_exists(cmd):
        error(f"Required command not found: {cmd}")
        if install_hint:
            info(f"Install hint: {install_hint}")
        else:
            hints = {
                "ssh": {
                    Platform.WINDOWS: "Enable OpenSSH: Settings > Apps > Optional Features > OpenSSH Client",
                    Platform.MACOS: "ssh is pre-installed on macOS",
                    Platform.LINUX: "Install: sudo apt install openssh-client  OR  sudo yum install openssh-clients",
                },
                "ssh-keygen": {
                    Platform.WINDOWS: "Enable OpenSSH: Settings > Apps > Optional Features > OpenSSH Client",
                    Platform.MACOS: "ssh-keygen is pre-installed on macOS",
                    Platform.LINUX: "Install: sudo apt install openssh-client  OR  sudo yum install openssh-clients",
                },
                "git": {
                    Platform.WINDOWS: "Download from https://git-scm.com/download/win or: winget install Git.Git",
                    Platform.MACOS: "Install: brew install git  OR  xcode-select --install",
                    Platform.LINUX: "Install: sudo apt install git  OR  sudo yum install git",
                },
                "gh": {
                    Platform.WINDOWS: "Install: winget install GitHub.cli",
                    Platform.MACOS: "Install: brew install gh",
                    Platform.LINUX: "Install: https://github.com/cli/cli/blob/trunk/docs/install_linux.md",
                },
            }
            if cmd in hints and PLATFORM.platform in hints[cmd]:
                info(hints[cmd][PLATFORM.platform])
        sys.exit(1)


# =============================================================================
# Configuration Management
# =============================================================================

CONFIG_LOCATIONS = [
    Path(__file__).parent / "identities.json",
    Path.home() / ".config" / "gh-multiuser" / "identities.json",
    Path.home() / ".gh-multiuser.json",
]

# Environment variable override
if "GH_MULTIUSER_CONFIG" in os.environ:
    CONFIG_LOCATIONS.insert(0, Path(os.environ["GH_MULTIUSER_CONFIG"]))


@dataclass
class Identity:
    """A GitHub identity configuration."""

    name: str
    github_username: str
    git_name: str
    git_email: str
    ssh_key_path: str
    ssh_host_alias: str
    description: str = ""

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "Identity":
        return cls(
            name=name,
            github_username=data.get("github_username", ""),
            git_name=data.get("git_name", ""),
            git_email=data.get("git_email", ""),
            ssh_key_path=data.get("ssh_key_path", ""),
            ssh_host_alias=data.get("ssh_host_alias", "github.com"),
            description=data.get("description", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "github_username": self.github_username,
            "git_name": self.git_name,
            "git_email": self.git_email,
            "ssh_key_path": self.ssh_key_path,
            "ssh_host_alias": self.ssh_host_alias,
        }

    def validate(self) -> List[str]:
        """Validate identity configuration, return list of issues."""
        issues = []
        if not self.github_username:
            issues.append(f"[{self.name}] Missing github_username")
        if not self.git_name:
            issues.append(f"[{self.name}] Missing git_name")
        if not self.git_email:
            issues.append(f"[{self.name}] Missing git_email")
        elif "@" not in self.git_email:
            issues.append(f"[{self.name}] Invalid git_email format (missing @)")
        if not self.ssh_key_path:
            issues.append(f"[{self.name}] Missing ssh_key_path")
        if not self.ssh_host_alias:
            issues.append(f"[{self.name}] Missing ssh_host_alias")
        return issues

    @property
    def expanded_key_path(self) -> Path:
        """Get the expanded SSH key path."""
        return Path(os.path.expandvars(os.path.expanduser(self.ssh_key_path)))

    @property
    def public_key_path(self) -> Path:
        """Get the public key path."""
        key_path = self.expanded_key_path
        # Handle both id_ed25519 and id_ed25519.pub naming
        if key_path.suffix == ".pub":
            return key_path
        return Path(str(key_path) + ".pub")


@dataclass
class Config:
    """Full configuration with identities and defaults."""

    identities: Dict[str, Identity]
    defaults: Dict[str, Any]
    config_path: Optional[Path] = None

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from file."""
        config_path: Path | None
        if path and path.exists():
            config_path = path
        else:
            config_path = cls.find_config()

        if config_path is None:
            # Create example config
            example_path = CONFIG_LOCATIONS[0].parent / "identities.example.json"
            if example_path.exists():
                error("No configuration file found.")
                info(f"Copy the example: cp {example_path} {CONFIG_LOCATIONS[0]}")
            else:
                error("No configuration file found.")
                info(f"Create one at: {CONFIG_LOCATIONS[0]}")
            sys.exit(1)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            error(f"Invalid JSON in config file: {e}")
            sys.exit(1)

        identities: dict[str, Identity] = {}
        for name, id_data in data.get("identities", {}).items():
            identities[name] = Identity.from_dict(name, id_data)

        return cls(
            identities=identities,
            defaults=data.get("defaults", {}),
            config_path=config_path,
        )

    @staticmethod
    def find_config() -> Optional[Path]:
        """Find the first existing configuration file."""
        for path in CONFIG_LOCATIONS:
            if path.exists():
                return path
        return None

    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to file."""
        save_path = path or self.config_path or CONFIG_LOCATIONS[0]
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "identities": {name: id.to_dict() for name, id in self.identities.items()},
            "defaults": self.defaults,
        }

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        info(f"Configuration saved to: {save_path}")

    def get_identity(self, name: str) -> Identity:
        """Get an identity by name."""
        if name not in self.identities:
            available = ", ".join(self.identities.keys())
            error(f"Identity '{name}' not found. Available: {available}")
            sys.exit(1)
        return self.identities[name]

    def validate(self) -> List[str]:
        """Validate all configuration, return list of issues."""
        issues = []
        if not self.identities:
            issues.append("No identities configured")
        for identity in self.identities.values():
            issues.extend(identity.validate())
        return issues


# =============================================================================
# SSH Management
# =============================================================================


class SSHManager:
    """Cross-platform SSH key and config management."""

    def __init__(self) -> None:
        self.platform = PLATFORM
        self.ssh_dir = PLATFORM.ssh_dir

    def ensure_ssh_dir(self) -> None:
        """Ensure SSH directory exists with correct permissions."""
        self.ssh_dir.mkdir(parents=True, exist_ok=True)

        # Set permissions (not applicable on Windows in the same way)
        if self.platform.is_unix_like:
            try:
                self.ssh_dir.chmod(0o700)
            except OSError:
                warn("Could not set SSH directory permissions")

    def key_exists(self, identity: Identity) -> bool:
        """Check if SSH key exists for identity."""
        return identity.expanded_key_path.exists()

    def generate_key(
        self, identity: Identity, key_type: str = "ed25519", force: bool = False
    ) -> Path:
        """Generate SSH key for an identity."""
        require_command("ssh-keygen")

        key_path = identity.expanded_key_path

        if key_path.exists() and not force:
            info(f"SSH key already exists: {key_path}")
            return key_path

        self.ensure_ssh_dir()

        info(f"Generating {key_type} SSH key: {key_path}")

        cmd = [
            "ssh-keygen",
            "-t",
            key_type,
            "-f",
            str(key_path),
            "-C",
            identity.git_email,
            "-N",
            "",  # Empty passphrase for automation
        ]

        # Remove existing key if force
        if force and key_path.exists():
            key_path.unlink()
            pub_key = identity.public_key_path
            if pub_key.exists():
                pub_key.unlink()

        safe_run(cmd, timeout=30)

        # Set permissions
        if self.platform.is_unix_like:
            try:
                key_path.chmod(0o600)
                if identity.public_key_path.exists():
                    identity.public_key_path.chmod(0o644)
            except OSError:
                warn("Could not set key permissions")

        info("SSH key generated successfully")
        return key_path

    def get_public_key(self, identity: Identity) -> Optional[str]:
        """Read the public key content."""
        pub_path = identity.public_key_path
        if pub_path.exists():
            return pub_path.read_text().strip()
        return None

    def add_ssh_config_entry(self, identity: Identity) -> bool:
        """Add or update SSH config entry for an identity."""
        host_alias = identity.ssh_host_alias

        # Skip if host alias is the default github.com
        if host_alias == "github.com":
            debug(f"Skipping SSH config for default host: {host_alias}")
            return True

        config_path = self.ssh_dir / "config"
        self.ensure_ssh_dir()

        # Read existing config
        existing_content = ""
        if config_path.exists():
            existing_content = config_path.read_text()

        # Check if entry already exists
        if f"Host {host_alias}" in existing_content:
            # Check if it's configured correctly
            host_block_pattern = (
                rf"Host\s+{re.escape(host_alias)}\s*\n((?:\s+\S+.*\n)*)"
            )
            match = re.search(host_block_pattern, existing_content)
            if match:
                block = match.group(1)
                expected_key = str(identity.expanded_key_path)
                if expected_key in block or identity.ssh_key_path in block:
                    info(f"SSH config already correct for Host {host_alias}")
                    return True
                else:
                    warn(f"SSH config for {host_alias} exists but may have wrong key")
                    # Continue to append a new corrected entry
            else:
                info(f"SSH config already contains Host {host_alias}")
                return True

        # Create new entry
        entry = f"""
# GitHub identity: {identity.description or identity.name}
Host {host_alias}
    HostName github.com
    User git
    IdentityFile {identity.expanded_key_path}
    IdentitiesOnly yes
    AddKeysToAgent yes
"""

        # Add macOS keychain support
        if self.platform.platform == Platform.MACOS:
            entry += "    UseKeychain yes\n"

        # Append to config
        with open(config_path, "a", encoding="utf-8") as f:
            f.write(entry)

        # Set permissions
        if self.platform.is_unix_like:
            try:
                config_path.chmod(0o600)
            except OSError:
                pass

        info(f"Added SSH config entry for Host {host_alias}")
        return True

    def add_key_to_agent(self, identity: Identity) -> bool:
        """Add SSH key to the agent."""
        key_path = identity.expanded_key_path

        if not key_path.exists():
            warn(f"SSH key not found: {key_path}")
            return False

        if self.platform.platform == Platform.MACOS:
            # macOS: use --apple-use-keychain for persistence
            cmd = ["ssh-add", "--apple-use-keychain", str(key_path)]
        elif self.platform.is_unix_like:
            # Linux/WSL/Git Bash: standard ssh-add
            cmd = ["ssh-add", str(key_path)]
        else:
            # Windows native: use ssh-add from OpenSSH
            cmd = ["ssh-add", str(key_path)]

        try:
            result = safe_run(cmd, timeout=10, check=False)
            if result.returncode == 0:
                info(f"Added key to SSH agent: {key_path}")
                return True
            else:
                # Agent might not be running
                if "Could not open a connection" in (result.stderr or ""):
                    warn("SSH agent not running. Starting it...")
                    self.start_ssh_agent()
                    # Retry
                    result = safe_run(cmd, timeout=10, check=False)
                    return result.returncode == 0
                warn(f"Could not add key to agent: {result.stderr}")
                return False
        except Exception as e:
            warn(f"Error adding key to agent: {e}")
            return False

    def start_ssh_agent(self) -> bool:
        """Start SSH agent if not running."""
        if self.platform.platform == Platform.MACOS:
            # macOS agent is usually always running
            return True

        if self.platform.is_unix_like:
            # Check if agent is running
            if "SSH_AUTH_SOCK" in os.environ:
                sock = os.environ["SSH_AUTH_SOCK"]
                if Path(sock).exists():
                    return True

            # Try to start agent
            try:
                result = safe_run(["ssh-agent", "-s"], timeout=5, check=False)
                if result.returncode == 0:
                    # Parse and set environment variables
                    for line in result.stdout.split("\n"):
                        if "SSH_AUTH_SOCK" in line:
                            match = re.search(r"SSH_AUTH_SOCK=([^;]+)", line)
                            if match:
                                os.environ["SSH_AUTH_SOCK"] = match.group(1)
                        if "SSH_AGENT_PID" in line:
                            match = re.search(r"SSH_AGENT_PID=(\d+)", line)
                            if match:
                                os.environ["SSH_AGENT_PID"] = match.group(1)
                    info("SSH agent started")
                    return True
            except Exception as e:
                warn(f"Could not start SSH agent: {e}")

        elif self.platform.platform == Platform.WINDOWS:
            # Windows: Check if ssh-agent service is running
            try:
                result = safe_run(
                    [
                        "powershell",
                        "-Command",
                        "Get-Service ssh-agent | Select-Object -ExpandProperty Status",
                    ],
                    timeout=10,
                    check=False,
                )
                if "Running" not in result.stdout:
                    warn("Windows SSH agent service not running. Run as admin:")
                    info("  Start-Service ssh-agent")
                    info("  Set-Service -Name ssh-agent -StartupType Automatic")
                    return False
                return True
            except Exception:
                pass

        return False

    def test_connection(
        self, identity: Identity, timeout: int = 10
    ) -> Tuple[bool, str]:
        """Test SSH connection for an identity. Returns (success, message)."""
        host_alias = identity.ssh_host_alias

        # Ensure key is in agent
        self.add_key_to_agent(identity)

        # WHY: We use BatchMode=yes to prevent SSH from prompting for passwords or
        # confirmations, which would hang in automated scripts. StrictHostKeyChecking=
        # accept-new auto-accepts new hosts but rejects changed keys (security balance
        # between usability and MITM protection for first-time connections).
        cmd = [
            "ssh",
            "-T",
            "-o",
            f"ConnectTimeout={timeout}",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "BatchMode=yes",
            f"git@{host_alias}",
        ]

        try:
            result = safe_run(cmd, timeout=timeout + 5, check=False)
            output = (result.stdout or "") + (result.stderr or "")

            # GitHub returns exit code 1 even on success (no shell access)
            if "successfully authenticated" in output.lower():
                # Extract username from response
                match = re.search(r"Hi (\S+)!", output)
                if match:
                    authenticated_user = match.group(1)
                    if authenticated_user.lower() != identity.github_username.lower():
                        return (
                            False,
                            f"Wrong user! Expected {identity.github_username}, got {authenticated_user}",
                        )
                return True, output.strip()

            if "permission denied" in output.lower():
                return (
                    False,
                    "Permission denied. Key may not be added to GitHub account.",
                )

            if "connection refused" in output.lower():
                return False, "Connection refused. Check network/firewall."

            if (
                "connection timed out" in output.lower()
                or "timed out" in output.lower()
            ):
                return False, "Connection timed out. Check network."

            return False, output.strip() or "Unknown error"

        except subprocess.TimeoutExpired:
            return False, f"Connection timed out after {timeout}s"
        except Exception as e:
            return False, str(e)

    def list_loaded_keys(self) -> List[str]:
        """List keys currently loaded in SSH agent."""
        try:
            result = safe_run(["ssh-add", "-l"], timeout=5, check=False)
            if result.returncode == 0:
                return [line for line in result.stdout.split("\n") if line.strip()]
            return []
        except Exception:
            return []

    def clear_agent(self) -> bool:
        """Clear all keys from SSH agent."""
        try:
            result = safe_run(["ssh-add", "-D"], timeout=5, check=False)
            return result.returncode == 0
        except Exception:
            return False


# =============================================================================
# Git and GitHub CLI Management
# =============================================================================


class GitManager:
    """Git configuration and repository management."""

    @staticmethod
    def is_git_repo(path: Path) -> bool:
        """Check if path is a git repository."""
        return (path / ".git").is_dir() or (path / ".git").is_file()

    @staticmethod
    def configure_repo(path: Path, identity: Identity) -> bool:
        """Configure a repository for a specific identity."""
        require_command("git")

        if not GitManager.is_git_repo(path):
            error(f"Not a git repository: {path}")
            return False

        info(f"Configuring repository: {path}")

        # Set user identity
        try:
            safe_run(["git", "-C", str(path), "config", "user.name", identity.git_name])
            safe_run(
                ["git", "-C", str(path), "config", "user.email", identity.git_email]
            )
            info(f"  Set identity: {identity.git_name} <{identity.git_email}>")
        except Exception as e:
            error(f"  Failed to set git identity: {e}")
            return False

        # Update remote URL if needed
        if identity.ssh_host_alias != "github.com":
            try:
                result = safe_run(
                    ["git", "-C", str(path), "remote", "get-url", "origin"], check=False
                )
                if result.returncode != 0:
                    info("  No origin remote, skipping URL update")
                    return True

                current_url = result.stdout.strip()

                # Only modify GitHub URLs
                if "github.com" not in current_url:
                    info(f"  Remote is not GitHub, skipping: {current_url}")
                    return True

                # Parse and rebuild URL
                patterns = [
                    r"git@github\.com:(.+?)(?:\.git)?$",
                    r"https://github\.com/(.+?)(?:\.git)?$",
                    r"ssh://git@github\.com/(.+?)(?:\.git)?$",
                ]

                owner_repo = None
                for pattern in patterns:
                    match = re.search(pattern, current_url)
                    if match:
                        owner_repo = match.group(1).rstrip("/").rstrip(".git")
                        break

                if owner_repo:
                    new_url = f"git@{identity.ssh_host_alias}:{owner_repo}.git"
                    safe_run(
                        ["git", "-C", str(path), "remote", "set-url", "origin", new_url]
                    )
                    info(f"  Set remote: {new_url}")
                else:
                    warn(f"  Could not parse remote URL: {current_url}")

            except Exception as e:
                warn(f"  Could not update remote URL: {e}")

        return True

    @staticmethod
    def bulk_configure(root: Path, identity: Identity) -> Tuple[int, int, int]:
        """Bulk configure all repos under a directory. Returns (success, skipped, failed)."""
        info(f"Scanning for git repositories under: {root}")

        repos = []
        for path in root.rglob(".git"):
            if path.is_dir():
                repos.append(path.parent)
            elif path.is_file():
                # Git worktrees use .git as a file
                repos.append(path.parent)

        if not repos:
            info("No git repositories found")
            return 0, 0, 0

        info(f"Found {len(repos)} repositories")

        success = 0
        skipped = 0
        failed = 0

        for repo in repos:
            if GitManager.configure_repo(repo, identity):
                success += 1
            else:
                failed += 1

        info(f"\nConfigured: {success}, Skipped: {skipped}, Failed: {failed}")
        return success, skipped, failed


class GHCLIManager:
    """GitHub CLI management."""

    @staticmethod
    def is_installed() -> bool:
        return command_exists("gh")

    @staticmethod
    def get_authenticated_accounts() -> List[str]:
        """Get list of authenticated GitHub accounts."""
        if not GHCLIManager.is_installed():
            return []

        try:
            result = safe_run(["gh", "auth", "status"], check=False, timeout=10)
            output = result.stdout + result.stderr

            accounts = []
            for line in output.split("\n"):
                match = re.search(r"Logged in to \S+ account (\S+)", line)
                if match:
                    accounts.append(match.group(1))
            return accounts
        except Exception:
            return []

    @staticmethod
    def get_active_account() -> Optional[str]:
        """Get the currently active GitHub account."""
        if not GHCLIManager.is_installed():
            return None

        try:
            result = safe_run(["gh", "auth", "status"], check=False, timeout=10)
            output = result.stdout + result.stderr

            # Look for "Active account: true" pattern
            lines = output.split("\n")
            for i, line in enumerate(lines):
                if "Active account: true" in line:
                    # Look backwards for the account line
                    for j in range(i, -1, -1):
                        match = re.search(r"Logged in to \S+ account (\S+)", lines[j])
                        if match:
                            return match.group(1)
            return None
        except Exception:
            return None

    @staticmethod
    def switch_account(username: str) -> bool:
        """Switch to a different GitHub account."""
        if not GHCLIManager.is_installed():
            warn("gh CLI not installed, cannot switch account")
            return False

        try:
            result = safe_run(
                ["gh", "auth", "switch", "--user", username], check=False, timeout=10
            )
            if result.returncode == 0:
                info(f"Switched gh CLI to: {username}")
                return True
            else:
                # Check if user is authenticated at all
                accounts = GHCLIManager.get_authenticated_accounts()
                if username not in accounts:
                    warn(f"Account {username} not authenticated with gh CLI")
                    info(
                        "Run: gh auth login (while logged into that account in browser)"
                    )
                else:
                    warn(f"Could not switch to {username}: {result.stderr}")
                return False
        except Exception as e:
            warn(f"Error switching gh account: {e}")
            return False

    @staticmethod
    def print_status() -> None:
        """Print gh CLI authentication status."""
        if not GHCLIManager.is_installed():
            print("GitHub CLI (gh): Not installed")
            return

        print("GitHub CLI (gh):")
        try:
            result = safe_run(["gh", "auth", "status"], check=False, timeout=10)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"  Error: {e}")


# =============================================================================
# Diagnostics
# =============================================================================


class Diagnostics:
    """System diagnostics and auto-fix."""

    def __init__(self, config: Config):
        self.config = config
        self.ssh_manager = SSHManager()
        self.issues: List[Tuple[str, str, Callable[[], bool]]] = []

    def run_diagnostics(self) -> List[Tuple[str, str]]:
        """Run all diagnostics. Returns list of (issue, fix_suggestion)."""
        issues = []

        # Check required commands
        for cmd, name in [
            ("ssh", "SSH client"),
            ("ssh-keygen", "SSH keygen"),
            ("git", "Git"),
        ]:
            if not command_exists(cmd):
                issues.append((f"Missing: {name} ({cmd})", "Install the required tool"))

        # Check optional commands
        if not command_exists("gh"):
            issues.append(
                (
                    "gh CLI not installed",
                    "Install for account switching: brew install gh",
                )
            )

        # Check SSH agent
        if PLATFORM.is_unix_like:
            if "SSH_AUTH_SOCK" not in os.environ:
                issues.append(("SSH agent not running", "Run: eval $(ssh-agent -s)"))

        # Validate configuration
        config_issues = self.config.validate()
        for issue in config_issues:
            issues.append((issue, "Fix in identities.json"))

        # Check each identity
        for name, identity in self.config.identities.items():
            # Check SSH key exists
            if not identity.expanded_key_path.exists():
                issues.append(
                    (
                        f"[{name}] SSH key missing: {identity.expanded_key_path}",
                        f"Run: python3 gh-multiuser.py setup {name}",
                    )
                )
            else:
                # Check public key exists
                if not identity.public_key_path.exists():
                    issues.append(
                        (
                            f"[{name}] Public key missing: {identity.public_key_path}",
                            f"Regenerate: python3 gh-multiuser.py setup {name} --force",
                        )
                    )

            # Check SSH config entry
            if identity.ssh_host_alias != "github.com":
                config_path = PLATFORM.ssh_dir / "config"
                if config_path.exists():
                    content = config_path.read_text()
                    if f"Host {identity.ssh_host_alias}" not in content:
                        issues.append(
                            (
                                f"[{name}] SSH config missing for {identity.ssh_host_alias}",
                                f"Run: python3 gh-multiuser.py setup {name}",
                            )
                        )

        # Check gh CLI accounts
        if command_exists("gh"):
            accounts = GHCLIManager.get_authenticated_accounts()
            for name, identity in self.config.identities.items():
                if identity.github_username not in accounts:
                    issues.append(
                        (
                            f"[{name}] gh CLI not authenticated for {identity.github_username}",
                            f"Run: gh auth login (while logged into {identity.github_username} in browser)",
                        )
                    )

        return issues

    def auto_fix(self) -> int:
        """Attempt to auto-fix issues. Returns number of fixes applied."""
        fixes = 0

        # Ensure SSH directory exists
        self.ssh_manager.ensure_ssh_dir()

        # Start SSH agent if needed
        if self.ssh_manager.start_ssh_agent():
            fixes += 1

        # Add missing SSH config entries
        for identity in self.config.identities.values():
            if identity.ssh_host_alias != "github.com":
                config_path = PLATFORM.ssh_dir / "config"
                if (
                    not config_path.exists()
                    or f"Host {identity.ssh_host_alias}" not in config_path.read_text()
                ):
                    if identity.expanded_key_path.exists():
                        if self.ssh_manager.add_ssh_config_entry(identity):
                            fixes += 1

        # Add keys to agent
        for identity in self.config.identities.values():
            if identity.expanded_key_path.exists():
                if self.ssh_manager.add_key_to_agent(identity):
                    fixes += 1

        return fixes


# =============================================================================
# Commands
# =============================================================================


def cmd_setup(config: Config, args: argparse.Namespace) -> int:
    """Set up SSH key and config for an identity."""
    identity = config.get_identity(args.identity)
    ssh_manager = SSHManager()

    print(f"=== Setting up identity: {args.identity} ===\n")

    # Generate SSH key
    force = getattr(args, "force", False)
    key_type = config.defaults.get("ssh_key_type", "ed25519")
    ssh_manager.generate_key(identity, key_type=key_type, force=force)

    # Add SSH config entry
    ssh_manager.add_ssh_config_entry(identity)

    # Add key to agent
    ssh_manager.add_key_to_agent(identity)

    # Show public key
    pub_key = ssh_manager.get_public_key(identity)
    if pub_key:
        print(f"\n{'=' * 50}")
        print("PUBLIC KEY (add to GitHub):")
        print(f"{'=' * 50}")
        print(pub_key)
        print(f"{'=' * 50}\n")
        print(f"Add this key to GitHub account: {identity.github_username}")
        print("  1. Go to: https://github.com/settings/keys")
        print("  2. Click 'New SSH key'")
        print("  3. Paste the key above")

    print("\nNext steps:")
    print("  1. Add the public key to GitHub (see above)")
    print(f"  2. Test: python3 gh-multiuser.py test {args.identity}")
    print("  3. Authenticate gh: gh auth login")

    return 0


def cmd_test(config: Config, args: argparse.Namespace) -> int:
    """Test SSH connection for identity."""
    ssh_manager = SSHManager()

    if args.identity:
        identities = [config.get_identity(args.identity)]
    else:
        identities = list(config.identities.values())

    all_success = True

    for identity in identities:
        print(f"\n=== Testing: {identity.name} ({identity.github_username}) ===")
        print(f"SSH host: {identity.ssh_host_alias}")

        success, message = ssh_manager.test_connection(identity)

        if success:
            print(f"[OK] {message}")
        else:
            print(f"[FAILED] {message}")
            all_success = False

    return 0 if all_success else 1


def cmd_switch(config: Config, args: argparse.Namespace) -> int:
    """Switch to a different identity."""
    identity = config.get_identity(args.identity)
    ssh_manager = SSHManager()

    print(f"=== Switching to: {args.identity} ===\n")

    # Add key to agent
    ssh_manager.add_key_to_agent(identity)

    # Switch gh CLI
    if GHCLIManager.is_installed():
        GHCLIManager.switch_account(identity.github_username)

    # Print shell exports
    print("\nSet these environment variables in your shell:")

    if PLATFORM.is_unix_like:
        print(f'\nexport GIT_AUTHOR_NAME="{identity.git_name}"')
        print(f'export GIT_AUTHOR_EMAIL="{identity.git_email}"')
        print(f'export GIT_COMMITTER_NAME="{identity.git_name}"')
        print(f'export GIT_COMMITTER_EMAIL="{identity.git_email}"')
    else:
        print(f'\n$env:GIT_AUTHOR_NAME = "{identity.git_name}"')
        print(f'$env:GIT_AUTHOR_EMAIL = "{identity.git_email}"')
        print(f'$env:GIT_COMMITTER_NAME = "{identity.git_name}"')
        print(f'$env:GIT_COMMITTER_EMAIL = "{identity.git_email}"')

    print("\nTip: For persistent changes, configure each repository with:")
    print(f"  python3 gh-multiuser.py repo /path/to/repo {args.identity}")

    return 0


def cmd_repo(config: Config, args: argparse.Namespace) -> int:
    """Configure a repository for an identity."""
    identity = config.get_identity(args.identity)
    path = Path(args.path).resolve()

    if GitManager.configure_repo(path, identity):
        return 0
    return 1


def cmd_bulk_repo(config: Config, args: argparse.Namespace) -> int:
    """Bulk configure repositories."""
    identity = config.get_identity(args.identity)
    root = Path(args.root).resolve()

    if not root.is_dir():
        error(f"Not a directory: {root}")
        return 1

    success, skipped, failed = GitManager.bulk_configure(root, identity)
    return 0 if failed == 0 else 1


def cmd_status(config: Config, args: argparse.Namespace) -> int:
    """Show current status."""
    ssh_manager = SSHManager()

    print("=" * 60)
    print("GitHub Multi-User Status")
    print("=" * 60)

    print(f"\nPlatform: {PLATFORM.platform.name}")
    print(f"SSH Directory: {PLATFORM.ssh_dir}")
    print(f"Config File: {config.config_path}")

    # gh CLI status
    print("\n" + "-" * 40)
    GHCLIManager.print_status()

    # SSH agent keys
    print("\n" + "-" * 40)
    print("SSH Agent Keys:")
    keys = ssh_manager.list_loaded_keys()
    if keys:
        for key in keys:
            print(f"  {key}")
    else:
        print("  No keys loaded")

    # Configured identities
    print("\n" + "-" * 40)
    print("Configured Identities:")

    for name, identity in config.identities.items():
        key_exists = identity.expanded_key_path.exists()
        status = "[OK]" if key_exists else "[NO KEY]"
        print(f"\n  {name}: {status}")
        print(f"    Description: {identity.description or 'N/A'}")
        print(f"    GitHub User: {identity.github_username}")
        print(f"    Git Identity: {identity.git_name} <{identity.git_email}>")
        print(f"    SSH Key: {identity.expanded_key_path}")
        print(f"    SSH Host: {identity.ssh_host_alias}")

    return 0


def cmd_list(config: Config, args: argparse.Namespace) -> int:
    """List identities."""
    print("Configured identities:")
    for name, identity in config.identities.items():
        print(f"  - {name}: {identity.description or identity.github_username}")
    return 0


def cmd_add(config: Config, args: argparse.Namespace) -> int:
    """Add a new identity interactively."""
    print("=== Add New GitHub Identity ===\n")

    try:
        name = input("Identity name (e.g., 'secondary', 'work'): ").strip()
        if not name:
            error("Identity name is required")
            return 1

        if name in config.identities:
            error(f"Identity '{name}' already exists")
            return 1

        github_username = input("GitHub username: ").strip()
        if not github_username:
            error("GitHub username is required")
            return 1

        git_name = input(f"Git name [{github_username}]: ").strip() or github_username

        print("\nTip: Use GitHub's noreply email from Settings > Emails")
        print("Format: ID+USERNAME@users.noreply.github.com")
        git_email = input("Git email: ").strip()
        if not git_email:
            error("Git email is required")
            return 1

        default_key = f"~/.ssh/id_ed25519_{name}"
        ssh_key_path = input(f"SSH key path [{default_key}]: ").strip() or default_key

        default_host = f"github-{name}"
        ssh_host_alias = (
            input(f"SSH host alias [{default_host}]: ").strip() or default_host
        )

        description = input("Description (optional): ").strip()

        # Add identity
        config.identities[name] = Identity(
            name=name,
            github_username=github_username,
            git_name=git_name,
            git_email=git_email,
            ssh_key_path=ssh_key_path,
            ssh_host_alias=ssh_host_alias,
            description=description or f"{name} identity",
        )

        config.save()

        print(f"\nIdentity '{name}' added.")
        print(f"Run: python3 gh-multiuser.py setup {name}")

    except (KeyboardInterrupt, EOFError):
        print("\nCancelled")
        return 1

    return 0


def cmd_diagnose(config: Config, args: argparse.Namespace) -> int:
    """Run diagnostics."""
    print("=== Running Diagnostics ===\n")

    diagnostics = Diagnostics(config)
    issues = diagnostics.run_diagnostics()

    if not issues:
        print("[OK] No issues found")
        return 0

    print(f"Found {len(issues)} issue(s):\n")
    for i, (issue, fix) in enumerate(issues, 1):
        print(f"  {i}. {issue}")
        print(f"     Fix: {fix}")

    print("\nRun 'python3 gh-multiuser.py fix' to auto-fix some issues")
    return 1


def cmd_fix(config: Config, args: argparse.Namespace) -> int:
    """Auto-fix common issues."""
    print("=== Auto-Fixing Issues ===\n")

    diagnostics = Diagnostics(config)
    fixes = diagnostics.auto_fix()

    print(f"\nApplied {fixes} fix(es)")

    # Run diagnostics again
    issues = diagnostics.run_diagnostics()
    if issues:
        print(f"\nRemaining issues ({len(issues)}):")
        for issue, fix in issues:
            print(f"  - {issue}")
            print(f"    Fix: {fix}")
    else:
        print("\n[OK] All issues resolved")

    return 0 if not issues else 1


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bulletproof cross-platform GitHub multi-user identity management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 gh-multiuser.py setup secondary       # Set up SSH for 'secondary'
  python3 gh-multiuser.py test                  # Test all SSH connections
  python3 gh-multiuser.py switch secondary      # Switch to 'secondary'
  python3 gh-multiuser.py repo ./myrepo secondary  # Configure repo
  python3 gh-multiuser.py diagnose              # Check for issues
  python3 gh-multiuser.py fix                   # Auto-fix issues
        """,
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # setup
    setup_p = subparsers.add_parser("setup", help="Set up SSH key and config")
    setup_p.add_argument("identity", help="Identity name")
    setup_p.add_argument(
        "--force", action="store_true", help="Regenerate key if exists"
    )

    # test
    test_p = subparsers.add_parser("test", help="Test SSH connection")
    test_p.add_argument("identity", nargs="?", help="Identity name (optional)")

    # switch
    switch_p = subparsers.add_parser("switch", help="Switch active identity")
    switch_p.add_argument("identity", help="Identity name")

    # repo
    repo_p = subparsers.add_parser("repo", help="Configure a repository")
    repo_p.add_argument("path", help="Repository path")
    repo_p.add_argument("identity", help="Identity name")

    # bulk-repo
    bulk_p = subparsers.add_parser("bulk-repo", help="Bulk configure repos")
    bulk_p.add_argument("root", help="Root directory")
    bulk_p.add_argument("identity", help="Identity name")

    # status
    subparsers.add_parser("status", help="Show current status")

    # list
    subparsers.add_parser("list", help="List identities")

    # add
    subparsers.add_parser("add", help="Add new identity")

    # diagnose
    subparsers.add_parser("diagnose", help="Run diagnostics")

    # fix
    subparsers.add_parser("fix", help="Auto-fix issues")

    args = parser.parse_args()

    # Set log level
    global CURRENT_LOG_LEVEL
    if args.verbose:
        CURRENT_LOG_LEVEL = LogLevel.DEBUG

    if not args.command:
        parser.print_help()
        return 0

    # Commands that work without config
    if args.command == "add":
        try:
            config = Config.load()
        except SystemExit:
            config = Config(identities={}, defaults={})
        return cmd_add(config, args)

    # Load config
    try:
        config = Config.load()
    except SystemExit as e:
        # e.code can be int | str | None, ensure we return int
        if isinstance(e.code, int):
            return e.code
        return 1

    # Dispatch command
    commands: dict[str, Callable[[Config, argparse.Namespace], int]] = {
        "setup": cmd_setup,
        "test": cmd_test,
        "switch": cmd_switch,
        "repo": cmd_repo,
        "bulk-repo": cmd_bulk_repo,
        "status": cmd_status,
        "list": cmd_list,
        "diagnose": cmd_diagnose,
        "fix": cmd_fix,
    }

    if args.command in commands:
        return commands[args.command](config, args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        error(f"Unexpected error: {e}")
        if CURRENT_LOG_LEVEL == LogLevel.DEBUG:
            import traceback

            traceback.print_exc()
        sys.exit(1)
