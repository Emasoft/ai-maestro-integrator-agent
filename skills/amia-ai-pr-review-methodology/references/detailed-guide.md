# AI PR Review Methodology -- Detailed Guide

## Contents

- [4 Phases Overview](#4-phases-overview)
- [5 Analysis Dimensions](#5-analysis-dimensions)
- [Key Principle](#key-principle)
- [Evidence Requirements](#evidence-requirements)
- [Scenario-Specific Protocols](#scenario-specific-protocols)
- [Troubleshooting](#troubleshooting)
- [Error Handling](#error-handling)
- [Extended Examples](#extended-examples)
- [Related Skills](#related-skills)

## 4 Phases Overview

1. **Context Gathering** -- Mandatory preparation before any analysis begins. Read complete files, search for duplicates, understand the problem, and verify claims. See `references/phase-1-context-gathering.md` for the full protocol including 4 context gathering actions and completion checkpoint.

2. **Structured Analysis** -- Apply 5 analysis dimensions systematically to evaluate the PR. See `references/phase-2-structured-analysis.md` for the overview and cross-references to each dimension file.

3. **Evidence Requirements** -- Determine what evidence is missing and must be provided by the author before the PR can be approved. Every flagged item from Phase 2 that lacks evidence becomes a required evidence item.

4. **Review Output** -- Synthesize findings into a structured, actionable review document using the template in `references/review-output-template.md`.

## 5 Analysis Dimensions

1. **Problem Verification** -- Confirm the PR addresses the real root cause, not just symptoms. Identify the exact error message or unexpected behavior, determine root cause vs symptoms, verify the fix addresses the root cause, document assumptions, and apply before/after, multi-platform, edge case, and automated testing methodology. See `references/dimension-1-problem-verification.md`.

2. **Redundancy Check** -- Ensure the change does not duplicate existing functionality. Search for similar patterns, identify when existing code already handles the case, analyze list/array additions for priority order and placement justification, and evaluate configuration changes vs code changes. See `references/dimension-2-redundancy-check.md`.

3. **System Integration Validation** -- Verify paths, commands, and environment assumptions are correct on all target platforms. Covers file path verification on macOS/Linux/Windows, cross-referencing with official documentation, home directory expansion, relative vs absolute paths, platform-specific handling, and installation location accuracy across package managers. See `references/dimension-3-system-integration.md`.

4. **Senior Developer Review** -- Evaluate architecture, maintainability, performance, security, and backwards compatibility. Covers architectural layer assessment, technical debt evaluation, performance and resource implications, security implications, and backwards compatibility. See `references/dimension-4-senior-review.md`.

5. **False Positive Detection** -- Challenge assumptions, detect cargo cult programming, and apply the ultimate reversibility test. Covers assumption identification and verification, alternative explanation analysis, placebo effect check, cargo cult programming detection, confirmation bias detection, and the reversibility test. This is the most critical dimension. See `references/dimension-5-false-positive-detection.md`.

## Key Principle

Every claim in a PR must be backed by evidence. "It works on my machine" is not evidence. "Here is the output of the verification command on three target platforms" is evidence.

## Evidence Requirements

The minimum required evidence categories are:

1. **Problem Demonstration** -- Error message, stack trace, or screenshot; reproduction steps; root cause explanation.
2. **Solution Validation** -- Demonstration that the fix resolves the issue; test coverage; before/after comparison.
3. **Assumption Verification** -- For file paths: output of `ls` or equivalent. For commands: output showing availability. For system behavior: documentation links or code proof.
4. **Cross-Platform Testing** -- Results on all supported platforms; platform-specific edge cases handled.

## Scenario-Specific Protocols

If the PR matches one of these scenarios, use the corresponding reference file:

- **Path/File Changes:** `references/scenario-path-changes.md` -- Mandatory verification steps, verification commands to request from the author, evidence requirements specific to path changes.
- **Bug Fixes:** `references/scenario-bug-fixes.md` -- Original error identification, root cause requirements, reproduction before fix, fix demonstration, regression test requirement.
- **Performance Improvements:** `references/scenario-performance.md` -- Benchmark requirements (before/after), multiple test runs and statistical significance, functionality regression checks, complexity vs improvement tradeoff.
- **Dependency Updates:** `references/scenario-dependency-updates.md` -- Justification requirements, security vulnerability scanning, license compatibility, bundle size and performance impact, checking for alternatives.

## Troubleshooting

### The PR has too many file changes to review thoroughly

Break the review into logical groups of related files. Apply Phase 1 (context gathering) to each group separately. Focus the 5 dimensions on files most likely to contain issues: files with path changes, configuration changes, or security-sensitive code. See `references/phase-1-context-gathering.md` section 1.2 for guidance on prioritizing which files to read in full.

### The author cannot reproduce the reported bug

This is a red flag for false positive detection. See `references/dimension-5-false-positive-detection.md` section D5.4 (placebo effect check) and D5.7 (the ultimate reversibility test). If the bug cannot be reproduced, the fix cannot be validated. Request reproduction steps and evidence before proceeding.

### The PR modifies paths but the reviewer has no access to the target system

Request the author to provide terminal output (`ls -la`, `which`, `type`, or equivalent commands) showing the paths exist on each supported platform. See `references/scenario-path-changes.md` section S-PATH.3 for the specific verification commands to request.

### The reviewer is unsure whether a change is redundant

See `references/dimension-2-redundancy-check.md` section D2.2 for search strategies to find existing code that might already handle the case. If you find a potential duplicate, ask the author to explain why the existing solution is insufficient.

### The author becomes defensive when asked for evidence

Reiterate that evidence requirements are standard practice, not personal criticism. Frame questions as "help me understand" rather than "prove you are right." See `references/review-output-template.md` section T.6 for guidance on writing constructive author notes.

### The PR is a dependency update with no visible code changes

Even if the code diff is small, dependency updates require their own review protocol. See `references/scenario-dependency-updates.md` for the full checklist including security scanning, license checking, and bundle size assessment.

## Error Handling

### Error: Reviewer skips Phase 1 and jumps directly to analysis

Skipping context gathering leads to incorrect conclusions because the reviewer is working from partial information (the diff alone). Always complete all 4 actions in `references/phase-1-context-gathering.md` before writing any analysis. If you realize mid-review that you skipped context gathering, stop, go back to Phase 1, and restart.

### Error: Conflicting findings across analysis dimensions

When Dimension 1 (Problem Verification) says the fix is correct but Dimension 5 (False Positive Detection) flags it as a potential false positive, this means the fix addresses the symptom but may not address the root cause. Apply the reversibility test from `references/dimension-5-false-positive-detection.md` section D5.7. If removing the change brings the problem back, the fix is real. If it does not, the fix is a false positive.

### Error: Insufficient evidence to complete the review

When the PR lacks enough information to evaluate one or more dimensions, do not guess or assume. Issue a REQUEST CHANGES recommendation listing exactly which evidence items are missing. Use the evidence categories from Phase 3 as your checklist. Do not approve a PR when any required evidence category is empty.

## Extended Examples

### Example 1: Reviewing a false-positive bug fix

A PR claims to fix a "file not found" error by adding a new search path to a configuration array. During Phase 1, the reviewer reads the complete configuration file and discovers that the path is already present three entries above the new addition. During Dimension 2 (Redundancy Check), the reviewer confirms the duplication. During Dimension 5 (False Positive Detection), the reviewer applies the reversibility test: removing the new entry does not reintroduce the error, proving the fix is a false positive. The reviewer issues REQUEST CHANGES with evidence showing the existing entry and the reversibility test result.

### Example 2: Reviewing a cross-platform path change

A PR adds `$HOME/.local/bin` to the PATH lookup for a CLI tool. During Phase 1, the reviewer verifies the path exists on Linux. During Dimension 3 (System Integration Validation), the reviewer checks macOS (where the tool installs to a different location) and Windows (where the path convention is entirely different). The reviewer requests terminal output from all three platforms. The final review is REQUEST CHANGES until cross-platform evidence is provided.

### Example 3: Reviewing a performance optimization PR

A PR replaces a linear search with a hash map lookup, claiming 10x speedup. During Phase 1, the reviewer reads the full module to understand the data flow. During Dimension 1, the reviewer confirms the linear search was indeed the bottleneck. During Dimension 4 (Senior Developer Review), the reviewer notes the hash map increases memory usage and checks whether the tradeoff is acceptable. The reviewer requests benchmark output showing before/after timing across at least 3 runs with statistical variance. The review is COMMENT with a list of required benchmark evidence, referencing `references/scenario-performance.md`.

## Reference Documents Index

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

## Related Skills

- **amia-code-review-patterns** -- General code review patterns and anti-patterns that complement the PR-specific methodology.
- **amia-quality-gates** -- Quality gate definitions and thresholds used to determine when a PR meets the bar for approval.
- **amia-github-pr-workflow** -- The end-to-end GitHub PR workflow including creation, review assignment, and merge procedures.
- **amia-tdd-enforcement** -- Test-driven development enforcement rules, relevant when evaluating whether a PR includes adequate test coverage.
- **amia-multilanguage-pr-review** -- Language-specific review considerations for PRs spanning multiple programming languages.
