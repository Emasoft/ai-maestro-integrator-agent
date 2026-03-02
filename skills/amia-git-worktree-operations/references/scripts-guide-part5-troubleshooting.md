# Worktree Automation Scripts Guide - Part 5: Troubleshooting

**Related Documents:**
- [Main Index](scripts-guide.md)
- [Part 1: Core Scripts](scripts-guide-part1-core-scripts.md)
- [Part 2: Management Scripts](scripts-guide-part2-management-scripts.md)
- [Part 3: Port Scripts](scripts-guide-part3-port-scripts.md)
- [Part 4: Common Workflows](scripts-guide-part4-workflows.md)

---

## Table of Contents

- [Troubleshooting](#troubleshooting)
  - [Problem: Script says "worktree already exists" but directory is empty](#problem-script-says-worktree-already-exists-but-directory-is-empty)
  - [Problem: Port allocation fails with "no ports available"](#problem-port-allocation-fails-with-no-ports-available)
  - [Problem: Registry validation fails with "corrupted JSON"](#problem-registry-validation-fails-with-corrupted-json)
  - [Problem: Health check shows "ERROR" for all ports](#problem-health-check-shows-error-for-all-ports)
  - [Problem: Worktree removal says "uncommitted changes" but there are none](#problem-worktree-removal-says-uncommitted-changes-but-there-are-none)
  - [Problem: Port shows "RUNNING" but browser says "Connection refused"](#problem-port-shows-running-but-browser-says-connection-refused)
  - [Problem: Multiple worktrees have same identifier](#problem-multiple-worktrees-have-same-identifier)
  - [Problem: Script fails with "Python version too old"](#problem-script-fails-with-python-version-too-old)
  - [Problem: Git says "worktree already exists" after script failure](#problem-git-says-worktree-already-exists-after-script-failure)
  - [Problem: "Permission denied" when running scripts](#problem-permission-denied-when-running-scripts)
  - [Problem: Registry grows too large and slows down scripts](#problem-registry-grows-too-large-and-slows-down-scripts)
  - [Problem: Branch doesn't exist and script can't create it](#problem-branch-doesnt-exist-and-script-cant-create-it)
- [Best Practices Summary](#best-practices-summary)
- [Quick Reference Command Matrix](#quick-reference-command-matrix)

---

## Troubleshooting

This section covers common problems and their solutions.

---

### Problem: Script says "worktree already exists" but directory is empty

**Symptoms:**
```bash
$ python scripts/worktree_create.py --purpose review --identifier GH-42 --branch feature/auth
Error: Worktree 'review-GH-42' already exists in registry
```

But when you check:
```bash
$ ls worktrees/
# Directory doesn't exist or is empty
```

**Cause:** Registry has entry but filesystem doesn't have directory (orphaned entry).

**Solution:**
```bash
# Option 1: Validate and fix registry
python scripts/registry_validate.py --fix

# Option 2: Manually remove from registry then recreate
python scripts/worktree_remove.py review-GH-42 --force
python scripts/worktree_create.py --purpose review --identifier GH-42 --branch feature/auth
```

---

### Problem: Port allocation fails with "no ports available"

**Symptoms:**
```bash
$ python scripts/worktree_create.py --purpose feature --identifier test --branch test --ports
Error: No available ports for service 'web' in range 8000-8099
```

**Cause:** All 100 ports in the range are allocated (unlikely) or registry is corrupted.

**Solution:**
```bash
# Check current port usage
python scripts/port_status.py --all

# If you see fewer than 100 worktrees, validate registry
python scripts/registry_validate.py --fix

# Release ports from completed worktrees
python scripts/worktree_remove.py --all-completed

# Check available ports
python scripts/port_allocate.py --available web
```

---

### Problem: Registry validation fails with "corrupted JSON"

**Symptoms:**
```bash
$ python scripts/registry_validate.py
Error: Registry file is corrupted (invalid JSON)
```

**Cause:** Manual editing broke JSON syntax, or file write was interrupted.

**Solution:**
```bash
# Check if backup exists
ls -la .claude/worktree-registry.json.backup*

# Restore from most recent backup
cp .claude/worktree-registry.json.backup.2024-01-15-103000 .claude/worktree-registry.json

# If no backup exists, rebuild from filesystem
# (This script would need to be created or done manually)
python scripts/rebuild_registry.py
```

**Prevention:** Always use scripts to modify registry, never manual editing.

---

### Problem: Health check shows "ERROR" for all ports

**Symptoms:**
```bash
$ python scripts/port_status.py --all --health-check
review-GH-42:
  web:       8002    [ERROR]  ✗
  api:       9002    [ERROR]  ✗
```

**Cause:** Firewall blocking connections, or script doesn't have network permissions.

**Solution:**
```bash
# Test manual connection
nc -zv localhost 8002

# If that works, check script has correct permissions
ls -la scripts/port_status.py

# Check firewall isn't blocking
# macOS:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Linux:
sudo ufw status
```

---

### Problem: Worktree removal says "uncommitted changes" but there are none

**Symptoms:**
```bash
$ python scripts/worktree_remove.py review-GH-42
Error: Worktree has uncommitted changes (use --force to override)

$ cd worktrees/review-GH-42
$ git status
On branch feature/auth
nothing to commit, working tree clean
```

**Cause:** Untracked files or different git behavior than script expects.

**Solution:**
```bash
# Check for untracked files
cd worktrees/review-GH-42
git status --porcelain

# If you see files listed, either:
# Option 1: Commit them
git add .
git commit -m "WIP"

# Option 2: Force remove anyway
python scripts/worktree_remove.py review-GH-42 --force

# Option 3: Stash untracked files
git stash --include-untracked
```

---

### Problem: Port shows "RUNNING" but browser says "Connection refused"

**Symptoms:**
```bash
$ python scripts/port_status.py --worktree feature-test --health-check
feature-test:
  web:       8001    [RUNNING]  ✓
```

But browser at http://localhost:8001 shows "Connection refused"

**Cause:** Different service is running on that port (not your development server).

**Solution:**
```bash
# Check what's actually running on the port
lsof -i :8001
# or on Linux:
netstat -tulpn | grep 8001

# If it's not your service, kill it
kill <PID>

# Then start your actual development server
cd worktrees/feature-test
npm run dev -- --port 8001
```

---

### Problem: Multiple worktrees have same identifier

**Symptoms:**
```bash
$ python scripts/worktree_list.py
review-GH-42
feature-GH-42
bugfix-GH-42
```

All have identifier "GH-42" but different purposes.

**Cause:** This is actually allowed and intended behavior.

**Explanation:** Identifiers can be reused across different purposes. The unique key is the worktree name (purpose-identifier combination), not just the identifier.

**Not a problem unless:** You want to prevent this for clarity.

**Optional solution:**
```bash
# Use more specific identifiers
--identifier GH-42-auth-review
--identifier GH-42-auth-feature
--identifier GH-42-auth-bugfix
```

---

### Problem: Script fails with "Python version too old"

**Symptoms:**
```bash
$ python scripts/worktree_create.py --purpose review --identifier test --branch test
SyntaxError: invalid syntax (type hints not supported)
```

**Cause:** Running Python 2.7 or Python 3.6/3.7 instead of required 3.8+.

**Solution:**
```bash
# Check current version
python --version
python3 --version

# Use python3 explicitly
python3 scripts/worktree_create.py --purpose review --identifier test --branch test

# Or update Python
# macOS with Homebrew:
brew install python@3.12

# Linux (Ubuntu/Debian):
sudo apt install python3.12
```

---

### Problem: Git says "worktree already exists" after script failure

**Symptoms:**
```bash
$ python scripts/worktree_create.py --purpose review --identifier GH-42 --branch feature/auth
Error: Git command failed: worktree already exists
```

**Cause:** Script failed mid-execution, git created worktree but registry wasn't updated.

**Solution:**
```bash
# Check git's worktree list
git worktree list

# If you see the worktree:
git worktree remove worktrees/review-GH-42

# Then retry creation
python scripts/worktree_create.py --purpose review --identifier GH-42 --branch feature/auth

# Or validate and fix
python scripts/registry_validate.py --fix
```

---

### Problem: "Permission denied" when running scripts

**Symptoms:**
```bash
$ python scripts/worktree_create.py --purpose review --identifier test --branch test
-bash: python: Permission denied
```

**Cause:** Scripts need execute permissions or Python path is wrong.

**Solution:**
```bash
# Check file permissions
ls -la scripts/worktree_create.py

# Make executable if needed
chmod +x scripts/worktree_create.py

# Run with explicit Python interpreter
python3 scripts/worktree_create.py --purpose review --identifier test --branch test

# Check Python is in PATH
which python3
```

---

### Problem: Registry grows too large and slows down scripts

**Symptoms:**
- Scripts take several seconds to run
- Registry file is over 1MB

**Cause:** Too many completed worktrees still in registry.

**Solution:**
```bash
# Remove all completed worktrees
python scripts/worktree_remove.py --all-completed --force

# Validate and cleanup
python scripts/registry_validate.py --fix

# Check new file size
ls -lh .claude/worktree-registry.json
```

**Prevention:** Regular cleanup of completed worktrees (weekly or monthly).

---

### Problem: Branch doesn't exist and script can't create it

**Symptoms:**
```bash
$ python scripts/worktree_create.py --purpose feature --identifier test --branch feature/new
Error: Branch 'feature/new' does not exist and cannot be created
```

**Cause:** Starting point for new branch is ambiguous (git doesn't know what to branch from).

**Solution:**
```bash
# Create branch manually first from current HEAD
git branch feature/new

# Or create from specific commit/branch
git branch feature/new main

# Then create worktree
python scripts/worktree_create.py --purpose feature --identifier test --branch feature/new

# Or specify base branch in script
python scripts/worktree_create.py --purpose feature --identifier test --branch feature/new --base main
```

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

| Task | Command | Options |
|------|---------|---------|
| Create worktree | `worktree_create.py` | `--purpose`, `--identifier`, `--branch`, `--ports` |
| List worktrees | `worktree_list.py` | `--purpose`, `--status`, `--ports`, `--json`, `--validate` |
| Remove worktree | `worktree_remove.py <name>` | `--force`, `--dry-run`, `--all-completed` |
| Validate registry | `registry_validate.py` | `--fix`, `--verbose` |
| Allocate port | `port_allocate.py` | `--service`, `--worktree`, `--release`, `--check`, `--available` |
| Check port status | `port_status.py` | `--all`, `--worktree`, `--service`, `--health-check`, `--json` |

---

**End of Part 5: Troubleshooting**

**Return to:** [Main Index](scripts-guide.md)
