---
name: amia-ai-pr-review-methodology
description: "Use when performing PR reviews. Trigger with /amia-ai-pr-review. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
compatibility: Requires code review experience and codebase access.
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
    - Table of Contents
    - 1.1 When to perform context gathering
    - 1.2 Action 1: Read complete files, not just diffs
      - 1.2.1 How to read complete files during a PR review
      - 1.2.2 Example: Good vs bad context gathering
    - 1.3 Action 2: Search for existing solutions and duplicates
      - 1.3.1 How to search for duplicates before analyzing a PR
      - 1.3.2 Example: Discovering an existing solution
    - 1.4 Action 3: Understand the problem (root cause vs symptoms)
      - 1.4.1 How to distinguish root cause from symptoms
      - 1.4.2 Example: Symptom-level vs root-cause understanding
    - 1.5 Action 4: Verify all claims made in the PR
      - 1.5.1 How to verify file path claims
      - 1.5.2 How to verify command availability claims
      - 1.5.3 Example: Verifying a claimed installation path
    - 1.6 Completion checkpoint for Phase 1

2. **Structured Analysis (Phase 2):** Read [phase-2-structured-analysis](references/phase-2-structured-analysis.md), then apply dimensions D1-D5 in order:
    - Table of Contents
    - 2.1 When to use the structured analysis framework
    - 2.2 Overview of the 5 analysis dimensions
    - 2.3 How to apply the dimensions sequentially
    - 2.4 How to flag items requiring author evidence
    - 2.5 Cross-references to each dimension file

   - [dimension-1-problem-verification](references/dimension-1-problem-verification.md)
     - Table of Contents
     - D1.1 When to apply problem verification
     - D1.2 Identifying the exact error message or unexpected behavior
     - D1.3 Determining root cause vs treating symptoms
     - D1.4 Verifying the fix addresses the root cause
     - D1.5 Documenting assumptions about the system and environment
     - D1.6 Testing methodology: before/after, multi-platform, edge cases, automated tests
     - D1.7 Red flags that indicate problem verification failure
     - D1.8 Example: A fix that treats symptoms vs one that addresses root cause
   - [dimension-2-redundancy-check](references/dimension-2-redundancy-check.md)
     - Table of Contents
     - D2.1 When to apply redundancy checking
     - D2.2 Searching for similar patterns in the codebase
     - D2.3 Identifying when existing code already handles the case
     - D2.4 List and array addition analysis: priority order and placement justification
     - D2.5 Configuration changes vs code changes
     - D2.6 Red flags for redundancy
     - D2.7 Example: Detecting a redundant path addition
   - [dimension-3-system-integration](references/dimension-3-system-integration.md)
     - Table of Contents
     - D3.1 When to apply system integration validation
     - D3.2 File path verification on target systems (macOS, Linux, Windows)
     - D3.3 Cross-referencing paths with official documentation
     - D3.4 Path handling: home directory expansion, relative vs absolute, platform-specific
     - D3.5 Installation location accuracy across package managers
     - D3.6 Red flags for integration failures
     - D3.7 Example: Validating a claimed binary installation path
   - [dimension-4-senior-review](references/dimension-4-senior-review.md)
     - Table of Contents
     - D4.1 When to apply senior developer review criteria
     - D4.2 Architectural layer assessment
     - D4.3 Technical debt and maintainability evaluation
     - D4.4 Performance and resource implications
     - D4.5 Security implications analysis
     - D4.6 Backwards compatibility assessment
     - D4.7 Red flags for architectural concerns
     - D4.8 Example: Evaluating a quick fix for long-term impact
   - [dimension-5-false-positive-detection](references/dimension-5-false-positive-detection.md)
     - Table of Contents
     - D5.1 When to apply false positive detection
     - D5.2 Assumption identification and verification
     - D5.3 Alternative explanation analysis
     - D5.4 Placebo effect check methodology
     - D5.5 Cargo cult programming detection
     - D5.6 Confirmation bias detection
     - D5.7 The ultimate test: reversibility verification
     - D5.8 Red flags for false positives
     - D5.9 Example: A false-positive bug fix with before/after analysis

