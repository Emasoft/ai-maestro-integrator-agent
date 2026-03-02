# Removing Worktrees - Part 3: Advanced Operations

## Table of Contents
1. [If you need to remove multiple worktrees → Bulk Removal](#bulk-removal)
   - 1.1 [Method 1: Loop Through List](#method-1-loop-through-list)
   - 1.2 [Method 2: From Registry Query](#method-2-from-registry-query)
   - 1.3 [Method 3: Age-Based Removal](#method-3-age-based-removal)
   - 1.4 [Method 4: Interactive Selection](#method-4-interactive-selection)
   - 1.5 [Bulk Removal Script](#bulk-removal-script)
2. [When you need to verify successful removal → Verification](#verification)
   - 2.1 [Verification Checklist](#verification-checklist)
   - 2.2 [Verification Commands](#verification-commands)
   - 2.3 [Verification Script](#verification-script)
3. [If you encounter removal problems → Troubleshooting](#troubleshooting)
   - 3.1 [Cannot remove current worktree](#problem-cannot-remove-current-worktree)
   - 3.2 [Removal succeeds but directory still exists](#problem-removal-succeeds-but-directory-still-exists)
   - 3.3 [Registry shows more worktrees than git](#problem-registry-shows-more-worktrees-than-git)
   - 3.4 [Prune removes wrong worktree](#problem-prune-removes-wrong-worktree)
   - 3.5 [Force removal fails](#problem-force-removal-fails)
4. [Quick command reference → Quick Reference](#quick-reference)

**Related Parts:**
- [Part 1: Preparation and Basic Commands](removing-worktrees-part1-basics.md)
- [Part 2: Post-Removal and Automation](removing-worktrees-part2-post-removal.md)
- [Index: All Removal Topics](removing-worktrees-index.md)

---

## Bulk Removal

**What is bulk removal?**
Removing multiple worktrees in one operation (e.g., all merged PRs, all completed reviews).

### Method 1: Loop Through List

```bash
# Remove all worktrees for merged PRs
for worktree_id in review-GH-42 review-GH-45 review-GH-47; do
  echo "Removing $worktree_id..."
  ./scripts/cleanup-worktree.sh "$worktree_id"
done
```

### Method 2: From Registry Query

```bash
# Remove all worktrees with status "completed"
jq -r '.worktrees[] | select(.status == "completed") | .worktree_id' \
  design/worktree-registry.json | while read -r worktree_id; do
  echo "Removing $worktree_id..."
  ./scripts/cleanup-worktree.sh "$worktree_id"
done
```

### Method 3: Age-Based Removal

```bash
# Remove worktrees older than 30 days
CUTOFF=$(date -d '30 days ago' -Iseconds)

jq -r ".worktrees[] | select(.created_at < \"$CUTOFF\") | .worktree_id" \
  design/worktree-registry.json | while read -r worktree_id; do
  echo "Removing old worktree: $worktree_id..."
  ./scripts/cleanup-worktree.sh "$worktree_id"
done
```

### Method 4: Interactive Selection

```bash
# Show all worktrees and prompt for removal
git worktree list

echo "Enter worktree IDs to remove (space-separated):"
read -r worktree_ids

for worktree_id in $worktree_ids; do
  ./scripts/cleanup-worktree.sh "$worktree_id"
done
```

### Bulk Removal Script

**Location:** `scripts/bulk-cleanup-worktrees.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# bulk-cleanup-worktrees.sh - Remove multiple worktrees
# Usage: ./bulk-cleanup-worktrees.sh <condition>
# Conditions: merged, closed, completed, older-than-30d

CONDITION="${1:-}"
REGISTRY_PATH="design/worktree-registry.json"

if [[ -z "$CONDITION" ]]; then
  echo "Usage: $0 <merged|closed|completed|older-than-30d>"
  exit 1
fi

case "$CONDITION" in
  merged)
    # Get worktrees where PR is merged
    jq -r '.worktrees[] | select(.pr_status == "merged") | .worktree_id' \
      "$REGISTRY_PATH"
    ;;
  closed)
    # Get worktrees where PR is closed
    jq -r '.worktrees[] | select(.pr_status == "closed") | .worktree_id' \
      "$REGISTRY_PATH"
    ;;
  completed)
    # Get worktrees marked completed
    jq -r '.worktrees[] | select(.status == "completed") | .worktree_id' \
      "$REGISTRY_PATH"
    ;;
  older-than-30d)
    # Get worktrees older than 30 days
    CUTOFF=$(date -d '30 days ago' -Iseconds 2>/dev/null || date -u -v-30d +"%Y-%m-%dT%H:%M:%S%z")
    jq -r ".worktrees[] | select(.created_at < \"$CUTOFF\") | .worktree_id" \
      "$REGISTRY_PATH"
    ;;
  *)
    echo "Unknown condition: $CONDITION"
    exit 1
    ;;
esac | while read -r worktree_id; do
  echo "Removing: $worktree_id"
  ./scripts/cleanup-worktree.sh "$worktree_id" || echo "Failed: $worktree_id"
done

echo "✓ Bulk cleanup complete"
```

---

## Verification

**Why verify:**
- Confirm removal was successful
- Detect partial failures
- Ensure registry is consistent
- Validate resource cleanup

### Verification Checklist

```markdown
## Post-Removal Verification

- [ ] **Git Worktree List**: Worktree not shown in `git worktree list`
- [ ] **Directory Removed**: Path does not exist
- [ ] **Registry Updated**: Entry removed from registry
- [ ] **Ports Released**: Ports show as available
- [ ] **Agent Updated**: Agent assignment cleared
- [ ] **Logs Written**: Removal logged
- [ ] **No Stale References**: No broken symlinks or references
```

### Verification Commands

**Check 1: Git worktree list**
```bash
git worktree list | grep review-GH-42
# Should return nothing (exit code 1)
```

**Check 2: Directory exists**
```bash
test -d "${PROJECT_ROOT}/review-GH-42" && echo "EXISTS" || echo "REMOVED"
# Should output: REMOVED
```

**Check 3: Registry updated**
```bash
jq '.worktrees[] | select(.worktree_id == "review-GH-42")' design/worktree-registry.json
# Should return nothing
```

**Check 4: Ports released**
```bash
# Check each port that was allocated
lsof -i :3000  # Should return nothing
lsof -i :8000  # Should return nothing
```

**Check 5: No git references**
```bash
git branch -a | grep review-GH-42
# Should return nothing (unless branch still exists on remote)
```

### Verification Script

**Location:** `scripts/verify-worktree-removal.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# verify-worktree-removal.sh - Verify worktree was fully removed
# Usage: ./verify-worktree-removal.sh <worktree-id>

WORKTREE_ID="${1:-}"
REGISTRY_PATH="design/worktree-registry.json"

if [[ -z "$WORKTREE_ID" ]]; then
  echo "Usage: $0 <worktree-id>"
  exit 1
fi

echo "=== Verifying Removal: $WORKTREE_ID ==="

FAILED=0

# Check 1: Git worktree list
echo -n "→ Git worktree list... "
if git worktree list | grep -q "$WORKTREE_ID"; then
  echo "FAIL (still in git worktree list)"
  FAILED=$((FAILED + 1))
else
  echo "PASS"
fi

# Check 2: Registry
echo -n "→ Registry cleanup... "
if jq -e ".worktrees[] | select(.worktree_id == \"$WORKTREE_ID\")" "$REGISTRY_PATH" > /dev/null 2>&1; then
  echo "FAIL (still in registry)"
  FAILED=$((FAILED + 1))
else
  echo "PASS"
fi

# Check 3: Directory removed
echo -n "→ Directory removed... "
if [[ -d "../$WORKTREE_ID" ]]; then
  echo "FAIL (directory still exists)"
  FAILED=$((FAILED + 1))
else
  echo "PASS"
fi

# Check 4: Removal logged
echo -n "→ Removal logged... "
if grep -q "$WORKTREE_ID" design/worktree-removal-log.txt 2>/dev/null; then
  echo "PASS"
else
  echo "WARN (not logged)"
fi

# Summary
echo ""
if [[ $FAILED -eq 0 ]]; then
  echo "✓ Verification PASSED - Worktree fully removed"
  exit 0
else
  echo "✗ Verification FAILED - $FAILED checks failed"
  exit 1
fi
```

---

## Troubleshooting

### Problem: "Cannot remove current worktree"

**Full error:**
```
fatal: 'review-GH-42' is the current worktree
```

**Cause:**
You're inside the worktree you're trying to remove.

**Solution:**
```bash
# Change to main repository or different directory
cd "${PROJECT_ROOT}"

# Now remove
git worktree remove review-GH-42
```

### Problem: Removal succeeds but directory still exists

**Cause:**
- Permissions prevent deletion
- Files in use by process
- File system issue

**Solution:**
```bash
# Check for processes
lsof +D /path/to/review-GH-42

# Manually remove directory
rm -rf /path/to/review-GH-42

# Prune git metadata
git worktree prune
```

### Problem: Registry shows more worktrees than git

**Cause:**
Worktrees removed without updating registry.

**Solution:**
```bash
# Sync registry with git truth
./scripts/sync-registry-with-git.sh
```

### Problem: Prune removes wrong worktree

**Cause:**
`git worktree prune` only removes entries for MISSING directories. It should not affect existing worktrees.

**Prevention:**
Always use `git worktree prune --dry-run` first:
```bash
git worktree prune --dry-run
# Review what would be removed
git worktree prune
```

### Problem: Force removal fails

**Full error:**
```
fatal: unable to delete 'review-GH-42': Directory not empty
```

**Cause:**
Files with special permissions or attributes.

**Solution:**
```bash
# Remove immutable attribute (if on Linux)
chattr -R -i /path/to/review-GH-42

# Remove directory manually
rm -rf /path/to/review-GH-42

# Prune git metadata
git worktree prune
```

---

## Quick Reference

### Common Removal Workflows

**Standard removal:**
```bash
# 1. Check status
cd worktree-dir && git status

# 2. Commit or stash if needed
git add . && git commit -m "message"

# 3. Remove worktree
cd .. && git worktree remove worktree-dir

# 4. Update registry
jq 'del(.worktrees[] | select(.worktree_id == "ID"))' registry.json > temp && mv temp registry.json
```

**Emergency removal:**
```bash
git worktree remove --force worktree-dir && git worktree prune
```

**Bulk removal:**
```bash
./scripts/bulk-cleanup-worktrees.sh merged
```

### Key Commands Summary

| Command | Purpose |
|---------|---------|
| `git worktree remove <path>` | Standard removal |
| `git worktree remove --force <path>` | Force removal (discards changes) |
| `git worktree remove --dry-run <path>` | Preview removal |
| `git worktree prune` | Clean stale entries |
| `git worktree prune --dry-run` | Preview pruning |
| `git worktree unlock <path>` | Unlock locked worktree |
| `git worktree list` | Show all worktrees |

---

**Previous:** [Part 2: Post-Removal and Automation](removing-worktrees-part2-post-removal.md)

**Return to:** [Worktree Management Overview](../SKILL.md)
