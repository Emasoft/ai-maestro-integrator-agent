---
name: amia-code-review-patterns
description: "Use when reviewing pull requests. Trigger with PR review or code quality requests. Loaded by ai-maestro-integrator-agent-main-agent."
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

Two-stage PR review: Quick Scan (70% threshold) then 8-dimension Deep Dive (80% approval).

## Prerequisites

- Access to the target repository
- Python 3.8+ for helper scripts
- AI Maestro installed

## Instructions

1. **Gate 0 compliance** - Verify requirements per [requirement-compliance](references/requirement-compliance.md)
2. **Stage 1: Quick Scan** - Assess structure, diff, issues; Go/No-Go at 70%+
3. **Stage 2: Deep Dive** - Score 8 dimensions; approve at 80%+
4. **Run quality gates and create report** via `scripts/review_report_generator.py`
5. **Merge or reject PR**; report completion via AI Maestro

### Checklist

Copy this checklist and track your progress:

- [ ] Gate 0 compliance check
- [ ] Stage 1: Quick Scan (Go/No-Go at 70%+)
- [ ] Stage 2: Deep Dive (8 dimensions, approve at 80%+)
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

## Error Handling

Script failures return non-zero exit codes. Check stderr for details.

## Examples

```bash
python scripts/review_report_generator.py --repo owner/repo --pr 42
# Output: {"stage1": "pass", "stage2": "pass", "dimensions": 8, "score": 85, "decision": "approve"}
```

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Core Methodology: Two-Stage Review Process
  - Key Concepts
    - Confidence Scoring System
    - Multi-Dimensional Analysis
  - Quick Reference Tables
    - Confidence Score Ranges
    - Dimension Weight Summary
  - Scripts Available
  - AI Maestro Communication Templates
    - Template 1: Receiving PR Review Request
    - Template 2: Reporting Review Completion
    - Template 3: Requesting Clarification from Author
    - Template 4: Escalating Quality Gate Failure
  - Error Handling
  - Reference Document TOCs
    - Gate 0: Requirement Compliance
    - Stage One: Quick Scan
    - Stage Two: Deep Dive
    - Workflow and Decision Tree
    - Implementation Checklist
    - Review Workflow
    - Commit Conventions
  - Reference Documents Index
