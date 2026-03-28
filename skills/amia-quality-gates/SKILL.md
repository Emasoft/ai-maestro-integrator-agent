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

## Reference Documents

See `references/` directory for all reference documents. Key files: `references/gate-pipeline.md` (pipeline flow), `references/escalation-paths.md` (escalation), `references/override-policies.md` (overrides), `references/detailed-guide.md` (full guide).

**Related skills:** amia-label-taxonomy, amia-code-review-patterns, amia-github-pr-workflow, amia-tdd-enforcement, amia-ci-failure-patterns

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

```bash
python scripts/amia_quality_gate_check.py --repo owner/repo --pr 42
# Output: {"gate_status": "pass", "gate": "pre-review", "checks_passed": 5, "checks_failed": 0}
```

See `references/detailed-guide.md` for more examples.

## Resources

See `references/` directory for all reference documents.
