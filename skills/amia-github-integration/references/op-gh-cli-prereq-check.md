---
name: op-gh-cli-prereq-check
description: "Verify GitHub CLI prerequisites (version, installation, configuration)"
procedure: support-skill
workflow-instruction: support
---

# Operation: GitHub CLI Prerequisites Check


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Check if gh is installed](#step-1-check-if-gh-is-installed)
  - [Step 2: Check version](#step-2-check-version)
  - [Step 3: Parse and compare version](#step-3-parse-and-compare-version)
  - [Step 4: Check configuration](#step-4-check-configuration)
  - [Step 5: Verify extensions (optional)](#step-5-verify-extensions-optional)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Installation Instructions](#installation-instructions)
  - [macOS (Homebrew)](#macos-homebrew)
  - [macOS (MacPorts)](#macos-macports)
  - [Linux (apt)](#linux-apt)
  - [Windows (winget)](#windows-winget)
- [Upgrade Instructions](#upgrade-instructions)
  - [macOS](#macos)
  - [Linux (apt)](#linux-apt)
- [Error Handling](#error-handling)
  - [Command not found](#command-not-found)
  - [Version too old](#version-too-old)
  - [PATH issues](#path-issues)
- [Verification Script](#verification-script)
- [Next Steps](#next-steps)

## Purpose

Verify that the GitHub CLI is properly installed and configured with the required version before performing any GitHub operations.

## When to Use

- At the very start of any GitHub integration workflow
- When setting up a new development environment
- When encountering unexpected CLI errors
- After system updates or reinstallation

## Prerequisites

None - this operation checks prerequisites.

## Procedure

### Step 1: Check if gh is installed

```bash
which gh || echo "GitHub CLI not found in PATH"
```

### Step 2: Check version

```bash
gh --version
```

Expected output format:
```
gh version 2.45.0 (2025-01-15)
https://github.com/cli/cli/releases/tag/v2.45.0
```

Minimum required version: **2.14.0** (for Projects V2 support)

### Step 3: Parse and compare version

```bash
# Get version number
GH_VERSION=$(gh --version | head -1 | awk '{print $3}')

# Compare with minimum (2.14.0)
MIN_VERSION="2.14.0"

# Version comparison function
version_compare() {
  [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$1" ]
}

if version_compare "$MIN_VERSION" "$GH_VERSION"; then
  echo "OK: Version $GH_VERSION meets minimum $MIN_VERSION"
else
  echo "FAIL: Version $GH_VERSION is below minimum $MIN_VERSION"
fi
```

### Step 4: Check configuration

```bash
# Check configured hosts
gh config list

# Check default editor
gh config get editor

# Check default protocol
gh config get git_protocol
```

### Step 5: Verify extensions (optional)

```bash
# List installed extensions
gh extension list
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| min_version | string | no | Minimum required version (default: 2.14.0) |
| required_extensions | string[] | no | Extensions that must be installed |

## Output

| Field | Type | Description |
|-------|------|-------------|
| installed | boolean | Whether gh is installed |
| version | string | Installed version |
| meets_minimum | boolean | Whether version meets minimum |
| config | object | Configuration settings |
| extensions | string[] | Installed extensions |

## Example Output

```json
{
  "installed": true,
  "version": "2.45.0",
  "meets_minimum": true,
  "config": {
    "git_protocol": "ssh",
    "editor": "vim",
    "browser": "default"
  },
  "extensions": ["gh-copilot"]
}
```

## Installation Instructions

### macOS (Homebrew)

```bash
brew install gh
```

### macOS (MacPorts)

```bash
sudo port install gh
```

### Linux (apt)

```bash
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
```

### Windows (winget)

```powershell
winget install --id GitHub.cli
```

## Upgrade Instructions

### macOS

```bash
brew upgrade gh
```

### Linux (apt)

```bash
sudo apt update && sudo apt upgrade gh
```

## Error Handling

### Command not found

**Symptom**: `gh: command not found`

**Solution**: Install GitHub CLI following instructions above.

### Version too old

**Symptom**: Version below 2.14.0

**Solution**: Upgrade using package manager.

### PATH issues

**Symptom**: gh installed but not found

**Solution**:
```bash
# Find installation
find /usr -name "gh" 2>/dev/null
# or
brew --prefix gh

# Add to PATH in ~/.zshrc or ~/.bashrc
export PATH="/path/to/gh/bin:$PATH"
```

## Verification Script

Complete prerequisites check:

```bash
#!/bin/bash
echo "=== GitHub CLI Prerequisites Check ==="

# Check installation
if ! command -v gh &>/dev/null; then
  echo "FAIL: GitHub CLI not installed"
  echo "Install with: brew install gh"
  exit 1
fi
echo "OK: GitHub CLI installed"

# Check version
GH_VERSION=$(gh --version | head -1 | awk '{print $3}')
echo "OK: Version $GH_VERSION"

# Check minimum version
MIN_VERSION="2.14.0"
if [ "$(printf '%s\n' "$MIN_VERSION" "$GH_VERSION" | sort -V | head -n1)" = "$MIN_VERSION" ]; then
  echo "OK: Meets minimum version $MIN_VERSION"
else
  echo "FAIL: Version $GH_VERSION below minimum $MIN_VERSION"
  echo "Upgrade with: brew upgrade gh"
  exit 1
fi

# Check authentication
if gh auth status &>/dev/null; then
  echo "OK: Authenticated"
else
  echo "WARN: Not authenticated - run: gh auth login"
fi

echo "=== Prerequisites Check Complete ==="
```

## Next Steps

After prerequisites are verified:

1. Run `op-gh-cli-auth-check` to verify authentication
2. Proceed with GitHub integration operations
