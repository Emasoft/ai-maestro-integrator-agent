# Worktree Automation Scripts Guide

## Document Map

This guide has been split into focused parts for easier navigation:

| Part | Topic | When to Read |
|------|-------|--------------|
| [Part 1](scripts-guide-part1-core-scripts.md) | **Core Scripts** | Creating worktrees, listing worktrees |
| [Part 2](scripts-guide-part2-management-scripts.md) | **Management Scripts** | Removing worktrees, validating registry |
| [Part 3](scripts-guide-part3-port-scripts.md) | **Port Scripts** | Allocating ports, checking port status |
| [Part 4](scripts-guide-part4-workflows.md) | **Common Workflows** | Step-by-step procedures for typical tasks |
| [Part 5](scripts-guide-part5-troubleshooting.md) | **Troubleshooting** | Problem resolution, best practices |

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Script Reference](#script-reference) (links to parts)
4. [Best Practices Summary](#best-practices-summary)
5. [Quick Reference Command Matrix](#quick-reference-command-matrix)

---

## Overview

### What Are Worktree Automation Scripts?

Worktree automation scripts are Python programs that help you manage git worktrees efficiently. A **git worktree** is a separate directory containing a checkout of your repository, allowing you to work on multiple branches simultaneously without switching between them.

### Purpose of Automation Scripts

These scripts automate five critical operations:

1. **Creation** - Set up new worktrees with proper naming, registration, and port allocation
2. **Discovery** - List and filter existing worktrees by purpose, status, or assigned ports
3. **Removal** - Clean up worktrees safely with validation and confirmation
4. **Validation** - Verify registry integrity and fix inconsistencies automatically
5. **Port Management** - Allocate, track, and release development server ports

### Why Use These Scripts Instead of Manual Commands?

**Manual approach problems:**
- Forgetting to update the registry file (`.claude/worktree-registry.json`)
- Port conflicts between worktrees running development servers
- Inconsistent naming conventions
- Orphaned worktree directories after branch deletion
- No tracking of worktree purpose or completion status

**Automated approach benefits:**
- Automatic registry updates with metadata
- Guaranteed unique port allocation per service
- Enforced naming standards (purpose-identifier format)
- Validation checks before removal
- Centralized worktree lifecycle tracking

---

## Prerequisites

### Required Software Versions

- **Python 3.8 or higher** - Required for type hints and modern syntax
- **Git 2.20 or higher** - Required for `git worktree` subcommand support

### How to Check Your Versions

```bash
# Check Python version
python3 --version
# Expected output: Python 3.8.x or higher

# Check Git version
git --version
# Expected output: git version 2.20.x or higher
```

### Required Directory Structure

All scripts expect this standard layout:

```
repository-root/
├── .git/                          # Main git directory
├── .claude/                       # Claude configuration directory
│   └── worktree-registry.json    # Worktree metadata database (auto-created)
├── scripts/                       # Automation scripts location
│   ├── worktree_create.py
│   ├── worktree_list.py
│   ├── worktree_remove.py
│   ├── registry_validate.py
│   ├── port_allocate.py
│   └── port_status.py
└── worktrees/                     # Parent directory for all worktrees (auto-created)
    ├── review-GH-42/
    ├── feature-auth-system/
    └── hotfix-CVE-2024-001/
```

### Registry File Format

The registry file (`.claude/worktree-registry.json`) is automatically created and maintained by the scripts. Example structure:

```json
{
  "worktrees": {
    "review-GH-42": {
      "path": "/absolute/path/to/worktrees/review-GH-42",
      "branch": "feature/authentication",
      "purpose": "review",
      "identifier": "GH-42",
      "created_at": "2024-01-15T10:30:00",
      "completed": false,
      "ports": {
        "web": 8001,
        "api": 9001
      }
    }
  },
  "port_allocations": {
    "8001": {
      "worktree": "review-GH-42",
      "service": "web",
      "allocated_at": "2024-01-15T10:30:00"
    }
  }
}
```

---

## Script Reference

### Core Scripts (Part 1)

See [scripts-guide-part1-core-scripts.md](scripts-guide-part1-core-scripts.md) for full details.

**worktree_create.py** - Creates new git worktrees
- TOC:
  - Purpose and usage syntax
  - Required arguments (--purpose, --identifier, --branch)
  - Optional arguments (--ports)
  - Examples: review worktree, feature with ports, hotfix from tag, experiment
  - Exit codes

**worktree_list.py** - Lists and filters worktrees
- TOC:
  - Purpose and usage syntax
  - Filter arguments (--purpose, --status, --ports, --json, --validate)
  - Examples: all active, by purpose, with ports, JSON output, validation
  - Exit codes

### Management Scripts (Part 2)

See [scripts-guide-part2-management-scripts.md](scripts-guide-part2-management-scripts.md) for full details.

**worktree_remove.py** - Safely removes worktrees
- TOC:
  - Purpose and usage syntax
  - Arguments (WORKTREE_NAME, --force, --dry-run, --all-completed)
  - Examples: safe removal, force removal, dry run, batch removal
  - Safety checks performed
  - Exit codes

**registry_validate.py** - Validates and fixes registry
- TOC:
  - Purpose and usage syntax
  - Arguments (--fix, --verbose)
  - Examples: validation only, auto-fix, verbose mode
  - Validation checks performed
  - Exit codes

### Port Scripts (Part 3)

See [scripts-guide-part3-port-scripts.md](scripts-guide-part3-port-scripts.md) for full details.

**port_allocate.py** - Allocates and releases ports
- TOC:
  - Purpose and usage syntax
  - Arguments (--service, --release, --check, --available, --worktree)
  - Examples: allocate port, release port, check availability, list available
  - Port ranges by service
  - Exit codes

**port_status.py** - Displays port allocation status
- TOC:
  - Purpose and usage syntax
  - Arguments (--all, --worktree, --service, --health-check, --json)
  - Examples: all ports, specific worktree, health check, JSON output
  - Health check behavior
  - Exit codes

---

## Common Workflows (Part 4)

See [scripts-guide-part4-workflows.md](scripts-guide-part4-workflows.md) for full details.

| Workflow | Description |
|----------|-------------|
| Code Review Setup | Create isolated environment for PR review |
| Feature Development | Multi-service development with port allocation |
| Cleanup Old Worktrees | Batch removal of completed work |
| Emergency Hotfix | Quick worktree from production tag |
| Experiment Without Risk | Test changes without affecting main codebase |
| Validate After Manual Ops | Fix registry after manual git operations |

---

## Troubleshooting (Part 5)

See [scripts-guide-part5-troubleshooting.md](scripts-guide-part5-troubleshooting.md) for full details.

| Problem | Quick Solution |
|---------|----------------|
| "worktree already exists" but empty | `registry_validate.py --fix` |
| "no ports available" | `port_status.py --all` then cleanup |
| "corrupted JSON" | Restore from backup |
| Health check shows ERROR | Check firewall, test with `nc -zv` |
| "uncommitted changes" false positive | Check untracked files with `git status --porcelain` |
| Port RUNNING but connection refused | Check `lsof -i :PORT` for wrong process |
| Python version too old | Use `python3` explicitly |
| Git worktree already exists | `git worktree remove` then retry |
| Permission denied | `chmod +x` and check PATH |
| Registry too large | `worktree_remove.py --all-completed --force` |

---

## Best Practices Summary

1. **Always use scripts for worktree lifecycle** - Don't mix manual git commands with automation
2. **Regular validation** - Run `registry_validate.py` weekly or after manual operations
3. **Cleanup completed work** - Remove finished worktrees to free ports and disk space
4. **Use descriptive identifiers** - Makes tracking and debugging easier
5. **Allocate ports at creation time** - Use `--ports` flag to avoid manual allocation later
6. **Validate before removal** - Use `--dry-run` to preview destructive operations
7. **Keep backups** - Registry backups are created automatically, don't delete them
8. **Monitor port usage** - Run `port_status.py --all` periodically to check capacity
9. **Document purpose** - Use appropriate purpose values for clear organization
10. **Health check before debugging** - Use `--health-check` to verify services are running

---

## Quick Reference Command Matrix

| Task | Command | Key Options |
|------|---------|-------------|
| Create worktree | `worktree_create.py` | `--purpose`, `--identifier`, `--branch`, `--ports` |
| List worktrees | `worktree_list.py` | `--purpose`, `--status`, `--ports`, `--json`, `--validate` |
| Remove worktree | `worktree_remove.py <name>` | `--force`, `--dry-run`, `--all-completed` |
| Validate registry | `registry_validate.py` | `--fix`, `--verbose` |
| Allocate port | `port_allocate.py` | `--service`, `--worktree`, `--release`, `--check`, `--available` |
| Check port status | `port_status.py` | `--all`, `--worktree`, `--service`, `--health-check`, `--json` |

---

## Port Ranges by Service

| Service     | Range        | Default Start |
|-------------|--------------|---------------|
| web         | 8000-8099    | 8000          |
| api         | 9000-9099    | 9000          |
| db          | 5432-5532    | 5432          |
| redis       | 6379-6479    | 6379          |
| grpc        | 50051-50151  | 50051         |
| websocket   | 3000-3099    | 3000          |

---

## Valid Purpose Values

| Purpose | Description | Typical Use Case |
|---------|-------------|------------------|
| `review` | Code review or PR testing | Reviewing someone's pull request |
| `feature` | New feature development | Building new functionality |
| `bugfix` | Bug fix work | Fixing non-critical bugs |
| `hotfix` | Emergency production fix | Critical security or functionality fixes |
| `experiment` | Experimental/research work | Testing architectural changes |
| `refactor` | Code refactoring | Improving code structure |
| `docs` | Documentation updates | Updating or adding documentation |

---

**End of Scripts Guide Index**

**Detailed documentation:**
- [Part 1: Core Scripts](scripts-guide-part1-core-scripts.md)
- [Part 2: Management Scripts](scripts-guide-part2-management-scripts.md)
- [Part 3: Port Scripts](scripts-guide-part3-port-scripts.md)
- [Part 4: Common Workflows](scripts-guide-part4-workflows.md)
- [Part 5: Troubleshooting](scripts-guide-part5-troubleshooting.md)
