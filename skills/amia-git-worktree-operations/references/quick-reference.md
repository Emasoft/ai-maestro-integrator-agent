# Quick Reference

## Contents
- [Essential Git Commands](#essential-git-commands) - Core worktree commands
- [Registry Commands](#registry-commands) - Registry access and validation
- [Port Management Commands](#port-management-commands) - Port allocation and status
- [Script Quick Reference](#script-quick-reference) - All available scripts
- [Common Patterns](#common-patterns) - Frequently used command sequences

---

## Essential Git Commands

### List All Worktrees
```bash
git worktree list
```
Shows all worktrees with their paths and branches.

### Create New Worktree
```bash
# Create from existing branch
git worktree add ../worktree-name branch-name

# Create with new branch
git worktree add -b new-branch ../worktree-name base-branch
```

### Remove Worktree
```bash
# Standard removal
git worktree remove ../worktree-name

# Force removal (if dirty)
git worktree remove --force ../worktree-name
```

### Lock Worktree
```bash
# Prevent accidental deletion
git worktree lock ../worktree-name

# With reason
git worktree lock --reason "Long-running experiment" ../worktree-name
```

### Unlock Worktree
```bash
git worktree unlock ../worktree-name
```

### Move Worktree
```bash
git worktree move ../old-path ../new-path
```

### Prune Stale Worktrees
```bash
# Dry run
git worktree prune --dry-run

# Actually prune
git worktree prune
```

---

## Registry Commands

### View Registry Contents
```bash
cat ~/design/worktree-registry.json
```

### Pretty Print Registry
```bash
cat ~/design/worktree-registry.json | python -m json.tool
```

### Validate Registry
```bash
python scripts/registry_validate.py
```

### List Worktrees with Details
```bash
python scripts/worktree_list.py
```

### List as JSON
```bash
python scripts/worktree_list.py --format json
```

---

## Port Management Commands

### Find Next Available Port
```bash
python scripts/port_allocate.py --find-next
```

### Show Port Usage
```bash
python scripts/port_status.py
```

### Allocate Port to Worktree
```bash
python scripts/port_allocate.py --worktree myworktree --port 8101
```

### Check Specific Port
```bash
python scripts/port_status.py --port 8101
```

### Release Port
```bash
python scripts/port_allocate.py --release --port 8101
```

---

## Script Quick Reference

| Script | Purpose | Common Usage |
|--------|---------|--------------|
| `worktree_create.py` | Create worktree | `--name NAME --branch BRANCH --port PORT` |
| `worktree_list.py` | List worktrees | `--format [table\|json]` |
| `worktree_remove.py` | Remove worktree | `--name NAME` |
| `registry_validate.py` | Validate registry | `--fix-orphans` |
| `port_allocate.py` | Manage ports | `--find-next` or `--worktree NAME --port PORT` |
| `port_status.py` | Port report | `--port PORT` |
| `merge_safeguard.py` | Merge validation | `--check PATH` or `--conflicts` |

---

## Common Patterns

### Create Feature Branch Worktree
```bash
python scripts/worktree_create.py \
  --name feature-xyz \
  --branch feature/xyz \
  --port 8101
cd ../feature-xyz
```

### Review PR in Isolation
```bash
python scripts/worktree_create.py \
  --name review-pr-123 \
  --branch pr/123/head \
  --port 8120
cd ../review-pr-123
npm install && npm start --port 8120
```

### Check Health Before Merge
```bash
python scripts/merge_safeguard.py --check .
python scripts/merge_safeguard.py --conflicts
```

### Clean Up After Feature Complete
```bash
cd ../main-repo
python scripts/worktree_remove.py --name feature-xyz
python scripts/registry_validate.py
```

### Daily Maintenance
```bash
python scripts/registry_validate.py
python scripts/port_status.py
git worktree prune --dry-run
```

### Emergency Hotfix
```bash
python scripts/worktree_create.py \
  --name hotfix-urgent \
  --branch hotfix/urgent-fix \
  --base-branch production \
  --port 8100
```
