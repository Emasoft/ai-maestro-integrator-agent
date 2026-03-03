---
name: amia-github-projects-sync
description: Use when managing team tasks through GitHub Projects V2 or synchronizing project state via GraphQL API. Trigger with /sync-projects or when updating project items.
license: Apache-2.0
compatibility: "Requires GitHub CLI authentication, GitHub Projects V2 enabled repository, GraphQL API access, Python 3.8+, and AI Maestro integration for notifications. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Projects Sync

## Overview

The GitHub Projects Sync skill enables the INTEGRATOR-AGENT to manage team tasks through GitHub Projects V2. This is the OFFICIAL task management interface for coordinating work across remote developer agents.

**Critical Distinction**:
- **GitHub Projects** = Team/Project tasks (features, bugs, PRs, issues)
- **Claude Tasks** = Orchestrator personal tasks ONLY (reading docs, planning, reviewing)

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated with `project` scope
- GitHub Projects V2 enabled repository
- GraphQL API access
- Python 3.8+ for automation scripts
- AI Maestro integration for notifications (optional)

## Instructions

Follow these steps when using this skill:

1. **Identify the task type** - Determine if you need to create, update, query, or sync GitHub Projects data
2. **Authenticate** - Verify GitHub CLI is authenticated with `gh auth status` and has `project` scope
3. **Locate the project** - Find the project ID using GraphQL queries (see Quick Start section below)
4. **Select the appropriate operation** - Refer to the Reference Documentation section to find the matching use case
5. **Execute the operation** - Use GraphQL API via `gh api graphql` or run automation scripts
6. **Verify the result** - Check the project board or query the API to confirm the change was applied
7. **Notify stakeholders** - Send AI Maestro messages to relevant agents if coordination is needed
8. **Document the change** - Add comments to issues or update task lists to maintain audit trail

### Checklist

Copy this checklist and track your progress:

- [ ] Identify the task type (create/update/query/sync)
- [ ] Verify GitHub CLI authentication with `project` scope
- [ ] Locate the project using GraphQL queries
- [ ] Select the appropriate operation from reference documentation
- [ ] Execute the operation via GraphQL API or automation scripts
- [ ] Verify the result on the project board or via API query
- [ ] Notify stakeholders via AI Maestro if needed
- [ ] Document the change in issue comments or task lists

**When to invoke this skill:**
- Assigning GitHub issues to remote agents
- Tracking feature implementation progress
- Synchronizing PR status with project boards
- Managing sprint/iteration planning
- Generating project status reports
- Coordinating multi-agent work on features

## Output

| Output Type | Format | Location | Description |
|-------------|--------|----------|-------------|
| Project item IDs | JSON | API response | GraphQL node IDs for created/updated items |
| Status updates | JSON | API response | Confirmation of field value changes |
| Issue metadata | JSON | API response | Issue numbers, titles, states, assignees |
| Project reports | Markdown | AI Maestro messages | Status summaries, progress updates |
| Sync logs | Text/JSON | Script stdout | Automation script execution results |
| Error details | JSON/Text | stderr | API errors, validation failures, rate limits |
| Notification receipts | JSON | AI Maestro API | Confirmation of sent messages to agents |

## Iron Rules Compliance

This skill is **READ + STATUS UPDATE ONLY**:
- Query project state via GraphQL API
- Update card status (Todo -> In Progress -> Done)
- Add comments and labels to issues
- Link PRs to project items
- **NEVER**: Execute code, run tests, modify source files

## Quick Start

### Authentication

```bash
# Verify gh CLI is authenticated
gh auth status
```

### Find Your Project

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      projectsV2(first: 10) {
        nodes { id title number }
      }
    }
  }
