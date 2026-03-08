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

Evidence-based PR review using 4 phases and 5 analysis dimensions. Catches false positives, redundant code, unverified assumptions, and cargo cult programming before merge.

## Prerequisites

- Basic PR workflow knowledge (creating, reviewing, merging)
- Ability to read diffs and understand file-level changes
- Shell access to verify paths and tool availability
- Access to the codebase under review (or ability to search/read it)

## Instructions

1. **Gather Context (Phase 1):** Read `references/phase-1-context-gathering.md` and complete all 4 actions: read complete files (not just diffs), search for duplicates, understand root cause, verify all claims.

2. **Run Structured Analysis (Phase 2):** Read `references/phase-2-structured-analysis.md`, then apply each dimension in order:
   - D1: Problem Verification -- `references/dimension-1-problem-verification.md`
   - D2: Redundancy Check -- `references/dimension-2-redundancy-check.md`
   - D3: System Integration -- `references/dimension-3-system-integration.md`
   - D4: Senior Review -- `references/dimension-4-senior-review.md`
   - D5: False Positive Detection -- `references/dimension-5-false-positive-detection.md`

3. **Determine Evidence Requirements (Phase 3):** Compile missing evidence from 4 categories: Problem Demonstration, Solution Validation, Assumption Verification, Cross-Platform Testing.

4. **Apply Scenario Protocol (if applicable):** Match the PR type to: `references/scenario-path-changes.md`, `references/scenario-bug-fixes.md`, `references/scenario-performance.md`, or `references/scenario-dependency-updates.md`.

5. **Generate Review Output (Phase 4):** Use `references/review-output-template.md` to produce the final structured review document.

6. **Final Checklist:** Run through `references/quick-reference-checklist.md` before submitting.

### Checklist

- [ ] Read complete files affected by the PR, not just the diff
- [ ] Search for existing solutions and duplicates
- [ ] Understand root cause (not just symptoms)
- [ ] Verify all claims in the PR description
- [ ] Apply all 5 analysis dimensions (D1-D5)
- [ ] Compile missing evidence list
- [ ] Apply scenario-specific protocol if applicable
- [ ] Generate structured review using the template
- [ ] Confirm cross-platform compatibility
- [ ] Confirm adequate testing (before/after, edge cases)

## Output

| Section | Content |
|---------|---------|
| Summary | PR overview and overall assessment |
| Findings | Strengths, questions, blocking red flags |
| Evidence | Required evidence checklist for author |
| Recommendation | APPROVE / REQUEST CHANGES / COMMENT |
| Confidence | High / Medium / Low |

Template: `references/review-output-template.md`

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

**Core Workflow:**

- `references/phase-1-context-gathering.md` -- Context gathering actions
- `references/phase-2-structured-analysis.md` -- 5 dimensions overview
- `references/review-output-template.md` -- Review output template
- `references/quick-reference-checklist.md` -- Pre-approval checklist

**Analysis Dimensions:**

- `references/dimension-1-problem-verification.md` -- Root cause analysis
- `references/dimension-2-redundancy-check.md` -- Duplicate detection
- `references/dimension-3-system-integration.md` -- Platform validation
- `references/dimension-4-senior-review.md` -- Architecture review
- `references/dimension-5-false-positive-detection.md` -- Reversibility testing

**Scenario Protocols:**

- `references/scenario-path-changes.md` -- Path/file changes
- `references/scenario-bug-fixes.md` -- Bug fixes
- `references/scenario-performance.md` -- Performance optimizations
- `references/scenario-dependency-updates.md` -- Dependency updates

**Extended Guide:**

- `references/detailed-guide.md` -- Troubleshooting, error handling, examples

## Examples

### Example 1: False-positive bug fix review

```
Phase 1: Read full config file -> discover path already exists 3 entries above
Dim 2 (Redundancy): Confirm duplication
Dim 5 (False Positive): Reversibility test -> removing new entry does NOT
  reintroduce error -> fix is false positive
Result: REQUEST CHANGES with evidence of existing entry + reversibility test
```
