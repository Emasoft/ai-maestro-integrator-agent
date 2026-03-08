# GitHub Projects Sync — Detailed Guide

## Contents

- [Critical Distinction](#critical-distinction)
- [When to Invoke](#when-to-invoke)
- [Iron Rules Compliance](#iron-rules-compliance)
- [Issue Lifecycle Policy](#issue-lifecycle-policy)
- [AI Maestro Integration](#ai-maestro-integration)
- [Threshold Configuration](#threshold-configuration)
- [Error Handling Details](#error-handling-details)
- [Status Columns](#status-columns)
- [Reference File Contents Index](#reference-file-contents-index)

## Critical Distinction

- **GitHub Projects** = Team/Project tasks (features, bugs, PRs, issues)
- **Claude Tasks** = Orchestrator personal tasks ONLY (reading docs, planning, reviewing)

## When to Invoke

- Assigning GitHub issues to remote agents
- Tracking feature implementation progress
- Synchronizing PR status with project boards
- Managing sprint/iteration planning
- Generating project status reports
- Coordinating multi-agent work on features

## Iron Rules Compliance

This skill is **READ + STATUS UPDATE ONLY**:

- Query project state via GraphQL API
- Update card status (Todo -> In Progress -> Done)
- Add comments and labels to issues
- Link PRs to project items
- **NEVER**: Execute code, run tests, modify source files

## Issue Lifecycle Policy

**IRON RULE**: Issues are NEVER automatically closed due to inactivity.

| Issue Type | Closure Conditions |
|------------|-------------------|
| Feature | Implemented + merged, OR explicitly declined with reason |
| Bug | Fixed + verified, OR 3 documented reproduction attempts failed |
| Chore | Completed and verified |

For inactive issues, use labels (`needs-attention`, `awaiting-response`, `low-priority`) instead of closing.

See `references/status-management.md` for complete policy.

## AI Maestro Integration

For all inter-agent messaging, refer to the official AI Maestro skill:

```
~/.claude/skills/agent-messaging/SKILL.md
```

Use the `agent-messaging` skill to send notifications. For example, to notify the orchestrator, send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-master`
- **Subject**: Your notification subject
- **Content**: `{"type": "TYPE", "message": "MSG"}`
- **Priority**: The appropriate priority level
- **Verify**: Confirm message delivery via the `agent-messaging` skill's sent messages feature.

## Threshold Configuration

The `../shared/thresholds.py` module defines automation thresholds:

| Threshold | Value | Purpose |
|-----------|-------|---------|
| MAX_CONSECUTIVE_FAILURES | 3 | CI failures before escalation |
| INACTIVE_HOURS | 24 | Hours before flagging inactive items |
| LONG_REVIEW_HOURS | 48 | Hours before review escalation |
| BLOCKED_ESCALATION_HOURS | 72 | Hours before user escalation |

See `references/automation-scripts.md` for usage.

## Error Handling Details

When GitHub API calls or sync operations fail, consult `references/error-handling.md` for retry logic, rate-limit handling, and authentication troubleshooting. All errors should be logged and, if unresolvable after retries, escalated via AI Maestro.

## Status Columns

**Standard Columns:** Backlog -> Todo -> In Progress -> AI Review -> Human Review -> Merge/Release -> Done (+ Blocked)

## Reference File Contents Index

### Core Operations (`references/core-operations.md`)

- 1.1 When starting with GitHub Projects operations
- 1.2 When creating issues with project items
- 1.3 When updating project item status
- 1.4 When querying all project items
- 1.5 When linking PRs to issues
- 1.6 When adding comments to issues
- 1.7 When managing assignees

### GraphQL API Queries (`references/graphql-queries.md`)

- When listing projects
- When getting project items
- When updating item status
- When creating issues via GraphQL
- When working with custom fields

Sub-files:

- `references/graphql-queries-part1-read-operations.md` — All read queries
- `references/graphql-queries-part2-mutations.md` — All mutations

### Status Management (`references/status-management.md`)

- 3.1 When starting with status management
- 3.2 When you need to understand status meanings and metadata
- 3.3 When moving issues between statuses (transition rules)
- 3.4 When syncing GitHub state with project board
- 3.5 When updating status via API or scripts
- 3.6 When generating status reports or summaries
- 3.7 When issues need attention or escalation
- 3.8 When deciding whether to close inactive issues (NO STALE policy)
- 3.9 When following status management best practices

### Label Taxonomy (`references/label-taxonomy.md`)

- 4.1 When starting with the label system
- 4.2 When you need to know available label categories
- 4.3 When creating or managing labels via CLI
- 4.4 When applying labels automatically or manually
- 4.5 When searching or filtering issues by labels
- 4.6 When generating label statistics and counts
- 4.7 When following label usage best practices
- 4.8 When choosing label colors

Label categories: type:*, priority:*, status:*, component:*, effort:*, agent:*, review:*

### Issue Templates (`references/issue-templates.md`)

- 5.1-5.11 Templates for features, bugs, epics, refactoring, docs, PRs, CODEOWNERS, CLI

### Sub-Issue Tracking (`references/sub-issue-tracking.md`)

- 6.1 When breaking down large features into sub-issues
- 6.2 When creating parent/child issue relationships
- 6.3 When tracking progress across sub-issues
- 6.4 When automating progress updates
- 6.5 When using task lists for tracking
- 6.6 When querying sub-issue status

### Skill Integrations (`references/skill-integrations.md`)

- 7.1-7.6 Integration with Remote Agent Coordinator, Code Reviewer, Reports, AI Maestro, Claude Tasks

### CI Notification Setup (`references/ci-notification-setup.md`)

- 8.1-8.8 Webhook config, event types, security, multi-repo, CI integration

### Error Handling (`references/error-handling.md`)

- 9.1-9.7 API errors, rate limits, not found, update failures, auth, webhook, retry logic

### Best Practices (`references/best-practices.md`)

- 10.1-10.6 Project board state, issues/PRs, common mistakes, inactive issues, documentation

### Automation Scripts (`references/automation-scripts.md`)

- 11.1-11.5 sync_tasks.py, ci_webhook_handler.py, amia_kanban_sync.py, thresholds

### GitHub Sync Procedure (`references/github-sync-procedure.md`)

- 1.1-1.11 Auth, env vars, fetch, sync issues, sync back, labels, custom fields, Claude Tasks, errors, reports, troubleshooting

### Planning & Iteration

- `references/planning-phase-mapping.md` — Phase-to-status mapping, auto transitions, workflow examples
- `references/iteration-cycle-rules.md` — Sprint/iteration management, review flow, PR labeling

### Review & Plan Files

- `references/review-worktree-workflow.md` — Isolated review environment setup
- `references/plan-file-linking.md` — GitHub issue to plan file linking

### Examples & Troubleshooting (`references/examples-and-inline-troubleshooting.md`)

- E.1 Find and Query a Project
- E.2 Update Issue Status
- E.3-E.7 Troubleshooting: missing projects, board sync, column sync, rate limiting, task sync