'
```

## Reference Documentation

All detailed operations, templates, and scripts are organized in reference files below. Each section shows WHEN to read that reference and its contents.

---

### Core Operations ([references/core-operations.md](references/core-operations.md))

Read this when performing day-to-day GitHub Projects operations.

**Contents:**
- 1.1 When starting with GitHub Projects operations
- 1.2 When creating issues with project items
- 1.3 When updating project item status
- 1.4 When querying all project items
- 1.5 When linking PRs to issues
- 1.6 When adding comments to issues
- 1.7 When managing assignees

---

### GraphQL API Queries ([references/graphql-queries.md](references/graphql-queries.md))

Read this when you need complete GraphQL query/mutation syntax.

**Contents:**
- When listing projects
- When getting project items
- When updating item status
- When creating issues via GraphQL
- When working with custom fields
- Detailed Query References

**Sub-Files:**
- [graphql-queries-part1-read-operations.md](references/graphql-queries-part1-read-operations.md) - All read queries
- [graphql-queries-part2-mutations.md](references/graphql-queries-part2-mutations.md) - All mutations

---

### Status Management ([references/status-management.md](references/status-management.md))

Read this when managing issue/item status transitions.

**Contents:**
- 3.1 When starting with status management
- 3.2 When you need to understand status meanings and metadata
- 3.3 When moving issues between statuses (transition rules)
- 3.4 When syncing GitHub state with project board
- 3.5 When updating status via API or scripts
- 3.6 When generating status reports or summaries
- 3.7 When issues need attention or escalation
- 3.8 When deciding whether to close inactive issues (NO STALE policy)
- 3.9 When following status management best practices

**Standard Columns:** Backlog -> Todo -> In Progress -> AI Review -> Human Review -> Merge/Release -> Done (+ Blocked)

---

### Label Taxonomy ([references/label-taxonomy.md](references/label-taxonomy.md))

Read this when classifying or filtering issues by labels.

**Contents:**
- 4.1 When starting with the label system
- 4.2 When you need to know available label categories
- 4.3 When creating or managing labels via CLI
- 4.4 When applying labels automatically or manually
- 4.5 When searching or filtering issues by labels
- 4.6 When generating label statistics and counts
- 4.7 When following label usage best practices
- 4.8 When choosing label colors

**Label Categories:** type:*, priority:*, status:*, component:*, effort:*, agent:*, review:*

---

### Issue Templates ([references/issue-templates.md](references/issue-templates.md))

Read this when creating issues or setting up repository templates.

**Contents:**
- 5.1 When starting with issue templates
- 5.2 When setting up template file structure
- 5.3 When configuring template options
- 5.4 When creating feature request issues
- 5.5 When reporting bugs
- 5.6 When creating large multi-issue features (epics)
- 5.7 When proposing code refactoring
- 5.8 When requesting documentation improvements
- 5.9 When opening pull requests
- 5.10 When defining code ownership (CODEOWNERS)
- 5.11 When creating issues via GitHub CLI

---

### Sub-Issue Tracking ([references/sub-issue-tracking.md](references/sub-issue-tracking.md))

Read this when breaking down large features into smaller tasks.

**Contents:**
- 6.1 When breaking down large features into sub-issues
- 6.2 When creating parent/child issue relationships
- 6.3 When tracking progress across sub-issues
- 6.4 When automating progress updates
- 6.5 When using task lists for tracking
- 6.6 When querying sub-issue status

---

### Skill Integrations ([references/skill-integrations.md](references/skill-integrations.md))

Read this when coordinating GitHub Projects with other AMOA skills.

**Contents:**
- 7.1 When integrating GitHub Projects with other AMOA skills
- 7.2 When coordinating with Remote Agent Coordinator
- 7.3 When working with Code Reviewer skill
- 7.4 When generating reports
- 7.5 When using AI Maestro messaging
- 7.6 When syncing with Claude Tasks

---

### CI Notification Setup ([references/ci-notification-setup.md](references/ci-notification-setup.md))

Read this when configuring webhooks for CI/project sync.

**Contents:**
- 8.1 When understanding CI notification system
- 8.2 When configuring GitHub webhooks
- 8.3 When understanding event types and notifications
- 8.4 When customizing notification configuration
- 8.5 If webhook delivery or notification issues occur
- 8.6 When ensuring webhook security
- 8.7 When handling multiple repositories
- 8.8 When integrating CI events with project sync

---

### Error Handling ([references/error-handling.md](references/error-handling.md))

Read this when encountering API errors or failures.

**Contents:**
- 9.1 When encountering GitHub API errors
- 9.2 When hitting rate limits
- 9.3 When project or item is not found
- 9.4 When item updates fail
- 9.5 When authentication fails
- 9.6 When webhook delivery fails
- 9.7 When implementing retry logic

---

### Best Practices ([references/best-practices.md](references/best-practices.md))

Read this before starting work and when unsure about procedures.

**Contents:**
- 10.1 When following GitHub Projects best practices
- 10.2 When managing project board state (DO)
- 10.3 When handling issues and PRs (DO)
- 10.4 When avoiding common mistakes (DON'T)
- 10.5 When handling inactive issues (lifecycle reminders)
- 10.6 When documenting changes

---

### Automation Scripts ([references/automation-scripts.md](references/automation-scripts.md))

Read this when using the included Python automation scripts.

**Contents:**
- 11.1 When using skill automation scripts
- 11.2 When bulk creating issues from task lists (sync_tasks.py)
- 11.3 When receiving GitHub webhook events (ci_webhook_handler.py)
- 11.4 When synchronizing project with CI status (amia_kanban_sync.py)
- 11.5 When configuring shared thresholds

---

### GitHub Sync Procedure ([references/github-sync-procedure.md](references/github-sync-procedure.md))

Read this when synchronizing GitHub Projects state with external systems.

**Contents:**
- 1.1 Authenticating and verifying GitHub CLI access
- 1.2 Configuring GitHub Projects V2 environment variables
- 1.3 Fetching project board data via GraphQL API
- 1.4 Synchronizing GitHub issues to local task state
- 1.5 Synchronizing local changes back to GitHub
- 1.6 Managing GitHub issue labels across priority, status, and type dimensions
- 1.7 Syncing Project V2 custom fields bidirectionally
- 1.8 Integrating Claude Tasks with GitHub issue checklists
- 1.9 Handling sync errors and conflicts
- 1.10 Generating sync reports and logs
- 1.11 Troubleshooting API rate limits, label conflicts, and task parse errors

---

### Planning & Iteration ([references/planning-phase-mapping.md](references/planning-phase-mapping.md))

Read this when mapping planning phases to GitHub status.

**Contents:**
- When mapping planning phases to GitHub statuses
- When you need the phase-to-status mapping table
- When status should automatically transition
- When manually overriding automatic transitions
- When integrating with other automation
- When you need workflow examples

See also: [references/iteration-cycle-rules.md](references/iteration-cycle-rules.md) for sprint/iteration management.

**Contents (Iteration Cycle Rules):**
- When understanding iteration cycle requirements
- When determining if task is complete
- When following the review iteration flow
- When reviewing PRs for approval
- When tracking review iterations
- When updating the iteration counter
- If too many iterations occur
- If considering partial approval
- When waiting for next iteration
- When labeling PRs by iteration count

---

### Review & Plan Files

- [references/review-worktree-workflow.md](references/review-worktree-workflow.md) - Isolated review environment setup
- [references/plan-file-linking.md](references/plan-file-linking.md) - GitHub issue to plan file linking

---

## Issue Lifecycle Policy (NO STALE)

**IRON RULE**: Issues are NEVER automatically closed due to inactivity.

| Issue Type | Closure Conditions |
|------------|-------------------|
| Feature | Implemented + merged, OR explicitly declined with reason |
| Bug | Fixed + verified, OR 3 documented reproduction attempts failed |
| Chore | Completed and verified |

For inactive issues, use labels (`needs-attention`, `awaiting-response`, `low-priority`) instead of closing.

See [references/status-management.md](references/status-management.md#issue-lifecycle-policy-no-stale) for complete policy.

---

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

---

## Threshold Configuration

The `../shared/thresholds.py` module defines automation thresholds:

| Threshold | Value | Purpose |
|-----------|-------|---------|
| MAX_CONSECUTIVE_FAILURES | 3 | CI failures before escalation |
| INACTIVE_HOURS | 24 | Hours before flagging inactive items |
| LONG_REVIEW_HOURS | 48 | Hours before review escalation |
| BLOCKED_ESCALATION_HOURS | 72 | Hours before user escalation |

See [references/automation-scripts.md](references/automation-scripts.md#thresholds-configuration) for usage.

---

## Skill Files

```
github-projects-sync/
├── SKILL.md                          # This file (map/TOC)
├── scripts/
│   ├── sync_tasks.py                 # Bulk issue creation
│   ├── ci_webhook_handler.py         # Webhook receiver
│   └── amia_kanban_sync.py                # CI status sync
├── references/
│   ├── core-operations.md            # Day-to-day operations
│   ├── graphql-queries-index.md      # GraphQL library index
│   ├── graphql-queries-part1-*.md    # Read operations
│   ├── graphql-queries-part2-*.md    # Mutations
│   ├── status-management.md          # Status transitions & lifecycle
│   ├── label-taxonomy.md             # Label system
│   ├── issue-templates.md            # Issue/PR templates
│   ├── sub-issue-tracking.md         # Epic/sub-issue management
│   ├── skill-integrations.md         # AMOA skill integration
│   ├── ci-notification-setup.md      # Webhook configuration
│   ├── error-handling.md             # Error handling patterns
│   ├── best-practices.md             # Best practices guide
│   ├── automation-scripts.md         # Script documentation
│   ├── planning-phase-mapping.md     # Planning phase mapping
│   ├── iteration-cycle-rules.md      # Sprint/iteration rules
│   ├── review-worktree-workflow.md   # Review environment
│   └── plan-file-linking.md          # Plan file linking
└── ../shared/
    ├── thresholds.py                 # Automation thresholds
    └── aimaestro_notify.py           # AI Maestro CLI wrapper (TODO: not yet implemented)
