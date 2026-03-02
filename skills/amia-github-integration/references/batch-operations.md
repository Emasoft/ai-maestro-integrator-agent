# Batch Operations and Filtering

## Table of Contents

- [Use-Case TOC](#use-case-toc)
- [Filtering by Label](#filtering-by-label)
  - [Filter by Single Label](#filter-by-single-label)
  - [Filter by Multiple Labels (AND)](#filter-by-multiple-labels-and)
  - [Filter by Multiple Labels (OR)](#filter-by-multiple-labels-or)
  - [Filter by Status](#filter-by-status)
  - [Filter by Assignee](#filter-by-assignee)
  - [Filter by Date](#filter-by-date)
- [Advanced Filtering](#advanced-filtering)
  - [Complex Filter Examples](#complex-filter-examples)
  - [Saving Filter Results](#saving-filter-results)
  - [Filtering in Projects V2](#filtering-in-projects-v2)
- [Batch Issue Updates](#batch-issue-updates)
  - [Update Labels on Multiple Issues](#update-labels-on-multiple-issues)
  - [Update Assignees on Multiple Issues](#update-assignees-on-multiple-issues)
  - [Update Status in Projects V2](#update-status-in-projects-v2)
- [Bulk Label Operations](#bulk-label-operations)
  - [Add Label to All Matching Issues](#add-label-to-all-matching-issues)
  - [Remove Label from All Issues](#remove-label-from-all-issues)
  - [Replace Label Across All Issues](#replace-label-across-all-issues)
- [Bulk Closing Issues](#bulk-closing-issues)
  - [Close All Issues with Specific Label](#close-all-issues-with-specific-label)
  - [Close Stale Issues](#close-stale-issues)
- [Safe Batch Operations](#safe-batch-operations)
  - [Preview Changes Before Applying](#preview-changes-before-applying)
  - [Create Audit Trail](#create-audit-trail)
  - [Implement Rollback Capability](#implement-rollback-capability)
- [Best Practices](#best-practices)

## Use-Case TOC
- When you need to filter issues by label → [Filtering by Label](#filtering-by-label)
- When you need to update multiple issues → [Batch Issue Updates](#batch-issue-updates)
- When you need to change labels on many issues → [Bulk Label Operations](#bulk-label-operations)
- When you need to bulk close issues → [Bulk Closing Issues](#bulk-closing-issues)
- When you need to verify changes before executing → [Safe Batch Operations](#safe-batch-operations)
- When you need to filter by multiple criteria → [Advanced Filtering](#advanced-filtering)

## Filtering by Label

Filter issues to find specific subsets for batch operations.

### Filter by Single Label

```bash
# List all issues with "feature" label
gh issue list --label "feature" --limit 100

# List all issues with "bug" label
gh issue list --label "bug" --limit 100
```

### Filter by Multiple Labels (AND)

```bash
# Issues that have BOTH "feature" AND "high-priority"
gh issue list --label "feature,high-priority" --limit 100
```

Note: Comma-separated labels create an AND filter (issue must have all labels).

### Filter by Multiple Labels (OR)

For OR filtering, make multiple calls and combine:

```bash
#!/bin/bash
# get-issues-by-labels-or.sh

LABELS=("feature" "bug" "refactor")

for LABEL in "${LABELS[@]}"; do
  gh issue list --label "$LABEL" --json number --jq '.[].number'
done | sort -u
```

### Filter by Status

```bash
# Open issues only (default)
gh issue list --state open

# Closed issues only
gh issue list --state closed

# All issues (open and closed)
gh issue list --state all
```

### Filter by Assignee

```bash
# Issues assigned to you
gh issue list --assignee "@me"

# Issues assigned to specific user
gh issue list --assignee "@username"

# Unassigned issues
gh issue list --assignee ""
```

### Filter by Date

```bash
# Issues created after specific date
gh issue list --search "created:>2024-01-01"

# Issues updated in last 7 days
gh issue list --search "updated:>=$(date -d '7 days ago' +%Y-%m-%d)"

# Issues created this month
gh issue list --search "created:>=$(date +%Y-%m-01)"
```

## Advanced Filtering

Combine multiple filters for complex queries.

### Complex Filter Examples

**Example 1: Open bugs assigned to you, updated recently**
```bash
gh issue list \
  --label "bug" \
  --state open \
  --assignee "@me" \
  --search "updated:>=$(date -d '7 days ago' +%Y-%m-%d)"
```

**Example 2: Features without assignee, ready to work**
```bash
gh issue list \
  --label "feature" \
  --state open \
  --assignee "" \
  --search "label:ready"
```

**Example 3: High-priority security issues**
```bash
gh issue list \
  --label "security,high-priority" \
  --state open \
  --search "sort:updated-desc"
```

### Saving Filter Results

```bash
# Save issue numbers to file
gh issue list --label "feature" --json number --jq '.[].number' > feature-issues.txt

# Save full issue data
gh issue list --label "feature" --json number,title,state,labels > feature-issues.json
```

### Filtering in Projects V2

```bash
# List items in project with specific label
gh project item-list <project_number> \
  --owner "@username" \
  --format json \
  | jq '[.items[] | select(.content.labels[]?.name == "feature")]'
```

## Batch Issue Updates

Update multiple issues simultaneously.

### Update Labels on Multiple Issues

```bash
#!/bin/bash
# batch-update-labels.sh

ISSUES=(123 124 125 126 127)
NEW_LABEL="feature"

for ISSUE in "${ISSUES[@]}"; do
  echo "Updating issue #$ISSUE with label $NEW_LABEL"
  gh issue edit "$ISSUE" --add-label "$NEW_LABEL"
  sleep 1  # Rate limiting
done
```

### Update Assignees on Multiple Issues

```bash
#!/bin/bash
# batch-assign.sh

# Get all unassigned "bug" issues
ISSUES=$(gh issue list --label "bug" --assignee "" --json number --jq '.[].number')

ASSIGNEE="@bug-fixer"

for ISSUE in $ISSUES; do
  echo "Assigning issue #$ISSUE to $ASSIGNEE"
  gh issue edit "$ISSUE" --assignee "$ASSIGNEE"
  sleep 1
done
```

### Update Status in Projects V2

```bash
#!/bin/bash
# batch-update-status.sh

PROJECT_ID=1
ISSUES=(123 124 125)
NEW_STATUS="Ready"

for ISSUE in "${ISSUES[@]}"; do
  ISSUE_URL="https://github.com/owner/repo/issues/$ISSUE"

  echo "Updating issue #$ISSUE to status: $NEW_STATUS"

  # Get item ID (simplified - actual implementation requires GraphQL)
  # Update status using Projects V2 API
  # ... implementation details ...

  sleep 1
done
```

## Bulk Label Operations

Manage labels across multiple issues efficiently.

### Add Label to All Matching Issues

```bash
#!/bin/bash
# add-label-to-matching.sh

FILTER_LABEL="bug"
ADD_LABEL="backlog"

# Get all issues with filter label
ISSUES=$(gh issue list --label "$FILTER_LABEL" --json number --jq '.[].number')

echo "Found $(echo "$ISSUES" | wc -l) issues with label '$FILTER_LABEL'"
echo "Adding label '$ADD_LABEL' to all..."

for ISSUE in $ISSUES; do
  gh issue edit "$ISSUE" --add-label "$ADD_LABEL"
  echo "  ✓ Updated issue #$ISSUE"
  sleep 1
done

echo "Done!"
```

### Remove Label from All Issues

```bash
#!/bin/bash
# remove-label-from-all.sh

LABEL_TO_REMOVE="old-label"

# Get all issues with this label
ISSUES=$(gh issue list --label "$LABEL_TO_REMOVE" --state all --json number --jq '.[].number')

echo "Found $(echo "$ISSUES" | wc -l) issues with label '$LABEL_TO_REMOVE'"
echo "Removing label from all..."

for ISSUE in $ISSUES; do
  gh issue edit "$ISSUE" --remove-label "$LABEL_TO_REMOVE"
  echo "  ✓ Removed from issue #$ISSUE"
  sleep 1
done

echo "Done!"
```

### Replace Label Across All Issues

```bash
#!/bin/bash
# replace-label.sh

OLD_LABEL="enhancement"
NEW_LABEL="feature"

ISSUES=$(gh issue list --label "$OLD_LABEL" --state all --json number --jq '.[].number')

echo "Replacing '$OLD_LABEL' with '$NEW_LABEL' on $(echo "$ISSUES" | wc -l) issues"

for ISSUE in $ISSUES; do
  gh issue edit "$ISSUE" --remove-label "$OLD_LABEL" --add-label "$NEW_LABEL"
  echo "  ✓ Updated issue #$ISSUE"
  sleep 1
done

echo "Done!"
```

## Bulk Closing Issues

Close multiple issues at once with proper documentation.

### Close All Issues with Specific Label

```bash
#!/bin/bash
# close-by-label.sh

LABEL="wontfix"
REASON="not planned"
COMMENT="Closing as won't fix per project roadmap discussion."

ISSUES=$(gh issue list --label "$LABEL" --state open --json number --jq '.[].number')

echo "Closing $(echo "$ISSUES" | wc -l) issues with label '$LABEL'"

for ISSUE in $ISSUES; do
  gh issue close "$ISSUE" --reason "$REASON" --comment "$COMMENT"
  echo "  ✓ Closed issue #$ISSUE"
  sleep 1
done
```

### Close Stale Issues

```bash
#!/bin/bash
# close-stale.sh

# Close issues not updated in 90 days
CUTOFF_DATE=$(date -d '90 days ago' +%Y-%m-%d)

ISSUES=$(gh issue list \
  --state open \
  --search "updated:<$CUTOFF_DATE" \
  --json number \
  --jq '.[].number')

COMMENT="Closing due to inactivity. Please reopen if still relevant."

echo "Closing $(echo "$ISSUES" | wc -l) stale issues"

for ISSUE in $ISSUES; do
  gh issue close "$ISSUE" --reason "not planned" --comment "$COMMENT"
  echo "  ✓ Closed stale issue #$ISSUE"
  sleep 1
done
```

## Safe Batch Operations

Always verify before executing batch operations.

### Preview Changes Before Applying

```bash
#!/bin/bash
# safe-batch-update.sh

LABEL="feature"
NEW_ASSIGNEE="@developer"

# Get issues
ISSUES=$(gh issue list --label "$LABEL" --assignee "" --json number,title --jq '.[] | "\(.number): \(.title)"')

# Show preview
echo "The following issues will be assigned to $NEW_ASSIGNEE:"
echo "$ISSUES"
echo ""
echo "Total: $(echo "$ISSUES" | wc -l) issues"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Execute
  echo "$ISSUES" | cut -d: -f1 | while read ISSUE_NUM; do
    gh issue edit "$ISSUE_NUM" --assignee "$NEW_ASSIGNEE"
    echo "  ✓ Assigned issue #$ISSUE_NUM"
    sleep 1
  done
  echo "Done!"
else
  echo "Cancelled."
fi
```

### Create Audit Trail

```bash
#!/bin/bash
# batch-with-audit.sh

LOG_FILE="batch-operations-$(date +%Y%m%d-%H%M%S).log"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=== Batch Operation Started at $(date) ==="
echo "Operation: Add 'ai-review' label to all 'feature' issues"
echo ""

ISSUES=$(gh issue list --label "feature" --json number --jq '.[].number')

echo "Affected issues: $(echo "$ISSUES" | tr '\n' ', ')"
echo "Total count: $(echo "$ISSUES" | wc -l)"
echo ""

for ISSUE in $ISSUES; do
  echo "[$(date +%H:%M:%S)] Processing issue #$ISSUE"

  if gh issue edit "$ISSUE" --add-label "ai-review"; then
    echo "  ✓ Success"
  else
    echo "  ✗ Failed"
  fi

  sleep 1
done

echo ""
echo "=== Batch Operation Completed at $(date) ==="
```

### Implement Rollback Capability

```bash
#!/bin/bash
# batch-with-rollback.sh

BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).json"
LABEL_TO_ADD="reviewed"

# Backup current state
echo "Creating backup..."
gh issue list --label "feature" --json number,labels > "$BACKUP_FILE"
echo "Backup saved to $BACKUP_FILE"

# Perform operation
ISSUES=$(gh issue list --label "feature" --json number --jq '.[].number')

echo "Adding label '$LABEL_TO_ADD' to $(echo "$ISSUES" | wc -l) issues"

SUCCESS=0
FAILED=0

for ISSUE in $ISSUES; do
  if gh issue edit "$ISSUE" --add-label "$LABEL_TO_ADD"; then
    ((SUCCESS++))
  else
    ((FAILED++))
  fi
  sleep 1
done

echo "Success: $SUCCESS, Failed: $FAILED"

if [ $FAILED -gt 0 ]; then
  echo "Some operations failed. To rollback, run:"
  echo "  ./rollback-from-backup.sh $BACKUP_FILE"
fi
```

## Best Practices

1. **Preview before executing** - Always show what will change before applying
2. **Create backups** - Save current state before batch operations
3. **Add audit logging** - Record all changes with timestamps
4. **Rate limit** - Add `sleep 1` between operations to avoid API limits
5. **Verify filters** - Double-check filter results match expectations
6. **Use confirmation prompts** - Require explicit user confirmation
7. **Implement rollback** - Provide way to undo batch operations
8. **Monitor failures** - Track and report which operations failed
9. **Start small** - Test with small batches before full execution
10. **Document changes** - Add comments to issues explaining bulk changes
