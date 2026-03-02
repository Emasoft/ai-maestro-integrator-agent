# Multi-User Identity Script Reference

## Use-Case TOC

This document is split into multiple parts for easier navigation. Use the links below to find the section you need.

### Part 1: Installation and Overview
**File:** [script-multi-user-identity-part1-installation.md](script-multi-user-identity-part1-installation.md)

- When you need to understand what the script does → Overview
- When you need to set up multiple GitHub identities → Installation and Setup
- When you need to configure the identities.json file → Step 2: Edit Configuration
- When you need to generate SSH keys for all identities → Step 3: Generate SSH Keys
- When you need to add SSH keys to GitHub → Step 4: Add Keys to GitHub
- When you need to test all connections → Step 5: Test Connections
- When you need to authenticate the gh CLI → Step 6: Authenticate gh CLI

### Part 2: Core Commands
**File:** [script-multi-user-identity-part2-core-commands.md](script-multi-user-identity-part2-core-commands.md)

- When you need to generate SSH keys for a specific identity → Setup Command
- When you need to test SSH connections → Test Command
- When you need to switch between identities → Switch Command
- When you need to configure a single repository → Repo Command
- When you need to configure multiple repositories at once → Bulk-Repo Command

### Part 3: Advanced Commands
**File:** [script-multi-user-identity-part3-advanced-commands.md](script-multi-user-identity-part3-advanced-commands.md)

- When you need to check current identity status → Status Command
- When you need to add a new identity interactively → Add Command
- When you need to detect configuration issues → Diagnose Command
- When you need to automatically fix common issues → Fix Command

### Part 4: Troubleshooting and Integration
**File:** [script-multi-user-identity-part4-troubleshooting.md](script-multi-user-identity-part4-troubleshooting.md)

- When SSH key is not found → SSH Key Not Found
- When wrong user appears on SSH test → Wrong User on SSH Test
- When SSH config is not updated → SSH Config Not Updated
- When permission denied on push → Permission Denied on Push
- When gh CLI is not switching → gh CLI Not Switching
- When configuration file is not found → Configuration File Not Found
- When you need to know supported environment variables → Environment Variables
- When you need orchestration setup examples → Agent Orchestration Setup
- When you need CI/CD pipeline examples → CI/CD Pipeline
- When you need shell profile integration → Shell Profile Integration

---

## Quick Reference

### Script Files

| File | Description |
|------|-------------|
| `gh_multiuser.py` | Main script (Python 3, stdlib only, cross-platform) |
| `identities.example.json` | Configuration template |

### Running the Script

**Linux/macOS:**
```bash
python3 gh_multiuser.py <command> [args...]
```

**Windows:**
```powershell
python gh_multiuser.py <command> [args...]
# or
py -3 gh_multiuser.py <command> [args...]
```

### Command Summary

| Command | Description |
|---------|-------------|
| `setup <identity>` | Generate SSH key and configure host alias |
| `test [identity]` | Test SSH connection for one or all identities |
| `switch <identity>` | Switch active GitHub identity |
| `repo <path> <identity>` | Configure a repository for an identity |
| `bulk-repo <dir> <identity>` | Configure all repos under a directory |
| `status` | Show current identity status |
| `add` | Interactively add a new identity |
| `diagnose` | Detect configuration issues |
| `fix` | Auto-fix common issues |

---

## See Also

- [Multi-User Workflow](multi-user-workflow.md) - Conceptual guide to multi-user workflows
- [Prerequisites and Setup](prerequisites-and-setup.md) - Initial GitHub CLI setup
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide
