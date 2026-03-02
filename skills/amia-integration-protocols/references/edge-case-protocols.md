# Edge Case Protocols for Integrator Agent

This document defines standardized protocols for handling edge cases and failure scenarios in the Integrator Agent (amia-) plugin.

## Table of Contents

- 1.0 AI Maestro Unavailable
  - 1.1 Detection Methods
  - 1.2 Response Workflow
  - 1.3 Fallback Reporting
- 2.0 GitHub Unavailable
  - 2.1 Detection Methods
  - 2.2 Response Workflow
  - 2.3 PR Operation Queueing
  - 2.4 Issue Operation Queueing
- 3.0 Remote Agent Timeout
  - 3.1 Detection Methods
  - 3.2 Escalation Ladder
  - 3.3 Review Handoff Protocol
- 4.0 PR Check Failures
  - 4.1 CI Pipeline Failures
  - 4.2 Test Failures
  - 4.3 Linting/Formatting Failures
  - 4.4 Security Scan Failures
- 5.0 Merge Conflicts
  - 5.1 Detection Methods
  - 5.2 Conflict Resolution Protocol
  - 5.3 Escalation to Orchestrator
- 6.0 Branch Protection Violations
  - 6.1 Direct Push Attempts
  - 6.2 Insufficient Reviews
  - 6.3 Failed Required Checks
- 7.0 Issue Closure Gate Failures
  - 7.1 Missing PR Link
  - 7.2 Incomplete Checklist
  - 7.3 Missing Test Evidence

---

## 1.0 AI Maestro Unavailable

### 1.1 Detection Methods

The Integrator uses AI Maestro to communicate with Orchestrator and Assistant Manager. Detect unavailability through:

| Check | Method | Failure Indicator |
|-------|--------|-------------------|
| API Health | Use the `agent-messaging` skill to check service health | HTTP 503/504 or timeout |
| Connection Test | Use the `agent-messaging` skill to check inbox (with 10s timeout) | Connection timeout after 10 seconds |
| Agent Registry | Use the `agent-messaging` skill to list known agents | Registry unreachable or empty response |

### 1.2 Response Workflow

When AI Maestro is unavailable:

1. **Log the failure**:
   > **Note**: The log entry below records service unavailability for diagnostics. The `agent-messaging` skill handles all messaging; AMP handles routing automatically.
   ```bash
   echo "$(date -Iseconds) | AIMAESTRO_UNAVAILABLE | AMP_SERVICE | HTTP $STATUS_CODE" >> .claude/logs/maestro-failures.log
   ```

2. **Queue outgoing messages**:
   > **Note**: This offline fallback is ONLY for when AI Maestro is completely unreachable. Under normal conditions, always use the `agent-messaging` skill to send messages.

   ```bash
   mkdir -p .claude/queue/outbox
   cat > ".claude/queue/outbox/${RECIPIENT_AGENT}-$(date +%s).json" <<EOF
   {
     "to": "${RECIPIENT_AGENT}",
     "subject": "${SUBJECT}",
     "priority": "${PRIORITY}",
     "content": {"type": "${TYPE}", "message": "${MESSAGE}"},
     "queued_at": "$(date -Iseconds)"
   }
   EOF
   ```

3. **Display warning**:
   ```
   WARNING: AI Maestro is unavailable. Cannot notify Orchestrator/Assistant Manager.
   Queued: N messages
   Review results will be stored locally and sent when service recovers.
   ```

4. **Use fallback reporting** (see section 1.3)

5. **Retry every 5 minutes**
   - After 30 minutes, require user intervention

### 1.3 Fallback Reporting

When AI Maestro is down, report via:

| Priority | Method | Use Case |
|----------|--------|----------|
| 1st | GitHub PR comments | Code review results |
| 2nd | GitHub Issue comments | Status updates |
| 3rd | Local handoff files | Detailed review reports |

**PR Comment Fallback Template**:
```markdown
## Integrator Review (AI Maestro Offline)

**Status**: [APPROVED/CHANGES_REQUESTED/BLOCKED]
**Reviewed by**: amia-code-reviewer

### Summary
[Review summary]

### Next Steps
[Required actions]

---
*Note: AI Maestro unavailable. Full report stored in `.claude/reviews/`*
```

