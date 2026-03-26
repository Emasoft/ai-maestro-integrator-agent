---
name: amia-ai-pr-review-methodology
description: "Trigger with /amia-ai-pr-review. Use when performing deep evidence-based PR reviews, investigating false-positive fixes, or validating integration changes."
license: Apache-2.0
compatibility: Requires intermediate software development experience, code review basics, and access to the full codebase for running verification commands.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
---

# AI PR Review Methodology Skill

## Overview

Evidence-based PR review using 4 phases and 5 analysis dimensions to catch false positives, redundant code, and unverified assumptions.

## Prerequisites

- PR workflow knowledge and ability to read diffs
- Shell access and codebase access for verification

## Instructions

1. **Gather Context (Phase 1):** Read [phase-1-context-gathering](references/phase-1-context-gathering.md). Read complete files (not just diffs), search for duplicates, understand root cause, verify all claims.

2. **Structured Analysis (Phase 2):** Read [phase-2-structured-analysis](references/phase-2-structured-analysis.md), then apply dimensions D1-D5 in order:
   - [dimension-1-problem-verification](references/dimension-1-problem-verification.md)
   - [dimension-2-redundancy-check](references/dimension-2-redundancy-check.md)
   - [dimension-3-system-integration](references/dimension-3-system-integration.md)
   - [dimension-4-senior-review](references/dimension-4-senior-review.md)
   - [dimension-5-false-positive-detection](references/dimension-5-false-positive-detection.md)

3. **Evidence Requirements (Phase 3):** Compile missing evidence: Problem Demonstration, Solution Validation, Assumption Verification, Cross-Platform Testing.

4. **Scenario Protocol (if applicable):** Match PR type to the appropriate scenario:
   - [scenario-bug-fixes](references/scenario-bug-fixes.md)
   - [scenario-dependency-updates](references/scenario-dependency-updates.md)
   - [scenario-path-changes](references/scenario-path-changes.md)
   - [scenario-performance](references/scenario-performance.md)

5. **Generate Review (Phase 4):** Use [review-output-template](references/review-output-template.md) and run [quick-reference-checklist](references/quick-reference-checklist.md) before submitting.

### Checklist

Copy this checklist and track your progress:

- [ ] Read complete files, not just the diff
- [ ] Search for existing solutions and duplicates
- [ ] Verify all claims and understand root cause
- [ ] Apply all 5 analysis dimensions (D1-D5)
- [ ] Compile missing evidence list
- [ ] Apply scenario-specific protocol if applicable
- [ ] Generate structured review using the template

## Output

| Section | Content |
|---------|---------|
| Summary | PR overview and overall assessment |
| Findings | Strengths, questions, blocking red flags |
| Evidence | Required evidence checklist for author |
| Recommendation | APPROVE / REQUEST CHANGES / COMMENT |
| Confidence | High / Medium / Low |

See the review output template and detailed guide in Resources for template details.

> **Output discipline:** All scripts support `--output-file <path>`.

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See the detailed guide in Resources for error scenarios.

## Examples

```bash
python scripts/amia_pr_review.py --repo owner/repo --pr 42
# Output: {"verdict": "request_changes", "score": 65, "findings": 4, "false_positives": 1}
```

## Resources

[review-output-template](references/review-output-template.md):
  - T.1 When to generate the review output
  - T.2 The complete review output template (copy-paste ready)
  - T.3 How to fill each section of the template
  - T.4 Choosing the final recommendation: APPROVE, REQUEST CHANGES, or COMMENT
  - T.5 Setting the confidence level: High, Medium, or Low
  - T.6 Writing the author note
  - T.7 Example: A completed review output

[detailed-guide](references/detailed-guide.md):
  - 4 Phases Overview
  - 5 Analysis Dimensions
  - Key Principle
  - Evidence Requirements
  - Scenario-Specific Protocols
  - Troubleshooting
  - Error Handling
  - Extended Examples
  - Related Skills
