---
name: amia-code-review-patterns
description: "Use when reviewing pull requests. Trigger with PR review or code quality requests."
license: Apache-2.0
compatibility: Requires intermediate software development experience and familiarity with code review basics. Designed for reviewers analyzing pull requests with 1-30+ file changes using an 8-dimensional evaluation framework. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
---

# Code Review Patterns Skill

## Overview

Two-stage PR review methodology. Stage 1 (Quick Scan): surface-level assessment, 70% confidence threshold. Stage 2 (Deep Dive): 8-dimension analysis, 80% approval threshold.

## Prerequisites

- Intermediate software development experience
- Familiarity with code review basics and PR workflows
- Access to the target repository
- Python 3.8+ for helper scripts
- AI Maestro installed for inter-agent communication

## Instructions

1. **Receive PR review request** from AMOA or user via AI Maestro
2. **Gate 0 compliance check** - Verify requirements per `references/requirement-compliance.md`
3. **Stage 1: Quick Scan** - Assess file structure, diff magnitude, obvious issues; calculate confidence score; Go/No-Go at 70%+ (see `references/stage-one-quick-scan.md`)
4. **Stage 2: Deep Dive** - Evaluate all 8 dimensions (Functional, Architecture, Quality, Performance, Security, Testing, Compatibility, Documentation); final score at 80%+ to approve (see `references/stage-two-deep-dive.md`)
5. **Run quality gates** - Tests, linting, documentation checks
6. **Create review report** using `scripts/review_report_generator.py`
7. **Merge or reject PR** based on final decision; close related issues if merged
8. **Report completion** to requesting agent via AI Maestro

### Checklist

Copy this checklist and track your progress:

- [ ] Receive PR review request
- [ ] Gate 0 compliance check
- [ ] Stage 1: Quick Scan (structure, diff, issues, confidence, Go/No-Go)
- [ ] Stage 2: Deep Dive (8 dimensions, final confidence)
- [ ] Run quality gates (tests, linting, docs)
- [ ] Create review report via script
- [ ] Merge or reject; close issues if merged
- [ ] Report completion via AI Maestro

## Output

| Output Type | Format | Contents |
|-------------|--------|----------|
| Quick Scan Report | Markdown table | File structure, diff magnitude, issues, confidence (0-100%), Go/No-Go |
| Deep Dive Report | Markdown table | 8-dimension scores, final confidence (0-100%), approval decision |
| Final Review Document | Markdown | Both stages, confidence calculations, decision rationale |

> **Output discipline:** All scripts support `--output-file <path>`. Use it in automated workflows to minimize token consumption.

## Reference Documents

**Review Process:**

- `references/requirement-compliance.md` -- Gate 0 compliance checklist
- `references/stage-one-quick-scan.md` -- Stage 1 quick scan process
- `references/stage-two-deep-dive.md` -- Stage 2 eight-dimension analysis
- `references/workflow-and-decision-tree.md` -- Workflow and decision flow
- `references/review-workflow.md` -- Review workflow with gates
- `references/implementation-checklist.md` -- Implementation checklist

**8 Dimensions (Deep Dive):**

- `references/functional-correctness.md` -- Dim 1: Functional Correctness
- `references/architecture-design.md` -- Dim 2: Architecture and Design
- `references/code-quality.md` -- Dim 3: Code Quality
- `references/performance-analysis.md` -- Dim 4: Performance
- `references/security-analysis.md` -- Dim 5: Security
- `references/testing-analysis.md` -- Dim 6: Testing
- `references/backward-compatibility.md` -- Dim 7: Backward Compatibility
- `references/documentation-analysis.md` -- Dim 8: Documentation

**Quality and Standards:**

- `references/pre-pr-quality-gate.md` -- Pre-PR validation steps
- `references/commit-conventions.md` -- Commit message conventions
- `references/examples.md` -- Detailed review examples

**Troubleshooting:**

- `references/troubleshooting-performance.md` -- Slow reviews
- `references/troubleshooting-calibration.md` -- Reviewer calibration
- `references/troubleshooting-coverage.md` -- Coverage gaps
- `references/troubleshooting-agreement.md` -- Reviewer disagreements

**Detailed Guide:**

- `references/detailed-guide.md` -- Scoring, dimension weights, AI Maestro templates, reference tables



## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

See `references/detailed-guide.md` for usage examples.
## Resources

See `references/` directory for all reference documents.