---

## 2.0 GitHub Unavailable

### 2.1 Detection Methods

| Check | Command | Failure Indicator |
|-------|---------|-------------------|
| API Status | `gh api rate_limit` | HTTP 5xx errors |
| Network | `gh pr list --limit 1` | Network failure |
| Rate Limit | `gh api rate_limit --jq '.rate.remaining'` | Returns 0 (403 error) |

### 2.2 Response Workflow

1. **Cache last known state**:
   ```bash
   mkdir -p .claude/cache/github
   gh pr list --json number,title,state,mergeable > .claude/cache/github/prs.json
   gh issue list --json number,title,state,labels > .claude/cache/github/issues.json
   echo "$(date -Iseconds)" > .claude/cache/github/cached_at
   ```

2. **Queue all GitHub operations** (see 2.3, 2.4)

3. **Notify user**:
   ```
   WARNING: GitHub is unavailable.
   - Cached state from: [timestamp]
   - Queued PR operations: N
   - Queued Issue operations: M
   - Code reviews paused until GitHub recovers.
   - Will retry every 10 minutes.
   ```

4. **Continue with local operations**:
   - Local code analysis
   - Generate review comments (queue for posting)
   - Run local tests

5. **Retry every 10 minutes**

### 2.3 PR Operation Queueing

Queue PR operations when GitHub is unavailable:

```bash
mkdir -p .claude/queue/github/pr
cat > ".claude/queue/github/pr/op-$(date +%s).json" <<EOF
{
  "operation": "pr_review",
  "pr_number": 123,
  "action": "approve|request_changes|comment",
  "body": "Review content...",
  "queued_at": "$(date -Iseconds)"
}
EOF
```

### 2.4 Issue Operation Queueing

Queue Issue operations when GitHub is unavailable:

```bash
mkdir -p .claude/queue/github/issue
cat > ".claude/queue/github/issue/op-$(date +%s).json" <<EOF
{
  "operation": "issue_close|issue_comment|label_add",
  "issue_number": 456,
  "params": {...},
  "queued_at": "$(date -Iseconds)"
}
EOF
```

---

## 3.0 Remote Agent Unresponsive

### 3.1 Detection Methods

AI agents collaborate asynchronously and may be hibernated for extended periods. Detection is based on **state**, not elapsed time.

| State | Detection | Priority |
|-------|-----------|----------|
| No ACK | Code reviewer has not acknowledged review request | Normal |
| No Progress | Reviewer acknowledged but no partial results posted | Normal |
| Stale | Reviewer's last update predates PR changes | High |
| Unresponsive | Multiple reminders sent without any response | Urgent |
| Offline | AI Maestro reports agent session terminated | Immediate |

### 3.2 Escalation Order

**Step 1: First Reminder (when state = No ACK or No Progress)**

