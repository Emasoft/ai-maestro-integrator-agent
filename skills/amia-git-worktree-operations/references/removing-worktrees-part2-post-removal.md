# Removing Worktrees - Part 2: Post-Removal and Automation

## Table of Contents
1. [After removing a worktree → Post-Removal Steps](#post-removal-steps)
   - 1.1 [Update Registry](#step-1-update-registry)
   - 1.2 [Release Allocated Ports](#step-2-release-allocated-ports)
   - 1.3 [Clean Up Remaining Files](#step-3-clean-up-remaining-files)
   - 1.4 [Update Agent Assignments](#step-4-update-agent-assignments)
   - 1.5 [Document Removal](#step-5-document-removal)
2. [If you want to automate worktree cleanup → Cleanup Script](#cleanup-script)
3. [When worktree removal fails → Handling Failures](#handling-failures)
   - 3.1 [Failure: Locked Worktree](#failure-locked-worktree)
   - 3.2 [Failure: Missing Worktree Path](#failure-missing-worktree-path)
   - 3.3 [Failure: Registry Out of Sync](#failure-registry-out-of-sync)
   - 3.4 [Failure: Permission Denied](#failure-permission-denied)
   - 3.5 [Failure: Worktree Has Uncommitted Changes](#failure-worktree-has-uncommitted-changes)

**Related Parts:**
- [Part 1: Preparation and Basic Commands](removing-worktrees-part1-basics.md)
- [Part 3: Advanced Operations](removing-worktrees-part3-advanced.md)
- [Index: All Removal Topics](removing-worktrees-index.md)

---

## Post-Removal Steps

### Step 1: Update Registry

**What to do:**
Remove or mark the worktree entry as deleted in `design/worktree-registry.json`.

**Method A - Remove entry (recommended):**
```bash
# Use jq to remove entry
jq 'del(.worktrees[] | select(.worktree_id == "review-GH-42"))' \
  design/worktree-registry.json > temp.json && \
  mv temp.json design/worktree-registry.json
```

**Method B - Mark as deleted:**
```bash
# Update status field
jq '(.worktrees[] | select(.worktree_id == "review-GH-42") | .status) = "deleted"' \
  design/worktree-registry.json > temp.json && \
  mv temp.json design/worktree-registry.json
```

**Manual method (if jq unavailable):**
```bash
# Edit registry file
nano design/worktree-registry.json

# Remove this block:
# {
#   "worktree_id": "review-GH-42",
#   ...
# }

# Save and exit
```

**Verification:**
```bash
# Check entry is gone
cat design/worktree-registry.json | grep "review-GH-42"
# Should return nothing
```

### Step 2: Release Allocated Ports

**What are allocated ports?**
Network ports (e.g., 3000, 8000) that were reserved for this worktree's development servers.

**Why release them:**
- Other worktrees can reuse these ports
- Prevents port exhaustion
- Maintains port allocation accuracy

**How to release:**

**Option A - Update port tracker:**
```bash
# If using design/port-allocations.json
jq 'del(.allocations["review-GH-42"])' \
  design/port-allocations.json > temp.json && \
  mv temp.json design/port-allocations.json
```

**Option B - Manual registry update:**
```bash
# Edit registry and remove ports array from worktree entry
# This happens automatically if you removed the entry in Step 1
```

**Verify ports are free:**
```bash
# Check port 3000 is not in use
lsof -i :3000
# Should return nothing

# Check port 8000 is not in use
lsof -i :8000
# Should return nothing
```

### Step 3: Clean Up Remaining Files

**What remaining files?**
Files outside the worktree directory that might be related:
- Build artifacts
- Log files
- Temporary caches
- Database files (SQLite, etc.)
- Config files with worktree paths

**Common locations:**
```bash
# Build output directories
rm -rf /tmp/build-review-GH-42

# Application logs
rm -rf logs/review-GH-42-*.log

# Database files
rm -f data/review-GH-42.db

# Temporary files
rm -rf /tmp/review-GH-42-*
```

**Check for symlinks:**
```bash
# Find broken symlinks pointing to removed worktree
find . -type l ! -exec test -e {} \; -print

# Remove broken symlinks
find . -type l ! -exec test -e {} \; -delete
```

### Step 4: Update Agent Assignments

**What is an agent assignment?**
The record of which AI agent was working in this worktree.

**Why update:**
- Agent may be waiting for tasks in removed worktree
- Frees agent for new assignments
- Prevents confusion in agent tracking

**How to update:**

**Option A - AI Maestro messaging:**

Send a message using the `agent-messaging` skill with:
- **Recipient**: `code-reviewer-1`
- **Subject**: `Worktree review-GH-42 removed`
- **Priority**: `normal`
- **Content**: `{"type": "notification", "message": "Worktree review-GH-42 has been removed. You are now available for new assignments."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Option B - Update agent registry:**
```bash
# If using design/agent-assignments.json
jq '(.agents[] | select(.agent_id == "code-reviewer-1") | .assigned_worktree) = null' \
  design/agent-assignments.json > temp.json && \
  mv temp.json design/agent-assignments.json
```

### Step 5: Document Removal

**Why document:**
- Audit trail for worktree lifecycle
- Helps debug registry issues
- Tracks resource usage over time

**What to record:**
```bash
# Append to removal log
echo "$(date -Iseconds) | review-GH-42 | GH-42 merged | removed by orchestrator" \
  >> design/worktree-removal-log.txt
```

**Log format:**
```
TIMESTAMP | WORKTREE_ID | REASON | REMOVED_BY
2025-12-31T10:30:00+00:00 | review-GH-42 | PR merged | orchestrator
2025-12-31T11:15:00+00:00 | review-GH-43 | PR closed | manual
```

---

## Cleanup Script

**What is the cleanup script?**
An automated script that performs all removal and post-removal steps in one command.

**Location:**
`scripts/cleanup-worktree.sh`

**Usage:**
```bash
# Basic usage
./scripts/cleanup-worktree.sh review-GH-42

# With force removal
./scripts/cleanup-worktree.sh --force review-GH-42

# Dry run (show what would be removed)
./scripts/cleanup-worktree.sh --dry-run review-GH-42
```

**Script contents:**
```bash
#!/usr/bin/env bash
set -euo pipefail

# cleanup-worktree.sh - Automated worktree removal
# Usage: ./cleanup-worktree.sh [--force] [--dry-run] <worktree-id>

FORCE=false
DRY_RUN=false
REGISTRY_PATH="design/worktree-registry.json"
LOG_PATH="design/worktree-removal-log.txt"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force) FORCE=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) WORKTREE_ID="$1"; shift ;;
  esac
done

if [[ -z "${WORKTREE_ID:-}" ]]; then
  echo "Error: Worktree ID required"
  echo "Usage: $0 [--force] [--dry-run] <worktree-id>"
  exit 1
fi

echo "=== Worktree Removal: $WORKTREE_ID ==="

# Step 1: Get worktree info from registry
echo "→ Looking up worktree in registry..."
if ! ENTRY=$(jq -r ".worktrees[] | select(.worktree_id == \"$WORKTREE_ID\")" "$REGISTRY_PATH"); then
  echo "Error: Worktree $WORKTREE_ID not found in registry"
  exit 1
fi

WORKTREE_PATH=$(echo "$ENTRY" | jq -r '.path')
PORTS=$(echo "$ENTRY" | jq -r '.ports[]')
AGENT=$(echo "$ENTRY" | jq -r '.assigned_agent // "none"')

echo "  Path: $WORKTREE_PATH"
echo "  Ports: $PORTS"
echo "  Agent: $AGENT"

if [[ "$DRY_RUN" == true ]]; then
  echo ""
  echo "DRY RUN - Would perform:"
  echo "  1. Remove worktree: $WORKTREE_PATH"
  echo "  2. Release ports: $PORTS"
  echo "  3. Update registry"
  echo "  4. Notify agent: $AGENT"
  echo "  5. Log removal"
  exit 0
fi

# Step 2: Check for uncommitted work (unless --force)
if [[ "$FORCE" == false ]] && [[ -d "$WORKTREE_PATH" ]]; then
  echo "→ Checking for uncommitted work..."
  if ! git -C "$WORKTREE_PATH" diff-index --quiet HEAD --; then
    echo "Error: Worktree has uncommitted changes"
    echo "Options:"
    echo "  1. Commit changes: cd $WORKTREE_PATH && git commit -am 'message'"
    echo "  2. Stash changes: cd $WORKTREE_PATH && git stash"
    echo "  3. Force remove: $0 --force $WORKTREE_ID"
    exit 1
  fi
fi

# Step 3: Remove worktree
echo "→ Removing worktree..."
if [[ "$FORCE" == true ]]; then
  git worktree remove --force "$WORKTREE_PATH" || true
else
  git worktree remove "$WORKTREE_PATH" || true
fi

# Step 4: Prune stale entries
echo "→ Pruning stale entries..."
git worktree prune

# Step 5: Update registry
echo "→ Updating registry..."
jq "del(.worktrees[] | select(.worktree_id == \"$WORKTREE_ID\"))" \
  "$REGISTRY_PATH" > "$REGISTRY_PATH.tmp" && \
  mv "$REGISTRY_PATH.tmp" "$REGISTRY_PATH"

# Step 6: Notify agent (if assigned)
# Use the agent-messaging skill to send this notification.
if [[ "$AGENT" != "none" ]] && [[ "$AGENT" != "null" ]]; then
  echo "→ Notifying agent: $AGENT..."
  echo "  ACTION REQUIRED: Send a message using the agent-messaging skill:"
  echo "    Recipient: $AGENT"
  echo "    Subject: Worktree $WORKTREE_ID removed"
  echo "    Content: {\"type\":\"notification\",\"message\":\"Worktree $WORKTREE_ID has been removed.\"}"
  echo "    Priority: normal"
fi

# Step 7: Log removal
echo "→ Logging removal..."
echo "$(date -Iseconds) | $WORKTREE_ID | removed | $(whoami)" >> "$LOG_PATH"

echo ""
echo "✓ Worktree $WORKTREE_ID successfully removed"
echo "  Released ports: $PORTS"
echo "  Agent freed: $AGENT"
```

**Making script executable:**
```bash
chmod +x scripts/cleanup-worktree.sh
```

**Integration with task agents:**
```bash
# From orchestrator - delegate cleanup to task agent
Task: "Run cleanup script for review-GH-42"
```

---

## Handling Failures

### Failure: Locked Worktree

**Symptom:**
```
fatal: 'review-GH-42' is locked
```

**Cause:**
Worktree is marked as locked (usually due to concurrent operations or crash).

**Solution:**
```bash
# Check lock status
git worktree list
# Output shows [locked]

# Unlock worktree
git worktree unlock ../review-GH-42

# Verify unlock
git worktree list
# [locked] should be gone

# Now remove
git worktree remove ../review-GH-42
```

**Why worktrees get locked:**
- Git operation crashed mid-execution
- Multiple git commands ran simultaneously
- Manual lock for safety

### Failure: Missing Worktree Path

**Symptom:**
```
fatal: '../review-GH-42' does not exist
```

**Cause:**
Directory was deleted manually without using `git worktree remove`.

**Solution:**
```bash
# Check if git still tracks it
git worktree list
# Shows: /path/to/review-GH-42 [missing]

# Clean up git metadata
git worktree prune

# Verify cleanup
git worktree list
# Entry should be gone
```

### Failure: Registry Out of Sync

**Symptom:**
Registry shows worktree exists, but `git worktree list` doesn't show it.

**Cause:**
- Worktree removed without updating registry
- Registry manually edited incorrectly
- Script failure during removal

**Solution:**
```bash
# Step 1: Get truth from git
git worktree list > /tmp/actual-worktrees.txt

# Step 2: Compare with registry
cat design/worktree-registry.json | jq -r '.worktrees[].worktree_id'

# Step 3: Identify orphaned registry entries
# (Entries in registry but not in git worktree list)

# Step 4: Remove orphaned entries
jq 'del(.worktrees[] | select(.worktree_id == "orphaned-id"))' \
  design/worktree-registry.json > temp.json && \
  mv temp.json design/worktree-registry.json
```

**Prevention:**
Always use cleanup script or manual process that updates registry.

### Failure: Permission Denied

**Symptom:**
```
error: unable to delete file: Permission denied
```

**Cause:**
- Files owned by different user
- Running processes have files open
- File system permissions issue

**Solution:**

**Step 1: Check for running processes:**
```bash
lsof +D /path/to/review-GH-42
# Kill any processes found
kill <PID>
```

**Step 2: Check file ownership:**
```bash
ls -la /path/to/review-GH-42
# If owned by different user, use sudo or fix ownership
sudo chown -R $(whoami) /path/to/review-GH-42
```

**Step 3: Retry removal:**
```bash
git worktree remove review-GH-42
```

### Failure: Worktree Has Uncommitted Changes

**Symptom:**
```
fatal: 'review-GH-42' contains modified or untracked files, use --force to delete it
```

**Cause:**
Uncommitted changes exist and standard removal prevents data loss.

**Solutions (choose one):**

**Option 1: Commit changes**
```bash
cd review-GH-42
git add .
git commit -m "Final changes before removal"
git push
cd ..
git worktree remove review-GH-42
```

**Option 2: Stash changes**
```bash
cd review-GH-42
git stash push -m "Changes from review-GH-42"
cd ..
git worktree remove review-GH-42
```

**Option 3: Force remove (discard changes)**
```bash
git worktree remove --force review-GH-42
```

---

**Continue to:** [Part 3: Advanced Operations](removing-worktrees-part3-advanced.md)

**Previous:** [Part 1: Preparation and Basic Commands](removing-worktrees-part1-basics.md)

**Return to:** [Worktree Management Overview](../SKILL.md)
