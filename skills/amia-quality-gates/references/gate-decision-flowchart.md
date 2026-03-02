# Gate Decision Flowchart

## Table of Contents

- [Visual Decision Tree](#visual-decision-tree)
- [Pre-Review Gate Decision](#pre-review-gate-decision)
- [Review Gate Decision](#review-gate-decision)
- [Pre-Merge Gate Decision](#pre-merge-gate-decision)
- [Post-Merge Gate Decision](#post-merge-gate-decision)
- [Override Decision Path](#override-decision-path)
- [Escalation Trigger Decision](#escalation-trigger-decision)
- [Key Decision Principles](#key-decision-principles)

## Visual Decision Tree

This flowchart guides gate pass/fail decisions across all four gates.

---

## Pre-Review Gate Decision

```
START: PR Created
    ↓
[Run automated checks]
    ↓
Tests passing? ──NO──→ FAIL (comment with test output) → Escalation Path A
    ↓ YES
Linting passing? ──NO──→ FAIL (comment with lint errors) → Escalation Path A
    ↓ YES
Build succeeds? ──NO──→ FAIL (comment with build log) → Escalation Path A
    ↓ YES
Description present? ──NO──→ FAIL (request description) → Escalation Path A
    ↓ YES
[Check warning conditions]
    ↓
Coverage < 80%? ──YES──→ Apply gate:coverage-warning (non-blocking)
    ↓ NO
Large PR (30+ files)? ──YES──→ Apply gate:large-pr (non-blocking)
    ↓ NO
No changelog? ──YES──→ Apply gate:changelog-needed (non-blocking)
    ↓ NO
[All checks passed]
    ↓
Apply gate:pre-review-passed
    ↓
PASS → Advance to Review Gate
```

---

## Review Gate Decision

```
START: Pre-Review Passed
    ↓
[Perform Stage 1: Quick Scan]
    ↓
Obvious blockers? ──YES──→ FAIL (request changes immediately) → Escalation Path B
    ↓ NO
[Perform Stage 2: Deep Dive]
    ↓
Evaluate 8 dimensions
    ↓
Calculate confidence score
    ↓
Confidence >= 80%? ──NO──→ FAIL (request changes with details) → Escalation Path B
    ↓ YES
[Check blocking conditions]
    ↓
Security issue? ──YES──→ FAIL (BLOCK - no override) → Escalation Path B
    ↓ NO
Breaking change? ──YES──→ FAIL (request compatibility fix) → Escalation Path B
    ↓ NO
Data loss risk? ──YES──→ FAIL (BLOCK - prove safety) → Escalation Path B
    ↓ NO
Critical bugs? ──YES──→ FAIL (fix bugs) → Escalation Path B
    ↓ NO
[Check warning conditions]
    ↓
Docs incomplete? ──YES──→ Apply gate:docs-needed (non-blocking)
    ↓ NO
Perf concerns? ──YES──→ Apply gate:perf-review (non-blocking)
    ↓ NO
[All checks passed]
    ↓
Apply gate:review-passed
    ↓
PASS → Advance to Pre-Merge Gate
```

---

## Pre-Merge Gate Decision

```
START: Review Passed
    ↓
[Run final checks]
    ↓
CI pipeline green? ──NO──→ FAIL (block merge, comment) → Escalation Path C
    ↓ YES
Merge conflicts? ──YES──→ FAIL (request rebase) → Escalation Path C
    ↓ NO
Valid approval? ──NO──→ FAIL (request re-review) → Escalation Path C
    ↓ YES
Branch up-to-date? ──NO (>5 commits)──→ FAIL (request rebase) → Escalation Path C
    ↓ YES or < 5 commits behind
[Check warning conditions]
    ↓
CI slow (>15 min)? ──YES──→ Apply gate:slow-ci (non-blocking)
    ↓ NO
Flaky test? ──YES──→ Apply gate:flaky-test (non-blocking)
    ↓ NO
New warnings? ──YES──→ Apply gate:new-warnings (non-blocking)
    ↓ NO
[All checks passed]
    ↓
Apply gate:pre-merge-passed
    ↓
PASS → Execute Merge
    ↓
Merge Complete
    ↓
Advance to Post-Merge Gate
```

---

## Post-Merge Gate Decision

```
START: Merge Complete
    ↓
[Monitor main branch]
    ↓
Wait for main CI to complete (timeout: 30 min)
    ↓
Main CI passed? ──NO──→ FAIL (immediate escalation) → Escalation Path D → Evaluate revert
    ↓ YES
[Check for regressions]
    ↓
New test failures? ──YES──→ FAIL (immediate escalation) → Escalation Path D → Evaluate revert
    ↓ NO
[Check deployment (if applicable)]
    ↓
Deployment succeeded? ──NO──→ FAIL (rollback) → Escalation Path D → Evaluate revert
    ↓ YES
[Check production health]
    ↓
Error spike? ──YES──→ FAIL (emergency response) → Escalation Path D → Evaluate revert
    ↓ NO
[All checks passed]
    ↓
Apply gate:post-merge-passed
    ↓
Close linked issue
    ↓
PASS → Integration Complete
```

---

## Override Decision Path

```
Gate Blocked
    ↓
Override needed? ──NO──→ Follow normal escalation path
    ↓ YES
Is it security issue? ──YES──→ NO OVERRIDE ALLOWED (BLOCK)
    ↓ NO
Check Override Authority Matrix
    ↓
Authority available? ──NO──→ Escalate to alternate authority
    ↓ YES
[Document override]
    ↓
Justification provided? ──NO──→ Request justification
    ↓ YES
Risk mitigation documented? ──NO──→ Request mitigation plan
    ↓ YES
Follow-up actions planned? ──NO──→ Request follow-up plan
    ↓ YES
Apply gate:override-applied label
    ↓
Comment with full override documentation
    ↓
OVERRIDE APPROVED → Advance gate
```

---

## Escalation Trigger Decision

```
Gate Failed
    ↓
Which gate?
    ├─ Pre-Review? → Escalation Path A
    ├─ Review? → Escalation Path B
    ├─ Pre-Merge? → Escalation Path C
    └─ Post-Merge? → Escalation Path D

Each Escalation Path:
    ↓
First Action (notify author/request changes)
    ↓
Wait for response (defined timeframe)
    ↓
Response received? ──YES──→ Issue resolved? ──YES──→ Return to gate
    ↓ NO                                       ↓ NO
Second Action (escalate to AMOA)               Return to First Action
    ↓
Wait for AMOA response
    ↓
Resolved? ──YES──→ Return to gate
    ↓ NO
Third Action (final escalation)
    ↓
Decision by authority
    ↓
Override or Close PR
```

---

## Key Decision Principles

1. **Security issues = No override** - Always block
2. **Infrastructure failures ≠ code failures** - Don't blame PR for infra issues
3. **When in doubt, ask** - Escalate unclear situations
4. **Post-merge failures = Revert first** - Safety over speed
5. **Document all overrides** - Transparency required
6. **Warning labels don't block** - But track technical debt
