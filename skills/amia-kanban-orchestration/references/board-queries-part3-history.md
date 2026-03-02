# Board Queries - Part 3: History and Completion

This part covers item history tracking and completion checking.

## Table of Contents

- [7.7 Item History](#77-item-history)
  - [Issue Timeline](#issue-timeline)
  - [Project Item History](#project-item-history)
  - [Suggested Comment Logging](#suggested-comment-logging)
- [7.8 Check Completion](#78-check-completion)
  - [Query](#query)
  - [Check Logic](#check-logic)
  - [Exit Codes](#exit-codes)

---

## 7.7 Item History

Get timeline and transitions for an item.

### Issue Timeline

```bash
gh api repos/OWNER/REPO/issues/42/timeline --jq '
  .[] | select(
    .event == "labeled" or
    .event == "unlabeled" or
    .event == "assigned" or
    .event == "unassigned" or
    .event == "moved_columns_in_project"
  ) | {
    event: .event,
    label: .label.name,
    assignee: .assignee.login,
    time: .created_at
  }
'
```

### Project Item History

Note: GitHub Projects V2 doesn't have built-in item history API. Track via:
1. Issue timeline events
2. Comments with status change logs
3. Custom logging in comments

### Suggested Comment Logging

When moving items, always add a comment:

```markdown
**Status Change**
From: In Progress
To: AI Review
Time: 2024-01-15 14:30 UTC
Actor: @agent-1
```

---

## 7.8 Check Completion

Check if all items are in Done status (for stop hook).

### Query

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          totalCount
          nodes {
            fieldValues(first: 5) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                state
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID"
```

### Check Logic

```bash
# Check completion status
RESULT=$(gh api graphql -f query='...')

TOTAL=$(echo "$RESULT" | jq '.data.node.items.totalCount')

DONE=$(echo "$RESULT" | jq '
  [.data.node.items.nodes[].fieldValues.nodes[]
  | select(.field.name == "Status" and .name == "Done")]
  | length
')

BLOCKED=$(echo "$RESULT" | jq '
  [.data.node.items.nodes[].fieldValues.nodes[]
  | select(.field.name == "Status" and .name == "Blocked")]
  | length
')

IN_PROGRESS=$(echo "$RESULT" | jq '
  [.data.node.items.nodes[].fieldValues.nodes[]
  | select(.field.name == "Status" and (.name == "In Progress" or .name == "AI Review" or .name == "Human Review" or .name == "Merge/Release" or .name == "Todo"))]
  | length
')

echo "Total: $TOTAL"
echo "Done: $DONE"
echo "Blocked: $BLOCKED"
echo "In Progress/Todo/Review: $IN_PROGRESS"

if [ "$IN_PROGRESS" -eq 0 ] && [ "$BLOCKED" -eq 0 ]; then
  echo "COMPLETE: All items done"
  exit 0
elif [ "$BLOCKED" -gt 0 ]; then
  echo "BLOCKED: $BLOCKED items blocked"
  exit 2
else
  echo "INCOMPLETE: $IN_PROGRESS items not done"
  exit 1
fi
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All items Done (can exit) |
| 1 | Items still in progress (cannot exit) |
| 2 | Blocked items exist (needs attention) |
