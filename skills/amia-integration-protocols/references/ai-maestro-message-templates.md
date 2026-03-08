# AI Maestro Message Templates for AMIA

This document contains all AI Maestro messaging templates for Emasoft Integrator Agent (AMIA) communication patterns. For the exact messaging commands and syntax, always refer to the `agent-messaging` skill.

## Contents

- 1.0 Standard AI Maestro Messaging Approach
- 2.0 Receiving Messages from Orchestrator (AMOA)
  - 2.1 Integration Request from AMOA
  - 2.2 Handoff Document Rejection
- 3.0 Sending Messages to Sub-Agents
  - 3.1 Task Delegation to Sub-Agent
- 4.0 Reporting Results to Orchestrator (AMOA)
  - 4.1 Integration Status Report (Success)
  - 4.2 Integration Status Report (In Progress)
  - 4.3 Integration Status Report (Failed)
  - 4.4 Blocker Escalation (Critical Issues)
- 5.0 Quality Gate Communication
  - 5.1 PR Review Complete (All Gates Passed)
  - 5.2 PR Review Complete (Tests Failed)
  - 5.3 Merge Approved
  - 5.4 Merge Rejected
  - 5.5 Release Ready Notification

---

## 1.0 Standard AI Maestro Messaging Approach

All AI Maestro messages are sent using the `agent-messaging` skill. When sending a message, specify these fields:

| Field | Description |
|-------|-------------|
| **Recipient** | The target agent name |
| **Subject** | Brief description of the message purpose |
| **Content** | A JSON object with `type` and `message` fields |
| **Priority** | One of: `urgent`, `high`, `normal`, `low` |

To send a message, use the `agent-messaging` skill with the above fields. To verify delivery, check that the skill confirms the message was sent successfully.

---

## 2.0 Receiving Messages from Orchestrator (AMOA)

### 2.1 Integration Request from AMOA

**Scenario**: AMOA sends a PR review request, CI fix task, or integration verification task.

**To check for incoming messages:** Check your inbox using the `agent-messaging` skill. Filter for messages with `content.type == "integration-request"`.

**Expected Message Format from AMOA:**

```json
{
  "from": "orchestrator-amoa",
  "to": "ai-maestro-integrator",
  "subject": "Integration Request: <brief description>",
  "priority": "urgent|high|normal|low",
  "content": {
    "type": "integration-request",
    "request_type": "PR_REVIEW|CI_FIX|CODE_REVIEW|TESTING|RELEASE|ISSUE_CLOSURE",
    "context": {
      "pr_number": 456,
      "issue_number": 123,
      "branch": "feature/add-auth",
      "description": "Review authentication module PR",
      "error_logs": "path/to/logs.txt (if applicable)",
      "priority": "high"
    },
    "success_criteria": "All tests pass, code review approved, no security issues"
  }
}
```

### 2.2 Handoff Document Rejection

**Scenario**: Received handoff document fails validation (missing UUID, invalid references, TBD placeholders).

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `[HANDOFF REJECTED] Invalid handoff document`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "handoff-rejected",
    "message": "Handoff rejected. Issues: Missing UUID, file path invalid (src/auth.py does not exist), TBD placeholder in success criteria. Please correct and resubmit.",
    "validation_errors": [
      "Missing UUID",
      "File path invalid: src/auth.py",
      "TBD placeholder in success criteria"
    ]
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

---

## 3.0 Sending Messages to Sub-Agents

### 3.1 Task Delegation to Sub-Agent

**Scenario**: Routing a task (PR review, bug investigation, code review) to a specialized sub-agent.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: The appropriate sub-agent (e.g., `amia-code-reviewer`)
- **Subject**: `Review PR #456: Add auth module`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "task-delegation",
    "task": "review-pr",
    "context": {
      "pr_number": 456,
      "branch": "feature/add-auth",
      "files_affected": ["src/auth.py", "tests/test_auth.py"],
      "description": "New authentication module with JWT support",
      "focus_areas": ["security", "test coverage", "error handling"]
    },
    "success_criteria": "Code quality score > 8/10, no security vulnerabilities, test coverage > 90%",
    "priority": "high",
    "callback_agent": "ai-maestro-integrator"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Valid Sub-Agent Targets:**

