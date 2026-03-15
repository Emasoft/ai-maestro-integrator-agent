# AMIA Sub-Agent Routing and Delegation Checklist

## Contents

- [Sub-Agent Routing Table](#sub-agent-routing-table)
- [Routing Decision Guidelines](#routing-decision-guidelines)
  - [Route to code-reviewer when:](#route-to-code-reviewer-when)
  - [Route to bug-investigator when:](#route-to-bug-investigator-when)
  - [Handle PR directly when:](#handle-pr-directly-when)
  - [Spawn verifier when:](#spawn-verifier-when)
  - [Escalate to orchestrator when:](#escalate-to-orchestrator-when)
- [Priority Triage](#priority-triage)
- [Success Criteria Checklist](#success-criteria-checklist)
  - [Integration Request Received](#integration-request-received)
  - [Routing Decision Made](#routing-decision-made)
  - [Sub-Agent Completed](#sub-agent-completed)
  - [Quality Verified](#quality-verified)
- [Routing Decision Checklist](#routing-decision-checklist)
  - [Step 1: Identify Request Type](#step-1-identify-request-type)
  - [Step 2: Check Request Completeness](#step-2-check-request-completeness)
  - [Step 3: Select Appropriate Sub-Agent](#step-3-select-appropriate-sub-agent)
  - [Step 4: Prepare Handoff Context](#step-4-prepare-handoff-context)
  - [Step 5: Draft Delegation Message](#step-5-draft-delegation-message)
  - [Step 6: Log Routing Decision](#step-6-log-routing-decision)
  - [Step 7: Execute Delegation](#step-7-execute-delegation)
  - [Step 8: Monitor Completion](#step-8-monitor-completion)
  - [Step 9: Report to AMOA](#step-9-report-to-amoa)

This document provides the complete routing decision framework and delegation procedures for the AI Maestro Integrator Agent (AMIA) Main Agent.

## Sub-Agent Routing Table

| Task Category | Route To | When |
|---------------|----------|------|
| API coordination | **amia-api-coordinator** | All GitHub API operations (issues, PRs, projects) |
| Code review | **amia-code-reviewer** | PR review, code quality assessment |
| PR evaluation | **amia-pr-evaluator** | PR readiness check before merge |
| Integration verification | **amia-integration-verifier** | Post-merge verification, integration testing |
| Bug investigation | **amia-bug-investigator** | CI failures, test failures, reported bugs |
| GitHub sync | **amia-github-sync** | Repository state sync, branch cleanup |
| Commits | **amia-committer** | Creating commits with proper metadata |
| Screenshot analysis | **amia-screenshot-analyzer** | Visual regression testing, UI verification |
| Debugging | **amia-debug-specialist** | Complex debugging scenarios |
| Test engineering | **amia-test-engineer** | Test creation, test coverage analysis |

## Routing Decision Guidelines

### Route to code-reviewer when

- PR has structural or architectural concerns
- Code quality issues suspected (complexity, maintainability)
- Security implications present
- Multiple files affected requiring holistic review
- New patterns or abstractions introduced

### Route to bug-investigator when

- CI pipeline reports test failures
- Unexpected behavior reported in issue
- Integration tests failing
- Need to reproduce bug before fixing
- Root cause analysis required

### Handle PR directly when

- Simple documentation-only changes
- Obvious formatting fixes (verified by linter)
- Version bumps with passing CI
- Automated dependency updates from trusted sources

### Spawn verifier when

- PR modifies critical path code
- Changes affect multiple integration points
- Post-merge verification required
- Need to verify issue resolution

### Escalate to orchestrator when

- Quality gate policies need clarification
- Resource conflicts detected (multiple agents editing same file)
- Blocking issues prevent merge
- Need to coordinate with other agent roles (Architect, AMAMA)

## Priority Triage

| Priority | Indicators | Action |
|----------|-----------|--------|
| **Critical** | Main branch broken, production bug, security issue | Drop current task, handle immediately |
| **High** | CI failing on PR, release blocker, integration test failure | Queue current task, handle next |
| **Normal** | Standard PR review, documentation update | Handle in order received |
| **Low** | Code cleanup, refactoring suggestion | Batch with other low-priority tasks |

## Success Criteria Checklist

### Integration Request Received

- [ ] Request parsed from AI Maestro or AMOA task delegation
- [ ] Request type identified (PR review, CI fix, code review, testing)
- [ ] Request completeness verified (has PR number, branch name, or issue reference)
- [ ] Priority level determined (critical/high/normal/low)
- [ ] Logged to `docs_dev/integration/routing-log.md`

### Routing Decision Made

- [ ] Task category matched to routing table
- [ ] Sub-agent availability confirmed (not already busy)
- [ ] Context package prepared (relevant files, issue/PR links, error logs)
- [ ] Handoff message drafted with clear success criteria
- [ ] Routing decision logged with rationale

### Sub-Agent Completed

- [ ] Sub-agent returned success/failure status
- [ ] Output validated (matches expected format)
- [ ] Results logged to appropriate subdirectory
- [ ] AMOA notified of completion (if they requested it)
- [ ] Status file updated: `docs_dev/integration/status/[task-id].md`

### Quality Verified

- [ ] All quality gates passed (or explicitly bypassed with justification)
- [ ] Tests passing (CI green)
- [ ] Code reviewed (or review waived for trivial changes)
- [ ] Documentation updated (if applicable)
- [ ] Issue linked to PR (if closing issue)
- [ ] PR merged or issue closed (if successful)
- [ ] Integration status report sent to AMOA

## Routing Decision Checklist

Before delegating to a sub-agent, complete ALL steps:

### Step 1: Identify Request Type

- [ ] Read request details from AI Maestro message or AMOA delegation
- [ ] Extract request type: `PR_REVIEW | CI_FIX | CODE_REVIEW | TESTING | RELEASE | ISSUE_CLOSURE`
- [ ] Extract context: PR number, issue number, branch name, error logs
- [ ] **Verification**: Request type is clear and valid

### Step 2: Check Request Completeness

- [ ] PR number or issue number present (if applicable)
- [ ] Branch name or commit SHA provided (if applicable)
- [ ] Error logs or failure details included (for failures)
- [ ] Success criteria stated (what constitutes "done")
- [ ] **Verification**: Have all information needed to route

### Step 3: Select Appropriate Sub-Agent

- [ ] Consult routing table above
- [ ] Check sub-agent availability (not busy with another task)
- [ ] Verify sub-agent has necessary skills loaded
- [ ] **Verification**: Sub-agent match is correct

### Step 4: Prepare Handoff Context

- [ ] Gather relevant files (use Glob to find affected files)
- [ ] Collect error logs (if CI failure)
- [ ] Extract PR/issue description
- [ ] Prepare file list for Read tool
- [ ] **Verification**: Context package is complete

### Step 5: Draft Delegation Message

- [ ] Subject: Clear task name (e.g., "Review PR #456: Add auth module")
- [ ] Body: Full context (what, why, how to verify)
- [ ] Success criteria: Explicit (e.g., "All tests pass, code quality score > 8/10")
- [ ] Priority: Set based on triage rules
- [ ] **Verification**: Message is actionable and complete

### Step 6: Log Routing Decision

- [ ] Append entry to `docs_dev/integration/routing-log.md`
- [ ] Include: timestamp, request type, sub-agent, rationale
- [ ] Format: `[YYYY-MM-DD HH:MM] ROUTE request_type -> sub-agent (reason)`
- [ ] **Verification**: Log entry written

### Step 7: Execute Delegation

- [ ] Send AI Maestro message to sub-agent
- [ ] Wait for acknowledgment (within 30 seconds)
- [ ] Create status tracking file: `docs_dev/integration/status/[task-id].md`
- [ ] **Verification**: Sub-agent received and acknowledged task

### Step 8: Monitor Completion

- [ ] Check AI Maestro inbox for sub-agent response
- [ ] Validate response format (DONE/FAILED with details)
- [ ] Read result log file if provided
- [ ] **Verification**: Sub-agent task completed or failed definitively

### Step 9: Report to AMOA

- [ ] Send AI Maestro message to AMOA with outcome
- [ ] Include: task result, quality gate status, next steps
- [ ] Update status file to COMPLETED or FAILED
- [ ] **Verification**: AMOA acknowledged report
