---
name: amia-quality-gates
description: "Use when enforcing quality gates. Trigger with /amia-enforce-gates. Loaded by ai-maestro-integrator-agent-main-agent."
version: 1.0.0
license: Apache-2.0
compatibility: Requires CI/CD and GitHub workflow experience. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
---

# AMIA Quality Gates

## Overview

Four-gate integration pipeline (Pre-Review, Review, Pre-Merge, Post-Merge) with blocking conditions and escalation paths.

## Prerequisites

- CI/CD pipeline configured with GitHub CLI (`gh`) authenticated
- GitHub labels from **amia-label-taxonomy** applied
- Review checklist from **amia-code-review-patterns** available

## Instructions

1. Identify current gate from PR labels (no label = Pre-Review)
2. Run gate checks (Pre-Review: tests/lints, Review: 8-dim review, Pre-Merge: CI/conflicts, Post-Merge: main health)
3. Apply decision label (passed/failed/warning); if passed, advance to next gate
4. If failed, apply failure label, escalate (path A/B/C/D), document in PR comments
5. For overrides: verify authority, document justification, apply `gate:override-applied`

### Checklist

Copy this checklist and track your progress:

- [ ] Identify current gate from PR labels
- [ ] Execute gate-specific checks
- [ ] Apply decision label (passed/failed/warning)
- [ ] If PASSED: advance to next gate
- [ ] If FAILED: apply failure label, escalate, document in PR
- [ ] Handle overrides: verify authority, document justification
- [ ] Confirm next steps are clear to all parties

## Output

| Field | Description |
|-------|-------------|
| Gate Status | Current gate name and pass/fail decision |
| Check Results | All checks performed with outcomes |
| Labels Applied | Labels added or removed |
| Escalation Actions | Notifications sent or escalations triggered |
| Next Steps | What should happen next in the pipeline |

> **Output discipline:** All scripts support `--output-file <path>`. With flag: JSON to file, summary to stderr. Without: JSON to stdout.

## Error Handling

Non-zero exit codes on failure. See detailed guide in Resources.

## Resources

**Related skills:** amia-label-taxonomy, amia-code-review-patterns, amia-github-pr-workflow, amia-tdd-enforcement, amia-ci-failure-patterns

[gate-pipeline](references/gate-pipeline.md) — Pipeline flow:
  - Overview
  - Pipeline Diagram
  - Gate Transitions
    - Transition: Pre-Review -> Review
    - Transition: Review -> Pre-Merge
    - Transition: Pre-Merge -> Merge
    - Transition: Merge -> Post-Merge
    - Transition: Post-Merge -> Complete
  - Failure Handling
  - Parallel Gates
  - Gate Bypass

[escalation-paths](references/escalation-paths.md) — Escalation:
  - Escalation Path A: Pre-Review Gate Failure
  - Escalation Path B: Review Gate Failure
  - Escalation Path C: Pre-Merge Gate Failure
  - Escalation Path D: Post-Merge Gate Failure

[override-policies](references/override-policies.md) — Overrides:
  - Overrides Are Exceptions
  - Override Authority Matrix
  - Override Procedure

[detailed-guide](references/detailed-guide.md) — Full guide:
  - Purpose and Principles
  - Gate Types and Pipeline Position
  - Error Handling
  - Output Discipline
  - Design Document Scripts
  - Encoding Compliance Scripts
  - Unicode Enforcement Scripts
  - PR Gate Scripts
  - Script Locations
  - Integration with Other Skills

## Examples

```bash
# Check Pre-Review gate for PR #42
gh pr view 42 --json labels,statusCheckRollup
# Verify tests pass
gh pr checks 42 --required
# Apply gate label
gh pr edit 42 --add-label "gate:pre-review-passed"
# Advance to Review gate
gh pr edit 42 --add-label "gate:review"
```

**Expected result:** PR #42 transitions from Pre-Review to Review gate with labels `gate:pre-review-passed` and `gate:review` applied, CI checks confirmed green.
