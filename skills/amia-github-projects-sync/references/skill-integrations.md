# Skill Integrations

## Table of Contents

1. [When integrating GitHub Projects with other AMOA skills](#overview)
2. [When coordinating with Remote Agent Coordinator](#remote-agent-coordinator)
3. [When working with Code Reviewer skill](#code-reviewer)
4. [When generating reports](#report-generator)
5. [When using AI Maestro messaging](#ai-maestro-messaging)
6. [When syncing with Claude Tasks personal tasks](#claude-tasks-task-sync)

## Overview

GitHub Projects Sync integrates with other AMOA (AI Maestro Orchestration Agent) skills to provide a complete task management workflow. This document describes the integration points and protocols.

**Key Integrations:**

- Remote Agent Coordinator: Task assignment and tracking
- Code Reviewer: PR status and review workflow
- Report Generator: Project status in reports
- AI Maestro: Notification delivery

> **Note:** See `amia-kanban-orchestration` skill for the canonical 8-column system definition.

## Remote Agent Coordinator

When assigning a task to an agent via Remote Agent Coordinator:

### Assignment Protocol

```
1. UPDATE issue status → "In Progress"
2. ADD assignee to issue
3. ADD "agent:{agent-id}" label
4. SEND task via AI Maestro with issue reference
5. ADD comment: "Assigned to [agent-id] at [timestamp]"
```

### Issue Comment on Assignment

```bash
gh issue comment ISSUE_NUMBER --body "$(cat <<'EOF'
## Task Assigned

**Agent**: dev-agent-1
**Assigned**: 2024-01-15 10:30 UTC
**Issue**: #42

### Instructions
See issue description for acceptance criteria.

### Reporting
- Report progress every 4 hours
- Report blockers immediately
- Submit PR when complete
EOF
)"
```

### Status Sync on Agent Report

When agent reports status:

| Agent Report | GitHub Action |
|--------------|---------------|
| `STARTED` | Update status → "In Progress", add in-progress label |
| `PROGRESS` | Add progress comment |
| `BLOCKED` | Update status → "Blocked", add blocked label |
| `COMPLETE` | Verify PR exists, update status → "AI Review" |
| `FAILED` | Add error comment, keep status, notify orchestrator |

### Completion Verification

```bash
#!/bin/bash
# verify-agent-completion.sh ISSUE_NUMBER

ISSUE="$1"

# Check for linked PR
PR_NUMBER=$(gh issue view "$ISSUE" --json body --jq '.body' | grep -oE 'PR #[0-9]+' | head -1 | tr -d 'PR #')

if [ -z "$PR_NUMBER" ]; then
  echo "ERROR: No PR linked to issue #$ISSUE"
  exit 1
fi

# Check PR status
PR_STATE=$(gh pr view "$PR_NUMBER" --json state --jq '.state')
CI_STATUS=$(gh pr checks "$PR_NUMBER" --json state --jq '.[] | select(.state != "SUCCESS") | .name')

if [ "$PR_STATE" = "MERGED" ]; then
  echo "DONE: PR #$PR_NUMBER merged"
elif [ -z "$CI_STATUS" ]; then
  echo "READY: PR #$PR_NUMBER CI passing, ready for review"
else
  echo "PENDING: PR #$PR_NUMBER has failing checks: $CI_STATUS"
fi
```

## Code Reviewer

After Code Reviewer completes PR review:

### Review Approved

```
1. REMOVE "review:needed" label
2. ADD "review:approved" label
3. UPDATE project item status → "Merge/Release" (ready to merge)
4. ADD comment with approval summary
```

### Changes Requested

```
1. REMOVE "review:needed" label
2. ADD "review:changes-requested" label
3. UPDATE project item status → "In Progress"
4. ADD comment with required changes
5. NOTIFY agent via AI Maestro
```

### Review Comment Template

```bash
gh issue comment ISSUE_NUMBER --body "$(cat <<'EOF'
## Code Review Complete

**Reviewer**: Code Reviewer Skill
**PR**: #52
**Decision**: Changes Requested

### Required Changes
1. Add input validation to login endpoint
2. Fix SQL injection vulnerability in user query
3. Add missing unit tests for error cases

### Next Steps
Agent should address feedback and push new commits.
Re-review will be triggered automatically.
EOF
)"
```

### Label Updates on Review

```bash
# On approval
gh issue edit ISSUE_NUMBER --remove-label "review:needed" --add-label "review:approved"

# On changes requested
gh issue edit ISSUE_NUMBER --remove-label "review:needed" --add-label "review:changes-requested"
gh pr edit PR_NUMBER --add-label "needs-work"
```

## Report Generator

Include GitHub Projects data in generated reports.

### Data Points for Reports

| Metric | Query |
|--------|-------|
| Issues by status | `gh issue list --state all --json labels \| jq 'group_by(.labels[].name)'` |
| Sprint progress | Count items by project status column |
| Blocked items | `gh issue list --label "status:blocked"` |
| Agent assignments | `gh issue list --label "agent:*"` |

### Report Section Template

```markdown
## Project Status

### By Status
| Status | Count |
|--------|-------|
| Backlog | 12 |
| Todo | 5 |
| In Progress | 3 |
| AI Review | 1 |
| Human Review | 1 |
| Merge/Release | 0 |
| Blocked | 1 |
| Done | 8 |

### Sprint Progress
- **Sprint 5**: 8/15 complete (53%)
- **Blocked Issues**: 1 (see #47)
- **At Risk**: 2 (behind schedule)

### Agent Workload
| Agent | In Progress | Completed |
|-------|-------------|-----------|
| dev-agent-1 | 2 | 5 |
| dev-agent-2 | 1 | 3 |
```

### Report Generation Script

```bash
#!/bin/bash
# generate-project-report.sh

PROJECT_ID="$1"

echo "# Project Status Report"
echo "Generated: $(date -u +"%Y-%m-%d %H:%M UTC")"
echo ""

# Status counts
echo "## Status Summary"
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
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq -r '
  .data.node.items.nodes
  | map(.fieldValues.nodes[0].name // "Unknown")
  | group_by(.)
  | map({status: .[0], count: length})
  | .[] | "| \(.status) | \(.count) |"
'
```

## AI Maestro Messaging

For complete messaging documentation, see the official AI Maestro skill:

```
~/.claude/skills/agent-messaging/SKILL.md
```

### Event Notification Types

| Event | Notification Type | Priority |
|-------|------------------|----------|
| Task assigned | `task_assigned` | normal |
| Task blocked | `task_blocked` | high |
| PR ready for review | `pr_ready` | normal |
| CI failed | `ci_failure` | high |
| Sprint complete | `sprint_complete` | low |

### Sending Notifications

Send notifications using the `agent-messaging` skill. For example, to send a task blocked notification:

- **Recipient**: `orchestrator-master`
- **Subject**: `Task Blocked: #42`
- **Priority**: `high`
- **Content**: `{"type": "task_blocked", "issue": 42, "reason": "Waiting for API spec"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## Claude Tasks Task Sync

GitHub Projects is for team/project tasks. Claude Tasks is for orchestrator personal tasks only.

**GitHub Projects** (team tasks):

- Feature implementation
- Bug fixes
- Code reviews
- Documentation

**Claude Tasks** (orchestrator personal tasks):

- Read skill documentation
- Review agent reports
- Plan sprint priorities
- Compile status reports

### Creating Claude Tasks Reminder for GitHub Issue

When a GitHub issue needs orchestrator attention:

```bash
# Add Claude Tasks task to review an issue
# Use TodoWrite tool in Claude Code
- [ ] Review blocked issue #42 - API dependency (priority: high, due: tomorrow)
```

### Linking Pattern

Do not duplicate tasks. Use references:

```
Claude Tasks Task: "Review #42 blocker" → Links to → GitHub Issue #42
```

The GitHub issue contains all details. Claude Tasks just reminds the orchestrator to check it.