- `amia-api-coordinator` - GitHub API operations
- `amia-code-reviewer` - Code quality assessment
- `amia-pr-evaluator` - PR readiness check
- `amia-integration-verifier` - Post-merge verification
- `amia-bug-investigator` - CI/test failures
- `amia-github-sync` - Repository state sync
- `amia-committer` - Creating commits
- `amia-screenshot-analyzer` - Visual verification
- `amia-debug-specialist` - Complex debugging
- `amia-test-engineer` - Test creation/analysis

---

## 4.0 Reporting Results to Orchestrator (AMOA)

### 4.1 Integration Status Report (Success)

**Scenario**: PR review completed successfully, all quality gates passed, ready to merge.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Integration Status: PR #456 - COMPLETED`
- **Priority**: `normal`
- **Content**:

  ```json
  {
    "type": "integration-status",
    "task_id": "pr-456-review",
    "status": "COMPLETED",
    "result": {
      "pr_number": 456,
      "quality_gates": ["code_review: PASS", "tests: PASS", "security: PASS"],
      "merge_status": "MERGED",
      "details_file": "docs_dev/integration/reports/pr-456-report.md"
    },
    "next_steps": "Issue #123 ready to close, all acceptance criteria met"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 4.2 Integration Status Report (In Progress)

**Scenario**: Integration task in progress, awaiting sub-agent completion.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Integration Status: PR #456 - IN PROGRESS`
- **Priority**: `normal`
- **Content**:

  ```json
  {
    "type": "integration-status",
    "task_id": "pr-456-review",
    "status": "IN_PROGRESS",
    "result": {
      "pr_number": 456,
      "current_phase": "code-review",
      "assigned_to": "amia-code-reviewer",
      "estimated_completion": "2026-02-05 16:00"
    },
    "next_steps": "Awaiting code review completion"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 4.3 Integration Status Report (Failed)

**Scenario**: Integration task failed due to quality gate failure or technical issue.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Integration Status: PR #456 - FAILED`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "integration-status",
    "task_id": "pr-456-review",
    "status": "FAILED",
    "result": {
      "pr_number": 456,
      "quality_gates": ["code_review: PASS", "tests: FAIL", "security: PASS"],
      "merge_status": "BLOCKED",
      "failure_reason": "Test coverage below 90% threshold (current: 78%)",
      "details_file": "docs_dev/integration/reports/pr-456-report.md"
    },
    "next_steps": "Request implementor add tests for uncovered code paths"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 4.4 Blocker Escalation (Critical Issues)

