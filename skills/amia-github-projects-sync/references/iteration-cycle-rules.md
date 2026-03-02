# Iteration Cycle Rules

## Table of Contents

1. [When understanding iteration cycle requirements](#purpose)
2. [When determining if task is complete](#core-principle)
3. [When following the review iteration flow](#iteration-cycle-flow)
4. [When reviewing PRs for approval](#review-checklist-all-must-pass)
5. [When tracking review iterations](#iteration-counter)
6. [When updating the iteration counter](#iteration-counter-location)
7. [If too many iterations occur](#maximum-iterations)
8. [If considering partial approval](#partial-approval-not-allowed)
9. [When waiting for next iteration](#between-iterations)
10. [When labeling PRs by iteration count](#labels-for-iteration-tracking)

## Purpose

Define how tasks iterate through review cycles until 100% approval is achieved.

## Core Principle

**NO TASK IS COMPLETE UNTIL 100% APPROVED**

A task stays in review until ALL criteria pass. There is no "good enough" - only DONE or NOT DONE.

### 100% Approval Rule

The **100% Approval Rule** means:
- ALL checklist items must pass (not "most" or "almost all")
- ALL tests must succeed (0 failures allowed)
- ALL review comments must be addressed
- ALL acceptance criteria must be met

Partial completion is NOT completion. A PR cannot be merged until it achieves 100% approval across all review dimensions.

## Iteration Cycle Flow

```
                    ┌─────────────────┐
                    │   PR Created    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
              ┌────►│   AI Review     │◄────┐
              │     └────────┬────────┘     │
              │              │              │
              │              ▼              │
              │     ┌─────────────────┐     │
              │     │  Review Check   │     │
              │     └────────┬────────┘     │
              │              │              │
              │    ┌─────────┴─────────┐    │
              │    │                   │    │
              ▼    ▼                   ▼    │
     ┌─────────────────┐      ┌─────────────────┐
     │ Changes Needed  │      │   Approved      │
     └────────┬────────┘      └────────┬────────┘
              │                        │
              ▼                        ▼
     ┌─────────────────┐      ┌─────────────────┐
     │  Fix & Iterate  │      │     Merge       │
     └────────┬────────┘      └─────────────────┘
              │
              └──────────────────────────────────►
```

## Review Checklist (ALL Must Pass)

### Code Quality
- [ ] All tests pass (0 failures)
- [ ] Code coverage ≥ 80%
- [ ] No linting errors
- [ ] No type errors
- [ ] Follows project style guide

### Functionality
- [ ] Meets all acceptance criteria
- [ ] No regressions in existing features
- [ ] Edge cases handled
- [ ] Error handling complete

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No SQL injection risks
- [ ] Authentication/authorization correct

### Documentation
- [ ] Code comments where needed
- [ ] API documentation updated
- [ ] README updated if applicable
- [ ] CHANGELOG entry added

## Iteration Counter

Track iterations per PR:

```markdown
## Review Iterations

| # | Date | Reviewer | Result | Issues |
|---|------|----------|--------|--------|
| 1 | Dec 30 | orchestrator | Changes | 3 lint errors |
| 2 | Dec 30 | orchestrator | Changes | 1 test failing |
| 3 | Dec 31 | orchestrator | Approved | - |
```

## Iteration Counter Location

The iteration counter table MUST be maintained in the **PR description**, immediately after the "## Changes Made" section.

### Update Process

After each review iteration:

1. **Agent updates the iteration table** in PR description
2. Increment the iteration number
3. Record date, reviewer, result, and issues found
4. Push updated PR description

### Example PR Description with Counter

```markdown
## Summary
[Brief description of changes]

## Changes Made
- [Change 1]
- [Change 2]

## Iteration History

| Iteration | Date | Reviewer | Result | Issues |
|-----------|------|----------|--------|--------|
| 1 | 2025-12-30 | orchestrator | Changes Requested | 3 issues |
| 2 | 2025-12-31 | orchestrator | Approved | 0 issues |

## Test Results
[Test summary]
```

### Automation Note

The iteration table update is MANUAL. Agent must:
1. Edit PR description (not add comment)
2. Add new row to table
3. Update previous row if re-reviewing same iteration

## Maximum Iterations

- **Soft limit**: 5 iterations - escalate to senior review
- **Hard limit**: 10 iterations - reassess task scope/assignment

## Partial Approval NOT Allowed

| Scenario | Action |
|----------|--------|
| "Tests pass but coverage low" | NOT APPROVED - fix coverage |
| "Works but needs refactoring" | NOT APPROVED - refactor first |
| "90% of acceptance criteria" | NOT APPROVED - complete 100% |
| "Minor issues, can fix later" | NOT APPROVED - fix now |

## Between Iterations

1. Agent receives review feedback
2. Agent addresses ALL issues (not partial)
3. Agent runs full test suite locally
4. Agent verifies all checks pass
5. Agent requests re-review
6. Cycle repeats until 100% approved

## Labels for Iteration Tracking

| Label | Meaning |
|-------|---------|
| `iteration:1` | First review |
| `iteration:2` | Second review |
| `iteration:3+` | Third or more reviews |
| `needs-major-rework` | Significant changes required |
