# Record-Keeping for Integration Agent

## Contents

- 1. Routing Log Format
- 1. Integration Status Files
- 1. Quality Reports
- 1. Session State Structure

---

This reference describes the logging, tracking, and documentation formats used by the Integrator Agent to maintain records of all integration activities.


## 1. Routing Log Format

### Purpose

Track all routing decisions, delegations, and completions in chronological order.

### Location

`docs_dev/integration/routing-log.md`

### Format Structure

```markdown
# Integration Routing Log

## [YYYY-MM-DD]

### HH:MM - ROUTE request_type -> sub-agent
- **Request**: Brief description
- **Rationale**: Why this sub-agent was chosen
- **Priority**: critical/high/normal/low
- **Context**: PR #456, branch feature/add-auth
- **Status**: DELEGATED

### HH:MM - COMPLETE task-id
- **Sub-Agent**: amia-code-reviewer
- **Result**: SUCCESS/FAILURE
- **Details**: docs_dev/integration/reports/pr-456-report.md
```

### Example Entry

```markdown
## 2026-02-04

### 14:32 - ROUTE PR_REVIEW -> amia-code-reviewer
- **Request**: Review PR #456 (Add auth module)
- **Rationale**: Structural changes to auth system, requires expert review
- **Priority**: high
- **Context**: PR #456, branch feature/add-auth, 3 files changed
- **Status**: DELEGATED

### 15:18 - COMPLETE pr-456-review
- **Sub-Agent**: amia-code-reviewer
- **Result**: SUCCESS
- **Details**: docs_dev/integration/reports/pr-456-report.md
- **Quality Gates**: All passed
- **Merge Status**: Approved for merge
```

### Entry Types

| Entry Type | When to Log |
|------------|-------------|
| `ROUTE` | When delegating to a sub-agent |
| `COMPLETE` | When sub-agent task completes |
| `ESCALATE` | When escalating to orchestrator |
| `GATE_CHECK` | When running quality gates |

---

## 2. Integration Status Files

### Purpose

Track the full lifecycle of an integration task from creation to completion.

### Location

`docs_dev/integration/status/[pr-number].md` or `docs_dev/integration/status/[task-id].md`

### Format Structure

```markdown
# Integration Status: [Task Name]

**Task ID**: pr-456-review
**Type**: PR_REVIEW
**Created**: 2026-02-04 14:32
**Updated**: 2026-02-04 15:18
**Status**: COMPLETED

## Request Details
- **PR Number**: #456
- **Branch**: feature/add-auth
- **Requestor**: orchestrator-amoa
- **Priority**: high

## Routing
- **Sub-Agent**: amia-code-reviewer
- **Delegated**: 2026-02-04 14:32
- **Completed**: 2026-02-04 15:18
- **Duration**: 46 minutes

## Quality Gates
- [x] Code Review - PASS
- [x] Test Coverage - PASS (93%)
- [x] Security Scan - PASS
- [x] CI Pipeline - PASS

## Result
- **Merge Status**: APPROVED
- **Details**: docs_dev/integration/reports/pr-456-report.md
- **Next Steps**: Ready to merge, issue #123 can be closed after merge
```

### Status Values

| Status | Meaning |
|--------|---------|
| `PENDING` | Awaiting delegation |
| `IN_PROGRESS` | Sub-agent working |
| `COMPLETED` | Task finished successfully |
| `FAILED` | Task failed |
| `ESCALATED` | Sent to orchestrator |

### Task Types

| Type | Description |
|------|-------------|
| `PR_REVIEW` | Pull request review |
| `MERGE_APPROVAL` | Merge authorization |
| `QUALITY_CHECK` | Quality gate verification |
| `ISSUE_TRACKING` | GitHub issue management |
| `DEPLOY_VALIDATION` | Deployment verification |

---

## 3. Quality Reports

### Purpose

Document detailed findings from code reviews, quality checks, and integration validations.

### Location

`docs_dev/integration/reports/pr-[number]-report.md` or `docs_dev/integration/reports/[task-id]-report.md`

### Format Structure

```markdown
# Code Review Report: PR #456

**Reviewer**: amia-code-reviewer
**Date**: 2026-02-04 15:18
**PR**: #456 - Add authentication module
**Branch**: feature/add-auth

## Summary
New JWT-based authentication module with role-based access control.

## Files Reviewed
- `src/auth.py` (new, 234 lines)
- `src/middleware.py` (modified, +45 lines)
- `tests/test_auth.py` (new, 156 lines)

## Quality Metrics
- **Code Quality Score**: 9.2/10
- **Test Coverage**: 93%
- **Complexity**: 6.2 (acceptable)
- **Security Issues**: 0 critical, 0 high, 1 low

## Findings

### Strengths
- Clear separation of concerns
- Comprehensive test coverage
- Good error handling
- Proper input validation

### Issues
- **Low**: Token expiry could be configurable (hardcoded 1 hour)

### Recommendations
- Consider making token expiry a config parameter
- Add integration tests with actual HTTP requests

## Verdict
**APPROVED** - Ready to merge after addressing low-priority issue (can be follow-up PR)
```

