# Status Management - Part 2: Operations

## Table of Contents

1. [When updating status via API or scripts](#status-change-api)
   - 1.1 [Update status script](#update-status-script)
2. [When generating status reports or summaries](#status-reporting)
   - 2.1 [Current status summary script](#current-status-summary)
   - 2.2 [Status history via issue timeline](#status-history-via-issue-timeline)
3. [When issues need attention or escalation](#alerting-rules)
   - 3.1 [Inactive work detection](#inactive-work-detection)
   - 3.2 [Long review alerts](#long-review)
   - 3.3 [Blocked too long alerts](#blocked-too-long)
4. [When deciding whether to close inactive issues](#issue-lifecycle-policy-no-stale)
   - 4.1 [Core principle: Issues stay open until solved](#core-principle-issues-stay-open-until-solved)
   - 4.2 [When feature requests can be closed](#feature-requests--enhancements)
   - 4.3 [When bug reports can be closed](#bug-reports)
   - 4.4 [What to do with inactive issues](#what-happens-to-inactive-issues)
   - 4.5 [Prohibited auto-close actions](#prohibited-actions)
   - 4.6 [Labels for issue management](#labels-for-issue-management-instead-of-closing)
5. [When following status management best practices](#best-practices)

**Parent document**: [Status Management](./status-management.md)

---

## Status Change API

### Update Status Script

```bash
#!/bin/bash
# update-item-status.sh

PROJECT_ID="$1"
ITEM_ID="$2"
NEW_STATUS="$3"
REASON="$4"

# Get status field ID and option IDs
STATUS_FIELD=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            options { id name }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID")

FIELD_ID=$(echo "$STATUS_FIELD" | jq -r '.data.node.field.id')
OPTION_ID=$(echo "$STATUS_FIELD" | jq -r --arg status "$NEW_STATUS" '.data.node.field.options[] | select(.name == $status) | .id')

# Validate transition (would check against rules)
# ...

# Update status
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item { id }
    }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID"

# Add transition comment
ISSUE_NUMBER=$(gh api graphql -f query='
  query($itemId: ID!) {
    node(id: $itemId) {
      ... on ProjectV2Item {
        content {
          ... on Issue { number }
        }
      }
    }
  }
' -f itemId="$ITEM_ID" | jq -r '.data.node.content.number')

gh issue comment "$ISSUE_NUMBER" --body "Status changed to **$NEW_STATUS**. Reason: $REASON"
```

---

## Status Reporting

### Current Status Summary

```bash
#!/bin/bash
# project-status-summary.sh

PROJECT_ID="$1"

gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            fieldValues(first: 5) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes
  | map(.fieldValues.nodes[] | select(.field.name == "Status") | .name)
  | group_by(.)
  | map({status: .[0], count: length})
  | sort_by(.status)
'
```

Output:
```json
[
  {"status": "Backlog", "count": 12},
  {"status": "Blocked", "count": 1},
  {"status": "Done", "count": 8},
  {"status": "In Progress", "count": 3},
  {"status": "AI Review", "count": 2},
  {"status": "Todo", "count": 5}
]
```

### Status History (via Issue Timeline)

```bash
gh api repos/OWNER/REPO/issues/42/timeline --jq '
  .[] | select(.event == "labeled" or .event == "unlabeled")
  | {event: .event, label: .label.name, time: .created_at}
'
```

---

## Alerting Rules

### Inactive Work Detection

```
IF item.status == "In Progress"
AND item.last_activity > 24 hours
THEN:
  - Send status request to agent
  - Flag for orchestrator review
  - Consider escalation if no response in 4 hours
```

### Long Review

```
IF item.status == "AI Review"
AND item.time_in_status > 48 hours
THEN:
  - Ping reviewers
  - Escalate to orchestrator
  - Consider reassigning review
```

### Blocked Too Long

```
IF item.status == "Blocked"
AND item.time_in_status > 72 hours
THEN:
  - Escalate to user
  - Consider cancellation or scope change
  - Add to morning report highlight
```

---

## Issue Lifecycle Policy (NO STALE)

### Core Principle: Issues Stay Open Until Solved

**IRON RULE**: Issues are NEVER automatically closed due to inactivity or "staleness".

GitHub's stale bot and similar automation that closes issues after periods of inactivity is **PROHIBITED**.

### When Issues CAN Be Closed

#### Feature Requests / Enhancements

Closed ONLY when:
- Implemented, tested, and merged to main
- User/owner explicitly declines the feature (with documented reason)
- Superseded by another issue (link to replacement)

#### Bug Reports

Closed ONLY when:
1. **Bug Fixed**: Code change merged that fixes the bug, with verification test
2. **Cannot Reproduce** (after 3 documented attempts):
   - Attempt 1: Initial reproduction try with documented steps
   - Attempt 2: Follow-up with any clarifications from reporter
   - Attempt 3: Final attempt, possibly on different environment
   - All 3 attempts must be documented in issue comments
   - Close with label `cannot-reproduce` and explanation

**Bug Closure Checklist**:
```markdown
## Reproduction Attempts

- [ ] Attempt 1 (YYYY-MM-DD): [description, environment, result]
- [ ] Attempt 2 (YYYY-MM-DD): [description, any reporter feedback incorporated]
- [ ] Attempt 3 (YYYY-MM-DD): [final attempt, different environment if applicable]

**Conclusion**: Unable to reproduce after 3 documented attempts.
Closing as cannot-reproduce. Will reopen if new reproduction steps provided.
```

#### Tasks / Chores

Closed ONLY when:
- Task completed and verified
- Task no longer relevant (with explanation)

### What Happens to "Inactive" Issues

Instead of closing inactive issues:

| Situation | Action |
|-----------|--------|
| No activity 30+ days | Add `needs-attention` label, ping assignee |
| No response from reporter 14+ days | Add `awaiting-response` label |
| Blocked on external dependency | Add `blocked` label with dependency link |
| Low priority, no resources | Add `backlog` status, keep OPEN |
| Unclear requirements | Add `needs-clarification` label |

### Prohibited Actions

- **NEVER** use stale bot or similar auto-close automation
- **NEVER** close issues just because they're old
- **NEVER** close bugs without reproduction attempts or fix verification
- **NEVER** close without documented reason in comments

### Labels for Issue Management (Instead of Closing)

| Label | Meaning |
|-------|---------|
| `needs-attention` | Inactive but still valid |
| `awaiting-response` | Waiting for reporter input |
| `low-priority` | Valid but not urgent |
| `help-wanted` | Open for community contribution |
| `cannot-reproduce` | Bug closed after 3 failed attempts |
| `wontfix` | Intentionally not addressing (with reason) |

---

## Best Practices

### DO

- Always provide transition reason in comments
- Update status promptly when state changes
- Use labels in addition to project status
- Keep parent issue progress updated
- Log all automated transitions
- Document all bug reproduction attempts
- Keep issues OPEN until genuinely resolved

### DON'T

- Skip intermediate statuses
- Leave items stuck in non-terminal status
- Update status without verifying preconditions
- Ignore sync conflicts
- Manually override without documenting reason
- Close issues due to inactivity
- Use stale bots or auto-close automation
- Close bugs without 3 documented reproduction attempts

---

## Related References

- **[Status Management](./status-management.md)** - Parent document with status definitions
- **[Part 1: Transitions](./status-management-part1-transitions.md)** - Transition rules and sync protocol
- **[Iteration Cycle Rules](./iteration-cycle-rules.md)** - Complete iteration workflow
- **[Review Worktree Workflow](./review-worktree-workflow.md)** - PR review validation