```

---

## Examples and Inline Troubleshooting

For worked examples (finding/querying projects, updating issue status) and inline troubleshooting (project not found, issues not appearing, sync failures, rate limiting), see [references/examples-and-inline-troubleshooting.md](references/examples-and-inline-troubleshooting.md):

- E.1 Example 1: Find and Query a Project
- E.2 Example 2: Update Issue Status
- E.3 Inline Troubleshooting: Cannot find GitHub Project
- E.4 Inline Troubleshooting: Issue not appearing on project board
- E.5 Inline Troubleshooting: Column/status sync fails
- E.6 Inline Troubleshooting: Rate limiting from GitHub API
- E.7 Inline Troubleshooting: Claude Tasks and GitHub Project out of sync

For comprehensive error handling patterns, see also [references/error-handling.md](references/error-handling.md):

- When encountering GitHub API errors
- When hitting rate limits
- When project or item is not found
- When item updates fail
- When authentication fails
- When webhook delivery fails
- When implementing retry logic

## Error Handling

When GitHub API calls or sync operations fail, consult [references/error-handling.md](references/error-handling.md) for retry logic, rate-limit handling, and authentication troubleshooting. All errors should be logged and, if unresolvable after retries, escalated via AI Maestro.

**Contents:**
- When encountering GitHub API errors
- When hitting rate limits
- When project or item is not found
- When item updates fail
- When authentication fails
- When webhook delivery fails
- When implementing retry logic

---

## Examples

For worked examples of finding projects, querying items, and updating issue status, see [references/examples-and-inline-troubleshooting.md](references/examples-and-inline-troubleshooting.md). That reference also covers inline troubleshooting for common failures such as missing projects, sync conflicts, and rate limiting.

**Contents:**
- E.1 Example 1: Find and Query a Project
- E.2 Example 2: Update Issue Status
- E.3 Inline Troubleshooting: Cannot find GitHub Project
- E.4 Inline Troubleshooting: Issue not appearing on project board
- E.5 Inline Troubleshooting: Column/status sync fails
- E.6 Inline Troubleshooting: Rate limiting from GitHub API
- E.7 Inline Troubleshooting: Claude Tasks and GitHub Project out of sync

---

## Resources

- [references/core-operations.md](references/core-operations.md) - Day-to-day operations
- [references/graphql-queries.md](references/graphql-queries.md) - Complete GraphQL reference
- [references/status-management.md](references/status-management.md) - Status transition rules
- [references/label-taxonomy.md](references/label-taxonomy.md) - Label system reference
- [references/automation-scripts.md](references/automation-scripts.md) - Script documentation
- [references/error-handling.md](references/error-handling.md) - Error handling patterns