### Verdict Values

| Verdict | Meaning | Action |
|---------|---------|--------|
| `APPROVED` | Ready to merge | Proceed with merge |
| `APPROVED_WITH_COMMENTS` | Minor issues, can merge | Merge, create follow-up issue |
| `CHANGES_REQUESTED` | Must fix issues | Block merge, request changes |
| `REJECTED` | Fundamental problems | Block merge, major rework needed |

### Quality Metrics

All reports should include these standard metrics:

- **Code Quality Score**: 0-10 (linting, style, patterns)
- **Test Coverage**: Percentage (with branch coverage if available)
- **Complexity**: Cyclomatic complexity score
- **Security Issues**: Count by severity (critical/high/medium/low)
- **Performance Impact**: If relevant
- **Documentation**: Coverage and quality

---

## 4. Session State Structure

### Purpose

Maintain the current state of the integration session for context and continuity.

### Location

In-memory during session, saved to `docs_dev/integration/session-state.json`

### JSON Structure

```json
{
  "session_id": "integration-2026-02-04-143210",
  "started": "2026-02-04T14:32:10Z",
  "last_updated": "2026-02-04T15:18:45Z",
  "active_tasks": [
    {
      "task_id": "pr-456-review",
      "type": "PR_REVIEW",
      "sub_agent": "amia-code-reviewer",
      "status": "IN_PROGRESS",
      "started": "2026-02-04T14:32:15Z"
    }
  ],
  "completed_tasks": [
    {
      "task_id": "pr-455-review",
      "type": "PR_REVIEW",
      "sub_agent": "amia-code-reviewer",
      "status": "COMPLETED",
      "result": "APPROVED",
      "duration_minutes": 23
    }
  ],
  "quality_gates": {
    "pr-456": {
      "code_review": "PENDING",
      "test_coverage": "PENDING",
      "security_scan": "PENDING",
      "ci_pipeline": "PENDING"
    }
  },
  "github_context": {
    "repository": "owner/repo",
    "current_branch": "feature/add-auth",
    "open_prs": 3,
    "pending_reviews": 1
  }
}
```

### State Fields

| Field | Type | Purpose |
|-------|------|---------|
| `session_id` | string | Unique identifier for this integration session |
| `started` | ISO 8601 timestamp | When session began |
| `last_updated` | ISO 8601 timestamp | Last state modification |
| `active_tasks` | array | Tasks currently being processed |
| `completed_tasks` | array | Recently completed tasks (last 24h) |
| `quality_gates` | object | Current status of all quality checks |
| `github_context` | object | Repository state and metadata |

### Task State Object

Each task (active or completed) contains:

```json
{
  "task_id": "unique-identifier",
  "type": "PR_REVIEW|MERGE_APPROVAL|QUALITY_CHECK|...",
  "sub_agent": "amia-code-reviewer|amia-github-manager|...",
  "status": "PENDING|IN_PROGRESS|COMPLETED|FAILED|ESCALATED",
  "started": "ISO 8601 timestamp",
  "completed": "ISO 8601 timestamp (if done)",
  "result": "SUCCESS|FAILURE|APPROVED|REJECTED|...",
  "duration_minutes": 23,
  "context": {
    "pr_number": 456,
    "branch": "feature/add-auth",
    "priority": "high"
  }
}
```

---

## Best Practices

### 1. Update Immediately

- Log routing decisions as they happen
- Update status files when state changes
- Don't batch updates

### 2. Be Consistent

- Use standard formats for all entries
- Follow naming conventions for files
- Use ISO 8601 for all timestamps

### 3. Include Context

- Reference PR numbers, issue numbers, branches
- Link to detailed reports
- Provide rationale for decisions

### 4. Track Duration

- Record start and end times
- Calculate and log duration
- Use for performance monitoring

### 5. Link Documents

- Status files reference reports
- Reports reference PRs/issues
- Routing log references both

---

## File Organization

```
docs_dev/integration/
├── routing-log.md              # Main chronological log
├── session-state.json          # Current session state
├── status/                     # Task status tracking
│   ├── pr-456.md
│   ├── pr-457.md
│   └── task-deploy-staging.md
└── reports/                    # Detailed findings
    ├── pr-456-report.md
    ├── pr-457-report.md
    └── deploy-staging-report.md
```

---

## When to Create Each Document

| Document Type | When to Create | When to Update |
|---------------|----------------|----------------|
| **Routing Log** | Start of session | Every routing/completion |
| **Status File** | When task delegated | Status changes, completion |
| **Quality Report** | When review completes | Never (immutable record) |
| **Session State** | Start of session | Every state change |

---

## Error Handling

If record-keeping fails:

1. **Log to routing-log.md**: Always priority #1
2. **Session state**: Can be reconstructed from routing log
3. **Status files**: Can be regenerated from sub-agent outputs
4. **Reports**: Sub-agents must always produce these

**Never block integration work due to logging failures** - escalate to orchestrator if persistent.
