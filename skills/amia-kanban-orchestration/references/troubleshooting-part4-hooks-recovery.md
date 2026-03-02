# Troubleshooting Part 4: Stop Hook and Recovery Issues

## Table of Contents

- [10.7 Stop Hook Issues](#107-stop-hook-issues)
  - [Stop Hook False Positive](#stop-hook-false-positive)
  - [Stop Hook Not Firing](#stop-hook-not-firing)
  - [Stop Hook Timeout](#stop-hook-timeout)
- [10.8 Recovery](#108-recovery)
  - [Full Board State Recovery](#full-board-state-recovery)
  - [Orphaned Item Cleanup](#orphaned-item-cleanup)
  - [Emergency Manual Fix](#emergency-manual-fix)

---

## 10.7 Stop Hook Issues

### Stop Hook False Positive

**Symptom:** Stop hook blocks exit but work is actually complete.

**Diagnosis:**
```bash
# Check what stop hook sees
python3 scripts/amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER
```

**Cause:**
- Board not updated after merge
- Item stuck in wrong status
- Orphaned items

**Solution:**
1. Update board to reflect reality
2. Or use manual override if verified complete

### Stop Hook Not Firing

**Symptom:** Can exit with incomplete work (stop hook not running).

**Diagnosis:**
- Check hook configuration
- Verify hook script is executable
- Check hook logs

**Solution:**
```bash
# Verify hook is configured
cat .claude/plugins/integrator-agent/hooks/hooks.json | jq '.hooks.Stop'

# Make script executable
chmod +x scripts/stop_hook.sh

# Test manually
./scripts/stop_hook.sh
```

### Stop Hook Timeout

**Symptom:** Stop hook takes too long, times out.

**Diagnosis:**
- Check network connectivity
- Check API rate limits

**Solution:**
- Increase timeout in configuration
- Cache board state for faster checks

---

## 10.8 Recovery

### Full Board State Recovery

When board state is severely corrupted:

```bash
#!/bin/bash
# recover_board_state.sh

PROJECT_NUMBER=$1
OWNER=$2
REPO=$3

echo "Starting board recovery..."

# 1. Get all issues in repo
gh issue list --repo "$OWNER/$REPO" --json number,state,title --limit 1000 > issues.json

# 2. Get all items in project
gh project item-list $PROJECT_NUMBER --owner $OWNER --format json > project_items.json

# 3. For each issue, verify it's in project
for issue in $(jq -r '.[].number' issues.json); do
  IN_PROJECT=$(jq -r --arg n "$issue" '.items[] | select(.content.number == ($n | tonumber)) | .id' project_items.json)

  if [ -z "$IN_PROJECT" ]; then
    echo "Issue #$issue not in project, adding..."
    gh project item-add $PROJECT_NUMBER --owner $OWNER --url "https://github.com/$OWNER/$REPO/issues/$issue"
  fi
done

# 4. Reconcile statuses
for issue in $(jq -r '.[].number' issues.json); do
  STATE=$(jq -r --arg n "$issue" '.[] | select(.number == ($n | tonumber)) | .state' issues.json)

  if [ "$STATE" == "CLOSED" ]; then
    echo "Issue #$issue closed, setting to Done"
    # [Update status to Done]
  fi
done

echo "Recovery complete"
```

### Orphaned Item Cleanup

Remove project items that no longer have issues:

```bash
# Find orphaned items (items without content)
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            content {
              ... on Issue { number }
              ... on PullRequest { number }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | select(.content == null or .content.number == null)
  | .id
'

# Delete orphaned items
for item_id in $(cat orphaned_items.txt); do
  gh api graphql -f query='
    mutation($projectId: ID!, $itemId: ID!) {
      deleteProjectV2Item(input: { projectId: $projectId, itemId: $itemId }) {
        deletedItemId
      }
    }
  ' -f projectId="$PROJECT_ID" -f itemId="$item_id"
done
```

### Emergency Manual Fix

When automation fails, manual fix via GitHub UI:

1. Go to project board in browser
2. Drag items to correct columns
3. Edit item fields directly
4. Verify issue states match

Document all manual fixes:
```bash
gh issue comment 42 --body "Manual fix: Moved to Done column after PR merge automation failed."
```