Send a message using the `agent-messaging` skill with:
- **Recipient**: The assigned reviewer agent
- **Subject**: `Review Check: PR #<PR_NUMBER>`
- **Priority**: `high`
- **Content**: `{"type": "status_request", "message": "Please provide status update for PR #<PR_NUMBER> review."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Step 2: Urgent Reminder (when state = Unresponsive after Step 1)**
- Send urgent priority message using the `agent-messaging` skill
- Note: "Review may be reassigned if no response"
- **Verify**: Confirm message delivery via the `agent-messaging` skill's sent messages feature.

**Step 3: Reassign or escalate to Orchestrator**

### 3.3 Review Handoff Protocol

When handing off a review to another reviewer:

1. **Document current state**:
   ```json
   {
     "pr_number": 123,
     "original_reviewer": "amia-code-reviewer",
     "partial_review": {
       "files_reviewed": ["src/main.py", "src/utils.py"],
       "files_pending": ["tests/test_main.py"],
       "comments_drafted": [...]
     },
     "handoff_reason": "timeout_no_response"
   }
   ```

2. **Transfer to new reviewer** with full context

3. **Notify Orchestrator** of delay

---

## 4.0 PR Check Failures

### 4.1 CI Pipeline Failures

**Detection**: `gh pr checks --json state | jq '.[] | select(.state == "FAILURE")'`

**Response Workflow**:

1. **Identify failure type**:
   | Failure | Action |
   |---------|--------|
   | Build failure | Route to Orchestrator for code fix |
   | Infrastructure failure | Retry after 5 minutes |
   | Timeout | Retry with increased timeout request |

2. **Log failure details**:
   ```bash
   gh run view $RUN_ID --log-failed > .claude/logs/ci-failure-$RUN_ID.log
   ```

3. **Create actionable report**:
   ```markdown
   ## CI Pipeline Failure

   **PR**: #123
   **Run ID**: 456789
   **Failure Type**: build_failure

   ### Error Summary
   [Extracted error messages]

   ### Suggested Fix
   [Analysis of fix needed]

   ### Files Affected
   - src/module.py:42 - Syntax error
   ```

4. **Route to Orchestrator** for fix assignment

### 4.2 Test Failures

**Detection**: Test step in CI fails.

**Response Workflow**:

1. **Extract failing tests**:
   ```bash
   gh run view $RUN_ID --log | grep -E "FAILED|ERROR" > .claude/logs/test-failures-$RUN_ID.log
   ```

2. **Categorize failures**:
   | Type | Action |
   |------|--------|
   | Unit test failure | Request code fix from Orchestrator |
   | Integration test failure | Investigate environment issues |
   | Flaky test | Re-run, document if persists |

3. **Block PR merge** until tests pass

4. **Post failure summary as PR comment**

### 4.3 Linting/Formatting Failures

**Detection**: Lint/format check fails.

**Response Workflow**:

1. **Identify violations**:
   ```bash
   # Python
   ruff check src/ --output-format=json > .claude/logs/lint-violations.json

   # JavaScript/TypeScript
   eslint src/ --format json > .claude/logs/lint-violations.json
   ```

2. **Check if auto-fixable**:
   - If yes: Suggest fix command
   - If no: Create detailed violation report

3. **Post comment with fix instructions**:
   ```markdown
   ## Linting Failures

   Found 5 violations (3 auto-fixable).

   ### Auto-fix command
   ```bash
   ruff check src/ --fix
   ```

   ### Manual fixes required
   - src/module.py:42 - Line too long (needs manual refactor)
   ```

### 4.4 Security Scan Failures

**Detection**: Security scanner reports vulnerabilities.

**Response Workflow**:

1. **Severity triage**:
   | Severity | Action |
   |----------|--------|
   | Critical | Block PR, immediate escalation |
   | High | Block PR, route to Orchestrator |
   | Medium | Warning, request fix before merge |
   | Low | Advisory comment, allow merge |

2. **Create security report**:
   ```markdown
   ## Security Scan Results

   **Status**: BLOCKED
   **Critical Issues**: 1
   **High Issues**: 2

   ### Critical: SQL Injection (CVE-XXXX)
   - File: src/db.py:87
   - Description: Unsanitized user input in query
   - Remediation: Use parameterized queries

   ### Required Actions
   1. Fix critical issues before merge
   2. Acknowledge high issues with mitigation plan
   ```

3. **Route to Orchestrator with URGENT priority**

---

## 5.0 Merge Conflicts

### 5.1 Detection Methods

```bash
# Check if PR has conflicts
gh pr view $PR_NUMBER --json mergeable | jq '.mergeable'
# Returns: "CONFLICTING" if conflicts exist
```

### 5.2 Conflict Resolution Protocol

1. **Identify conflicting files**:
   ```bash
   gh pr view $PR_NUMBER --json files | jq '.files[].path'
   ```

2. **Assess conflict complexity**:
   | Complexity | Criteria | Action |
   |------------|----------|--------|
   | Simple | <3 files, same author | Auto-resolve if possible |
   | Medium | 3-10 files, clear ownership | Route to original author |
   | Complex | >10 files, multiple authors | Escalate to Orchestrator |

3. **For simple conflicts, suggest resolution**:
   ```markdown
   ## Merge Conflict Detected

   **Files**: 2 files have conflicts
   - src/config.py
   - tests/test_config.py

   ### Suggested Resolution
   ```bash
   git fetch origin main
   git checkout feature-branch
   git merge origin/main
   # Resolve conflicts in editor
   git add .
   git commit -m "Resolve merge conflicts"
   git push
   ```
   ```

### 5.3 Escalation to Orchestrator

For complex conflicts:

```json
{
  "type": "conflict_escalation",
  "pr_number": 123,
  "conflicting_files": ["..."],
  "affected_modules": ["auth", "users"],
  "suggested_owners": ["agent-1", "agent-2"],
  "urgency": "high"
}
```

---

## 6.0 Branch Protection Violations

### 6.1 Direct Push Attempts

**Detection**: Hook intercepts push to protected branch.

**Response**:

1. **Block the operation**:
   ```json
   {
     "decision": "block",
     "reason": "Direct push to main/master is prohibited. Create a PR instead."
   }
   ```

2. **Provide alternative**:
   ```
   BLOCKED: Cannot push directly to main.

   To contribute changes:
   1. Create a feature branch: git checkout -b feature/my-change
   2. Push the branch: git push origin feature/my-change
   3. Create a PR: gh pr create
   ```

3. **Log the violation** for audit

### 6.2 Insufficient Reviews

**Detection**: PR attempts merge without required reviews.

**Response**:

1. **Block merge**:
   ```
   BLOCKED: PR requires 1 approving review before merge.

   Current status:
   - Approvals: 0/1 required
   - Requested reviewers: amia-code-reviewer

   Waiting for review completion.
   ```

2. **Send reminder to reviewers**

### 6.3 Failed Required Checks

**Detection**: PR attempts merge with failing checks.

**Response**:

1. **Block merge**:
   ```
   BLOCKED: Required checks have not passed.

   Failed checks:
   - CI / build (failure)
   - CI / test (failure)

   See section 4.0 for failure handling protocols.
   ```

2. **Route failures for resolution**

---

## 7.0 Issue Closure Gate Failures

### 7.1 Missing PR Link

**Detection**: Issue close attempted without linked PR.

**Response**:

1. **Block closure**:
   ```
   BLOCKED: Cannot close issue #456 - No linked PR.

   Issue closure requires:
   - [x] Issue has work completed
   - [ ] PR linked that addresses the issue
   - [ ] PR is merged

   Please link a PR before closing.
   ```

2. **Suggest linking**:
   ```
   To link a PR to this issue:
   - In PR description: "Closes #456" or "Fixes #456"
   - Or manually: gh issue develop 456 --base main
   ```

### 7.2 Incomplete Checklist

**Detection**: Issue checklist not fully checked.

**Response**:

1. **Block closure**:
   ```
   BLOCKED: Cannot close issue #456 - Checklist incomplete.

   Checklist status:
   - [x] Implementation complete
   - [ ] Tests written
   - [ ] Documentation updated

   Please complete all checklist items before closing.
   ```

2. **Route incomplete items to Orchestrator** if user requests

### 7.3 Missing Test Evidence

**Detection**: No test evidence in PR or issue.

**Response**:

1. **Block closure**:
   ```
   BLOCKED: Cannot close issue #456 - No test evidence.

   TDD Compliance requires:
   - Test files added/modified in PR
   - OR Test execution results posted
   - OR Explicit waiver with justification

   Please add test evidence or request a waiver.
   ```

2. **Provide test template**:
   ```python
   # Required test for issue #456
   def test_feature_described_in_issue_456():
       """Test that [feature] works as specified."""
       # Arrange
       ...
       # Act
       ...
       # Assert
       assert result == expected
   ```

---

## Emergency Recovery

If multiple edge cases compound:

1. **Stop all merge/close operations**
2. **Save complete state**:
   - PR review states
   - Issue states
   - Queue contents
3. **Create recovery checkpoint**
4. **Notify Orchestrator and User**
5. **Wait for guidance**

Recovery checkpoint: `.claude/recovery/integrator-checkpoint-{timestamp}.json`

---

## Related Documents

- [ci-status-interpretation.md](../../amia-github-pr-checks/references/ci-status-interpretation.md) - CI status handling
- [merge-strategies.md](../../amia-github-pr-merge/references/merge-strategies.md) - Merge options
- [troubleshooting.md](../../amia-github-integration/references/troubleshooting.md) - GitHub troubleshooting
- [blocking-workflow.md](../../amia-kanban-orchestration/references/blocking-workflow.md) - Blocking patterns
