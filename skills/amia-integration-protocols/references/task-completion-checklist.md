# Task Completion Checklist (Integrator Agent)

## Table of Contents

- [Before Reporting Task Complete](#before-reporting-task-complete)
  - [1. Acceptance Criteria Met](#1-acceptance-criteria-met)
  - [2. Quality Gates Passed](#2-quality-gates-passed)
  - [3. Integration Verification](#3-integration-verification)
  - [4. Documentation Updated](#4-documentation-updated)
  - [5. Handoff Prepared](#5-handoff-prepared)
  - [6. GitHub Updated (if applicable)](#6-github-updated-if-applicable)
  - [7. Session Memory Updated](#7-session-memory-updated)
- [Verification Loop](#verification-loop)
- [Common Traps (Integrator-Specific)](#common-traps-integrator-specific)
- [Completion Report Format](#completion-report-format)
- [Pre-Completion Checklist for Integrators](#pre-completion-checklist-for-integrators)
- [Integration-Specific Verification](#integration-specific-verification)
  - [API Integrations](#api-integrations)
  - [Webhook Integrations](#webhook-integrations)
  - [Database Integrations](#database-integrations)
- [When to Escalate vs Complete](#when-to-escalate-vs-complete)

## Before Reporting Task Complete

STOP and verify ALL of the following:

### 1. Acceptance Criteria Met
- [ ] ALL acceptance criteria from task definition satisfied
- [ ] Evidence documented for each criterion
- [ ] No "partial" or "mostly" completions
- [ ] Integration endpoints verified working

### 2. Quality Gates Passed
- [ ] Linting passed (ruff check, eslint)
- [ ] Type checking passed (mypy, pyright)
- [ ] Tests pass (pytest, jest)
- [ ] No regressions introduced
- [ ] API contracts validated

### 3. Integration Verification
- [ ] All API endpoints tested with real requests
- [ ] Authentication flows verified
- [ ] Error responses match expected format
- [ ] Rate limiting tested (if applicable)
- [ ] Timeout handling verified
- [ ] Retry logic tested
- [ ] Data transformation validated both directions

### 4. Documentation Updated
- [ ] Code comments explain WHY (not just what)
- [ ] README updated if behavior changed
- [ ] CHANGELOG entry added (if applicable)
- [ ] API documentation updated
- [ ] Integration diagrams updated (if applicable)

### 5. Handoff Prepared
- [ ] Handoff document written to docs_dev/handoffs/
- [ ] Next steps clearly defined
- [ ] AI Maestro message queued
- [ ] Integration credentials documented (secure location)

### 6. GitHub Updated (if applicable)
- [ ] PR created/updated with description
- [ ] Issue comments added with progress
- [ ] Labels updated to reflect status
- [ ] Projects board item moved

### 7. Session Memory Updated
- [ ] activeContext.md reflects completed work
- [ ] progress.md has completion entry
- [ ] patterns.md captures any new learnings

## Verification Loop

Before marking complete, ask yourself:

1. "If I was a different agent reading this, would I know what was done?"
2. "Is there any ambiguity about what 'done' means?"
3. "Did I actually test this with REAL requests, or am I assuming it works?"
4. "Are there edge cases I didn't handle?"
5. "What happens when the external service is unavailable?"
6. "Did I test error paths, not just happy paths?"

If ANY answer is uncertain, the task is NOT complete. Continue work.

## Common Traps (Integrator-Specific)

| Trap | Reality |
|------|---------|
| "API returns 200" | Does NOT equal "correct data returned" |
| "Mock tests pass" | Does NOT equal "real integration works" |
| "Works locally" | Does NOT equal "works in production" |
| "Schema validates" | Does NOT equal "data is correct" |
| "Connection established" | Does NOT equal "integration complete" |
| "Tests compile" | Does NOT equal "tests pass" |
| "Should work" | Does NOT equal "verified working" |
| "Almost done" | Does NOT equal "done" |

## Completion Report Format

When reporting completion:

```yaml
status: COMPLETE
task_id: <uuid>
summary: <1-2 sentences>
evidence:
  - <what proves it's done>
  - <test output, curl examples, etc.>
  - <sample request/response pairs>
files_changed:
  - <path:lines>
integrations_verified:
  - endpoint: <url or service>
    method: <GET/POST/etc>
    tested: <timestamp>
    result: <success/verified>
error_handling:
  - scenario: <what can go wrong>
    handling: <how it's handled>
next_steps: <what happens next>
handoff: <path to handoff doc>
```

## Pre-Completion Checklist for Integrators

Before declaring ANY integration task complete:

1. **Test with real services** - Mocks are for development, not verification
2. **Verify both directions** - Request AND response handling
3. **Test error scenarios** - 4xx, 5xx, timeouts, malformed responses
4. **Check idempotency** - What happens if the same request is sent twice?
5. **Validate data types** - Especially dates, numbers, encodings
6. **Document credentials** - Where are they stored? How are they rotated?
7. **Prepare handoff** - Include sample curl commands for verification

## Integration-Specific Verification

### API Integrations
- [ ] Tested with valid credentials
- [ ] Tested with invalid credentials (should fail gracefully)
- [ ] Tested with expired credentials (should fail gracefully)
- [ ] Response parsing handles all documented response types
- [ ] Pagination handling verified (if applicable)

### Webhook Integrations
- [ ] Webhook receives payloads correctly
- [ ] Signature verification works
- [ ] Idempotency handling tested
- [ ] Retry handling tested

### Database Integrations
- [ ] Connection pooling configured
- [ ] Timeout handling verified
- [ ] Transaction handling tested
- [ ] Rollback scenarios tested

## When to Escalate vs Complete

| Situation | Action |
|-----------|--------|
| All criteria met, verified | Mark COMPLETE |
| 1+ criteria unmet but fixable | Continue work, do NOT mark complete |
| External service unavailable | Mark BLOCKED, document reason |
| Credentials missing/invalid | Mark BLOCKED, request credentials |
| Schema mismatch | Mark BLOCKED, clarify requirements |
