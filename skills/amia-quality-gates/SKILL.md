---
name: amia-quality-gates
description: "Quality gate enforcement for PR integration. Use when verifying code through pre-review, review, pre-merge, or post-merge checkpoints. Trigger with /amia-enforce-gates."
version: 1.0.0
license: Apache-2.0
compatibility: Requires familiarity with CI/CD pipelines, code review processes, and GitHub workflows. Designed for the Integrator Agent role enforcing quality standards. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
---

# AMIA Quality Gates

## Overview

Mandatory checkpoints in the four-gate integration pipeline (Pre-Review, Review, Pre-Merge, Post-Merge). Each gate defines criteria, blocking conditions, and escalation paths. See `references/detailed-guide.md` for full details.

## Prerequisites

- Repository has CI/CD pipeline configured
- GitHub labels from **amia-label-taxonomy** applied
- Review checklist from **amia-code-review-patterns** available
- GitHub CLI (`gh`) installed and authenticated
- Understanding of the four-gate pipeline model

## Instructions

1. Identify the current gate by checking PR labels (no gate label = Pre-Review)
2. Execute gate-specific checks (Pre-Review: tests/lints, Review: 8-dimension review, Pre-Merge: CI/conflicts, Post-Merge: main branch health)
3. Apply gate decision label (passed/failed/warning) based on results
4. If checks pass, advance PR to next gate
5. If checks fail, apply "failed" label and follow escalation path (A, B, C, or D)
6. Document failure reasons in PR comments and notify responsible parties
7. For overrides: verify authority per Override Matrix, document justification, apply `gate:override-applied` label

### Checklist

Copy this checklist and track your progress:

- [ ] Identify current gate by checking PR labels
- [ ] Execute gate-specific checks for current gate
- [ ] Evaluate results against gate criteria
- [ ] Apply appropriate decision label (passed/failed/warning)
- [ ] If PASSED: advance to next gate
- [ ] If FAILED: apply failure label, identify escalation path
- [ ] Document failure reasons in PR comments
- [ ] Notify responsible parties per escalation order
- [ ] If override requested: verify authority and document justification
- [ ] Verify next steps are clear to all parties

## Output

| Field | Description |
|-------|-------------|
| Gate Status | Current gate name and pass/fail decision |
| Check Results | All checks performed with outcomes |
| Labels Applied | Labels added or removed |
| Escalation Actions | Notifications sent or escalations triggered |
| Next Steps | What should happen next in the pipeline |

> **Output discipline:** All scripts support `--output-file <path>`. With flag: JSON to file, summary to stderr. Without: JSON to stdout.

## Reference Documents

**Gate Details:**

- `references/gate-pipeline.md` -- Pipeline flow diagram and transitions
- `references/pre-review-gate.md` -- Gate 1: tests, lints, build, description
- `references/review-gate.md` -- Gate 2: 8-dimension review, 80% confidence
- `references/pre-merge-gate.md` -- Gate 3: CI, conflicts, approval, merge strategies
- `references/post-merge-gate.md` -- Gate 4: main branch health, issue closure

**Escalation and Overrides:**

- `references/escalation-paths.md` -- Escalation paths A, B, C, D
- `references/escalation-procedures.md` -- Detailed procedures per level
- `references/override-policies.md` -- Override authority matrix
- `references/override-examples.md` -- Override examples

**Code Quality Checks:**

- `references/encoding-compliance-checker.md` -- UTF-8 encoding
- `references/unicode-enforcement-hook.md` -- BOM, line endings, non-ASCII

**Procedures and Examples:**

- `references/gate-examples.md` -- Examples for all gates
- `references/gate-checklist.md` -- Enforcement checklist
- `references/gate-decision-flowchart.md` -- Decision flowchart
- `references/label-reference.md` -- Gate and warning label list
- `references/troubleshooting.md` -- Common issues and solutions
- `references/detailed-guide.md` -- Error handling, scripts, integration

**Verification and Evaluation:**

- `references/rule-14-enforcement.md` -- RULE 14 enforcement
- `references/pr-evaluation.md` -- PR evaluation
- `references/integration-verification.md` -- Integration verification

**Related:** amia-label-taxonomy, amia-code-review-patterns, amia-github-pr-workflow, amia-tdd-enforcement, amia-ci-failure-patterns



## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

See `references/detailed-guide.md` for usage examples.
## Resources

See `references/` directory for all reference documents.
