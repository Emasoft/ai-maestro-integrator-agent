# Handoff Templates

This document contains all templates used for agent handoff protocols.

## Table of Contents

- [Task Delegation](#task-delegation)
- [Acknowledgment](#acknowledgment)
- [Completion Report](#completion-report)
- [Blocker Report](#blocker-report)

---

## Task Delegation

Template for delegating tasks from orchestrator to remote agents.

### Format

```markdown
# Task Delegation: {{TASK_ID}}

## Summary

**Task ID**: {{TASK_ID}}
**Assigned To**: {{AGENT_SESSION}}
**Priority**: {{PRIORITY}}
**Deadline**: {{DEADLINE}}
**GitHub Issue**: {{ISSUE_URL}}

## Description

{{TASK_DESCRIPTION}}

## Requirements

1. {{REQUIREMENT_1}}
2. {{REQUIREMENT_2}}
3. {{REQUIREMENT_3}}

## Acceptance Criteria

- [ ] {{CRITERIA_1}}
- [ ] {{CRITERIA_2}}
- [ ] {{CRITERIA_3}}

## Resources

- {{RESOURCE_1}}
- {{RESOURCE_2}}

## Expected Output

{{OUTPUT_DESCRIPTION}}

## Notes

{{ADDITIONAL_NOTES}}

---
**Delegated By**: {{ORCHESTRATOR_SESSION}}
**Delegated At**: {{TIMESTAMP}}
```

### Variables

| Variable | Description |
|----------|-------------|
| `{{TASK_ID}}` | Unique task identifier (e.g., `TASK-001`) |
| `{{AGENT_SESSION}}` | Target agent's session name |
| `{{PRIORITY}}` | Task priority: `urgent`, `high`, `normal`, `low` |
| `{{DEADLINE}}` | Expected completion time |
| `{{ISSUE_URL}}` | GitHub issue URL for tracking |
| `{{TASK_DESCRIPTION}}` | Detailed task description |
| `{{ORCHESTRATOR_SESSION}}` | Orchestrator's session name |
| `{{TIMESTAMP}}` | ISO 8601 timestamp |

---

## Acknowledgment

Template for remote agents to acknowledge task receipt.

### Format

```
[ACK] {{TASK_ID}} - {{STATUS}}
Understanding: {{ONE_LINE_SUMMARY}}
ETA: {{ESTIMATED_COMPLETION}}
```

### Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `RECEIVED` | Task received, starting work immediately | None, proceed with task |
| `CLARIFICATION_NEEDED` | Need more information | Orchestrator provides details |
| `REJECTED` | Cannot accept task | Orchestrator reassigns |
| `QUEUED` | Have prior tasks, will start later | Wait or reassign |

### Examples

**Successful ACK**:
```
[ACK] TASK-001 - RECEIVED
Understanding: Implement user authentication with JWT tokens
ETA: 2 hours
```

**Clarification Needed**:
```
[ACK] TASK-001 - CLARIFICATION_NEEDED
Understanding: Implement authentication, but unclear on token expiry requirements
Questions:
1. What should be the JWT expiration time?
2. Should we implement refresh tokens?
```

**Rejection**:
```
[ACK] TASK-001 - REJECTED
Understanding: Database migration task
Reason: No database access credentials available
Suggested: Route to agent with database permissions
```

---

## Completion Report

Template for reporting task completion.

### Format

```markdown
# Completion Report: {{TASK_ID}}

## Status

**Task ID**: {{TASK_ID}}
**Status**: COMPLETED
**Completed By**: {{AGENT_SESSION}}
**Completed At**: {{TIMESTAMP}}

## Summary

{{COMPLETION_SUMMARY}}

## Work Done

1. {{WORK_ITEM_1}}
2. {{WORK_ITEM_2}}
3. {{WORK_ITEM_3}}

## Acceptance Criteria Status

- [x] {{CRITERIA_1}}
- [x] {{CRITERIA_2}}
- [x] {{CRITERIA_3}}

## Deliverables

| Deliverable | Location |
|-------------|----------|
| {{DELIVERABLE_1}} | {{PATH_OR_URL_1}} |
| {{DELIVERABLE_2}} | {{PATH_OR_URL_2}} |

## Testing

{{TESTING_SUMMARY}}

## Notes

{{ADDITIONAL_NOTES}}

---
**Awaiting Sign-off From**: {{ORCHESTRATOR_SESSION}}
```

### Required Fields

- **Task ID**: Must match the original delegation
- **Status**: One of `COMPLETED`, `PARTIAL`, `BLOCKED`
- **Summary**: 1-2 sentence summary of what was accomplished
- **Acceptance Criteria Status**: All criteria must be checked for `COMPLETED` status

---

## Blocker Report

Template for reporting blockers that prevent task completion.

### Format

```markdown
# Blocker Report: {{TASK_ID}}

## Status

**Task ID**: {{TASK_ID}}
**Status**: BLOCKED
**Reported By**: {{AGENT_SESSION}}
**Reported At**: {{TIMESTAMP}}
**Severity**: {{SEVERITY}}

## Blocker Description

{{BLOCKER_DESCRIPTION}}

## Category

{{BLOCKER_CATEGORY}}

## Impact

- **Progress Made**: {{PERCENTAGE}}%
- **Work Completed**: {{COMPLETED_WORK}}
- **Work Remaining**: {{REMAINING_WORK}}

## Attempted Solutions

1. {{ATTEMPT_1}}
   - Result: {{RESULT_1}}
2. {{ATTEMPT_2}}
   - Result: {{RESULT_2}}

## Required Resolution

{{RESOLUTION_NEEDED}}

## Suggested Actions

1. {{SUGGESTION_1}}
2. {{SUGGESTION_2}}

---
**Requires Urgent Attention**: {{YES_NO}}
**Blocking Other Tasks**: {{BLOCKED_TASKS}}
```

### Blocker Categories

| Category | Description | Typical Resolution |
|----------|-------------|-------------------|
| `missing_dependency` | Required package/resource unavailable | Orchestrator provides or installs |
| `auth_failure` | Cannot access required resource | Orchestrator provides credentials |
| `spec_ambiguity` | Requirements unclear | Orchestrator clarifies |
| `technical_block` | API limit, rate limiting, etc. | Wait or workaround |
| `conflict` | Merge conflict, resource contention | Orchestrator coordinates |
| `external_service` | Third-party service unavailable | Wait or alternative |

### Severity Levels

| Severity | Meaning | Response Time |
|----------|---------|---------------|
| `critical` | Cannot proceed at all | Immediate |
| `high` | Major functionality blocked | Within 1 hour |
| `medium` | Partial functionality blocked | Within 4 hours |
| `low` | Minor inconvenience | Next business day |

---

**Version**: 1.0.0
**Last Updated**: 2026-02-03