3. **Evidence Requirements (Phase 3):** Compile missing evidence: Problem Demonstration, Solution Validation, Assumption Verification, Cross-Platform Testing.

4. **Scenario Protocol (if applicable):** Match PR type to the appropriate scenario:
   - [scenario-bug-fixes](references/scenario-bug-fixes.md)
     - Table of Contents
     - S-BUG.1 When to use this scenario protocol
     - S-BUG.2 Original error identification
     - S-BUG.3 Root cause identification requirements
     - S-BUG.4 Reproduction before the fix
     - S-BUG.5 Fix demonstration
     - S-BUG.6 Regression test requirement
     - S-BUG.7 Example: Reviewing a bug fix PR end-to-end
   - [scenario-dependency-updates](references/scenario-dependency-updates.md)
     - Table of Contents
     - S-DEP.1 When to use this scenario protocol
     - S-DEP.2 Justification requirements for new or updated dependencies
     - S-DEP.3 Security vulnerability scanning
     - S-DEP.4 License compatibility checking
     - S-DEP.5 Bundle size and performance impact assessment
     - S-DEP.6 Checking for alternatives using existing dependencies
     - S-DEP.7 Example: Reviewing a PR that adds a new npm package
   - [scenario-path-changes](references/scenario-path-changes.md)
     - Table of Contents
     - S-PATH.1 When to use this scenario protocol
     - S-PATH.2 Mandatory verification steps for path changes
     - S-PATH.3 Verification commands to request from the author
     - S-PATH.4 Evidence requirements specific to path changes
     - S-PATH.5 Example: Reviewing a PR that adds a new binary search path
   - [scenario-performance](references/scenario-performance.md)
     - Table of Contents
     - S-PERF.1 When to use this scenario protocol
     - S-PERF.2 Benchmark requirements (before and after)
     - S-PERF.3 Multiple test runs and statistical significance
     - S-PERF.4 Verifying no functionality regressions
     - S-PERF.5 Significance justification (complexity vs improvement tradeoff)
     - S-PERF.6 Example: Reviewing a caching optimization PR

5. **Generate Review (Phase 4):** Use [review-output-template](references/review-output-template.md) and run [quick-reference-checklist](references/quick-reference-checklist.md) before submitting.
    - **review-output-template** TOC:
      - Table of Contents
      - T.1 When to generate the review output
      - T.2 The complete review output template (copy-paste ready)
      - T.3 How to fill each section of the template
      - T.4 Choosing the final recommendation: APPROVE, REQUEST CHANGES, or COMMENT
      - T.5 Setting the confidence level: High, Medium, or Low
      - T.6 Writing the author note
      - T.7 Example: A completed review output
    - **quick-reference-checklist** TOC:
      - Table of Contents
      - C.1 When to use this checklist
      - C.2 The 12-item pre-approval checklist
      - C.3 How to handle checklist failures
      - C.4 Example: Walking through the checklist for a sample PR

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
| Recommendation | APPROVE / REQUEST CHANGES / COMMENT |

> **Output discipline:** All scripts support `--output-file <path>`.

## Error Handling

Non-zero exit codes on failure. See detailed guide in Resources.

## Resources

- [review-output-template](references/review-output-template.md) — Review output format
  - Table of Contents
  - T.1 When to generate the review output
  - T.2 The complete review output template (copy-paste ready)
  - T.3 How to fill each section of the template
  - T.4 Choosing the final recommendation: APPROVE, REQUEST CHANGES, or COMMENT
  - T.5 Setting the confidence level: High, Medium, or Low
  - T.6 Writing the author note
  - T.7 Example: A completed review output

- [detailed-guide](references/detailed-guide.md) — Full methodology reference
  - Table of Contents
  - 4 Phases Overview
  - 5 Analysis Dimensions
  - Key Principle
  - Evidence Requirements
  - Scenario-Specific Protocols
  - Troubleshooting
  - Error Handling
  - Extended Examples
  - Reference Documents Index
  - Related Skills

## Examples

```bash
gh pr diff 42 > /tmp/pr42.diff
gh pr view 42 --json title,body,files
# Apply D1-D5 dimensions, compile evidence, generate review
gh pr review 42 --body "## Summary\nReviewed with AI PR methodology.\n### Recommendation: APPROVE"
```
