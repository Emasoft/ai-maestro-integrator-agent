# Worktree Verification - Part 3: Automated and Manual Verification

[Back to Worktree Verification Index](worktree-verification.md)

## Table of Contents

- [4.5 Automated Verification Script Usage](#45-automated-verification-script-usage)
  - [Using amia_verify_worktree_isolation.py](#using-amia_verify_worktree_isolationpy)
  - [Interpreting Script Output](#interpreting-script-output)
  - [Integrating Verification into Workflow](#integrating-verification-into-workflow)
- [4.6 Manual Verification When Scripts Fail](#46-manual-verification-when-scripts-fail)
  - [When to Use Manual Verification](#when-to-use-manual-verification)
  - [Manual Verification Procedure](#manual-verification-procedure)
  - [Manual Verification Checklist](#manual-verification-checklist)

---

## 4.5 Automated Verification Script Usage

### Using amia_verify_worktree_isolation.py

This script performs comprehensive isolation verification.

**Basic usage:**

```bash
python scripts/amia_verify_worktree_isolation.py \
    --worktree-path /tmp/worktrees/pr-123
```

**With main repo check:**

```bash
python scripts/amia_verify_worktree_isolation.py \
    --worktree-path /tmp/worktrees/pr-123 \
    --main-repo /path/to/main-repo
```

**Check all worktrees:**

```bash
for wt in /tmp/worktrees/*/; do
    python scripts/amia_verify_worktree_isolation.py \
        --worktree-path "$wt" \
        --main-repo /path/to/main-repo
done
```

### Interpreting Script Output

**Success output:**

```json
{
  "status": "clean",
  "worktree": "/tmp/worktrees/pr-123",
  "violations": [],
  "warnings": []
}
```

**Failure output:**

```json
{
  "status": "violation",
  "worktree": "/tmp/worktrees/pr-123",
  "violations": [
    {
      "type": "file_outside_worktree",
      "path": "/path/to/main-repo/src/changed.py",
      "details": "File modified during worktree session"
    }
  ],
  "warnings": [
    "Untracked files exist in worktree"
  ]
}
```

### Integrating Verification into Workflow

**Before commit:**

```bash
# Verify before committing
python scripts/amia_verify_worktree_isolation.py -w /tmp/worktrees/pr-123
if [ $? -ne 0 ]; then
    echo "Isolation violation detected, aborting commit"
    exit 1
fi
git -C /tmp/worktrees/pr-123 commit -m "Safe commit"
```

**Before cleanup:**

```bash
# Verify before removal
python scripts/amia_verify_worktree_isolation.py -w /tmp/worktrees/pr-123
if [ $? -eq 0 ]; then
    git worktree remove /tmp/worktrees/pr-123
else
    echo "Fix violations before cleanup"
fi
```

---

## 4.6 Manual Verification When Scripts Fail

### When to Use Manual Verification

- Verification scripts are not available
- Scripts report inconclusive results
- Scripts fail to run (missing dependencies)
- Need human judgment for edge cases

### Manual Verification Procedure

**Step 1: Visual inspection of main repo**

```bash
cd /path/to/main-repo
git status
# Manually review any changes shown
```

**Step 2: Check file timestamps**

```bash
# List recently modified files
ls -lt /path/to/main-repo/src/ | head -20
# Compare modification times with session start time
```

**Step 3: Review git log**

```bash
cd /path/to/main-repo
git log --oneline -10
# Verify no unexpected commits
```

**Step 4: Compare directories**

```bash
# Visual diff between worktree and main repo
diff -rq /tmp/worktrees/pr-123 /path/to/main-repo \
    --exclude=.git --exclude=__pycache__ --exclude=node_modules
```

**Step 5: Check for process locks**

```bash
# Find processes with files open in main repo
lsof +D /path/to/main-repo 2>/dev/null

# Find processes in worktree
lsof +D /tmp/worktrees/pr-123 2>/dev/null
```

### Manual Verification Checklist

```
MANUAL VERIFICATION CHECKLIST
=============================
□ Ran 'git status' in main repo - no unexpected changes
□ Ran 'git status' in worktree - clean or expected changes
□ Checked file timestamps - no suspicious modifications
□ Reviewed git log - no unexpected commits
□ Compared directories - differences are expected
□ Checked for open processes - none blocking cleanup

Notes:
_________________________________________________
_________________________________________________
_________________________________________________
```

---

[Back to Worktree Verification Index](worktree-verification.md) | [Previous: Part 2](worktree-verification-part2-branch-remote-sync.md) | [Next: Part 4](worktree-verification-part4-reporting.md)