**Scenario**: Critical blocker prevents integration (security vulnerability, resource conflict, policy unclear).

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `[BLOCKER] PR #456 Security Issue`
- **Priority**: `urgent`
- **Content**:

  ```json
  {
    "type": "blocker-escalation",
    "task_id": "pr-456-review",
    "blocker_type": "QUALITY_GATE_FAILED",
    "details": {
      "description": "PR #456 has security vulnerability (SQL injection in auth.py:42)",
      "severity": "critical",
      "blocking_gate": "security-scan",
      "recommendation": "Reject PR, request fix from implementor"
    },
    "requires_decision": true
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Valid Blocker Types:**

- `QUALITY_GATE_FAILED` - Tests failed, coverage insufficient, security issue
- `RESOURCE_CONFLICT` - Multiple agents editing same file
- `POLICY_UNCLEAR` - Quality gate policy needs clarification
- `DEPENDENCY_MISSING` - Missing dependencies or external services

---

## 5.0 Quality Gate Communication

### 5.1 PR Review Complete (All Gates Passed)

**Scenario**: PR review finished, all quality gates passed, no issues found.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `PR Review Complete: PR #456 - ALL GATES PASSED`
- **Priority**: `normal`
- **Content**:

  ```json
  {
    "type": "integration-status",
    "task_id": "pr-456-review",
    "status": "COMPLETED",
    "result": {
      "pr_number": 456,
      "quality_gates": [
        "code_review: PASS (9.2/10)",
        "tests: PASS (93% coverage)",
        "security: PASS (0 issues)",
        "ci_pipeline: PASS"
      ],
      "merge_status": "APPROVED",
      "reviewer": "amia-code-reviewer",
      "details_file": "docs_dev/integration/reports/pr-456-report.md"
    },
    "next_steps": "Ready to merge, issue #123 can close after merge"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 5.2 PR Review Complete (Tests Failed)

**Scenario**: PR review found test failures or insufficient test coverage.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `PR Review Complete: PR #456 - TESTS FAILED`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "integration-status",
    "task_id": "pr-456-review",
    "status": "FAILED",
    "result": {
      "pr_number": 456,
      "quality_gates": [
        "code_review: PASS (8.5/10)",
        "tests: FAIL (78% coverage, threshold 90%)",
        "security: PASS (0 issues)",
        "ci_pipeline: FAIL (3 tests failing)"
      ],
      "merge_status": "BLOCKED",
      "failing_tests": [
        "test_auth.py::test_invalid_token",
        "test_auth.py::test_expired_token",
        "test_middleware.py::test_unauthorized_access"
      ],
      "details_file": "docs_dev/integration/reports/pr-456-report.md"
    },
    "next_steps": "Request implementor fix failing tests and add coverage for uncovered code paths"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 5.3 Merge Approved

**Scenario**: Quality gates passed, PR approved for merge into main branch.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Merge Approved: PR #456`
- **Priority**: `normal`
- **Content**:

  ```json
  {
    "type": "merge-decision",
    "decision": "APPROVED",
    "pr_number": 456,
    "branch": "feature/add-auth",
    "target_branch": "main",
    "rationale": "All quality gates passed: code quality 9.2/10, test coverage 93%, no security issues, CI green",
    "merged_by": "ai-maestro-integrator",
    "merge_commit": "abc123def456",
    "linked_issues": [123]
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 5.4 Merge Rejected

**Scenario**: Quality gates failed, PR rejected and cannot be merged.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Merge Rejected: PR #456`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "merge-decision",
    "decision": "REJECTED",
    "pr_number": 456,
    "branch": "feature/add-auth",
    "target_branch": "main",
    "rationale": "Critical security vulnerability detected: SQL injection in auth.py:42",
    "blocking_issues": [
      {
        "type": "security",
        "severity": "critical",
        "description": "SQL injection vulnerability",
        "location": "auth.py:42"
      }
    ],
    "required_actions": [
      "Fix SQL injection by using parameterized queries",
      "Re-run security scan",
      "Request re-review"
    ]
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### 5.5 Release Ready Notification

**Scenario**: All PRs merged, tests passed, release candidate ready for tagging.

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Release Ready: v1.2.0`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "release-ready",
    "version": "1.2.0",
    "release_branch": "release/1.2.0",
    "included_prs": [456, 457, 458],
    "closed_issues": [123, 124, 125],
    "quality_status": {
      "all_tests_passing": true,
      "security_scan": "PASS",
      "code_quality_avg": "9.1/10",
      "test_coverage": "94%"
    },
    "release_notes_file": "docs_dev/integration/release-notes-1.2.0.md",
    "next_steps": "Create git tag v1.2.0, push to main, create GitHub release"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

---

## Notes

- Always use `content.type` field to categorize message types for filtering
- Priority levels: `urgent` (critical blockers), `high` (failed gates), `normal` (status updates), `low` (informational)
- Always include `details_file` path for full reports (avoid verbose messages)
- Use `callback_agent` field when delegating to sub-agents to specify who should receive the response
- All file paths should be relative to project root or absolute paths
- Message content must be a JSON object with `type` and `message` fields, NOT a plain string
- For the exact commands to send and receive messages, refer to the `agent-messaging` skill
