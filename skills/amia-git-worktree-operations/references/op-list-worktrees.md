---
name: op-list-worktrees
description: "List all active git worktrees in the repository"
procedure: support-skill
workflow-instruction: support
---

# Operation: List Worktrees


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Run basic list command](#step-1-run-basic-list-command)
  - [Step 2: Get detailed information (porcelain format)](#step-2-get-detailed-information-porcelain-format)
  - [Step 3: Parse into structured format](#step-3-parse-into-structured-format)
  - [Step 4: Check worktree health](#step-4-check-worktree-health)
  - [Step 5: Count worktrees](#step-5-count-worktrees)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Worktree Status Values](#worktree-status-values)
- [Detecting Specific Worktrees](#detecting-specific-worktrees)
- [Error Handling](#error-handling)
  - [Not in a git repository](#not-in-a-git-repository)
  - [Stale worktree entries](#stale-worktree-entries)
- [Complete List Script](#complete-list-script)
- [Verification](#verification)

## Purpose

Display all active git worktrees for the repository, showing their paths, branches, and status.

## When to Use

- Before creating a new worktree to check what exists
- When delegating work to see available worktrees
- For status overview of parallel work
- Before cleanup to identify stale worktrees

## Prerequisites

1. Inside a git repository
2. Git version 2.15 or higher

## Procedure

### Step 1: Run basic list command

```bash
git worktree list
```

Output format:
```
/path/to/main       abc1234 [main]
/tmp/worktrees/pr-123 def5678 [pr-123]
/tmp/worktrees/pr-456 ghi9012 [pr-456]
```

### Step 2: Get detailed information (porcelain format)

```bash
git worktree list --porcelain
```

Output format:
```
worktree /path/to/main
HEAD abc1234567890
branch refs/heads/main

worktree /tmp/worktrees/pr-123
HEAD def5678901234
branch refs/heads/pr-123

worktree /tmp/worktrees/pr-456
HEAD ghi9012345678
branch refs/heads/pr-456
```

### Step 3: Parse into structured format

```bash
# Parse porcelain output into JSON
git worktree list --porcelain | awk '
BEGIN { print "["; first=1 }
/^worktree / {
  if (!first) print ","
  first=0
  path=$2
}
/^HEAD / { head=substr($0, 6) }
/^branch / {
  branch=$2
  gsub(/refs\/heads\//, "", branch)
  printf "{\"path\":\"%s\",\"commit\":\"%s\",\"branch\":\"%s\"}", path, head, branch
}
END { print "]" }
'
```

### Step 4: Check worktree health

```bash
# Check for stale/locked worktrees
for wt in $(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do
  if [ ! -d "$wt" ]; then
    echo "STALE: $wt (directory missing)"
  elif [ -f "$wt/.git/index.lock" ]; then
    echo "LOCKED: $wt (has index.lock)"
  else
    echo "OK: $wt"
  fi
done
```

### Step 5: Count worktrees

```bash
WORKTREE_COUNT=$(git worktree list | wc -l)
echo "Total worktrees: $WORKTREE_COUNT"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| format | string | no | Output format: text, json, porcelain |
| include_main | boolean | no | Whether to include main worktree (default: true) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| worktrees | object[] | List of worktree objects |
| count | number | Total number of worktrees |
| stale_count | number | Number of stale worktrees |

## Example Output

```json
{
  "worktrees": [
    {
      "path": "/Users/dev/project",
      "commit": "abc1234",
      "branch": "main",
      "is_main": true,
      "status": "ok"
    },
    {
      "path": "/tmp/worktrees/pr-123",
      "commit": "def5678",
      "branch": "pr-123",
      "is_main": false,
      "status": "ok"
    }
  ],
  "count": 2,
  "stale_count": 0
}
```

## Worktree Status Values

| Status | Meaning |
|--------|---------|
| `ok` | Worktree is healthy |
| `stale` | Directory doesn't exist |
| `locked` | Index lock present |
| `detached` | HEAD is detached |

## Detecting Specific Worktrees

```bash
# Find worktree for specific branch
git worktree list | grep "pr-123"

# Find worktree for specific PR
PR_NUMBER=123
git worktree list | grep "pr-$PR_NUMBER"

# Check if worktree exists for path
WORKTREE_PATH="/tmp/worktrees/pr-123"
if git worktree list | grep -q "$WORKTREE_PATH"; then
  echo "Worktree exists at $WORKTREE_PATH"
fi
```

## Error Handling

### Not in a git repository

**Cause**: Command run outside git repo.

**Solution**: Navigate to repository first.

### Stale worktree entries

**Cause**: Worktree was deleted without using git worktree remove.

**Solution**: Run `git worktree prune` to clean up.

## Complete List Script

```bash
#!/bin/bash
# list_worktrees.sh

FORMAT="${1:-text}"

echo "=== Git Worktrees ==="

case "$FORMAT" in
  text)
    git worktree list
    echo ""
    echo "Total: $(git worktree list | wc -l | tr -d ' ') worktrees"
    ;;

  json)
    echo "["
    first=true
    while IFS= read -r line; do
      path=$(echo "$line" | awk '{print $1}')
      commit=$(echo "$line" | awk '{print $2}')
      branch=$(echo "$line" | grep -oP '\[.*\]' | tr -d '[]')

      if [ "$first" = true ]; then
        first=false
      else
        echo ","
      fi

      # Check status
      if [ ! -d "$path" ]; then
        status="stale"
      elif [ -f "$path/.git/index.lock" ]; then
        status="locked"
      else
        status="ok"
      fi

      echo "  {\"path\":\"$path\",\"commit\":\"$commit\",\"branch\":\"$branch\",\"status\":\"$status\"}"
    done < <(git worktree list)
    echo "]"
    ;;

  porcelain)
    git worktree list --porcelain
    ;;

  *)
    echo "Unknown format: $FORMAT"
    echo "Use: text, json, or porcelain"
    exit 1
    ;;
esac
```

## Verification

Use list to verify worktree operations:

```bash
# After creating worktree
git worktree list | grep "pr-123" && echo "Worktree exists"

# After removing worktree
git worktree list | grep -q "pr-123" || echo "Worktree removed"

# Check for stale entries
STALE=$(git worktree list --porcelain | grep -c "prunable")
echo "Stale worktrees: $STALE"
```
