# Operation: Execute Review Gate

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Required Checks](#required-checks)
- [The 8 Dimensions](#the-8-dimensions)
- [Steps](#steps)
  - [Step 1: Gather PR Context](#step-1-gather-pr-context)
  - [Step 2: Execute Quick Scan (Stage 1)](#step-2-execute-quick-scan-stage-1)
  - [Step 3: Execute Deep Dive (Stage 2)](#step-3-execute-deep-dive-stage-2)
  - [Step 4: Calculate Confidence Score](#step-4-calculate-confidence-score)
  - [Step 5: Check Blocking Thresholds](#step-5-check-blocking-thresholds)
  - [Step 6: Generate Review Report](#step-6-generate-review-report)
  - [Step 7: Apply Gate Decision](#step-7-apply-gate-decision)
- [Gate Pass Criteria](#gate-pass-criteria)
- [Example](#example)
- [Failure Handling](#failure-handling)
- [Review Gate Failed](#review-gate-failed)
  - [Dimension Scores](#dimension-scores)
  - [Required Changes](#required-changes)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Perform comprehensive code review using the 8-dimension analysis framework. This is the human/AI review gate that evaluates code quality across multiple dimensions.

## When to Use

- After Pre-Review Gate passes
- When gate is identified as review pending
- When re-review is requested after changes

## Prerequisites

- Pre-Review Gate passed
- PR files and diff accessible
- Review methodology (amia-code-review-patterns) available
- Reviewer has code understanding capability

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to review |
| repo | string | No | Repository in owner/repo format |
| quick_scan_result | object | No | Previous quick scan if available |

## Output

| Field | Type | Description |
|-------|------|-------------|
| gate_passed | boolean | Whether review meets 80% threshold |
| confidence_score | float | Final weighted confidence score |
| dimension_scores | object | Score for each of 8 dimensions |
| review_report_path | string | Path to generated review report |

## Required Checks

| Check | Threshold | Description |
|-------|-----------|-------------|
| Overall Confidence | >= 80% | Weighted score across all dimensions |
| Security Dimension | >= 70% | Security score must meet minimum |
| Functional Dimension | >= 70% | Functional correctness must meet minimum |

## The 8 Dimensions

| Dimension | Weight | Blocking Threshold |
|-----------|--------|-------------------|
| Functional Correctness | 20% | < 70% blocks |
| Security | 20% | < 70% blocks |
| Testing | 15% | None |
| Architecture & Design | 15% | None |
| Backward Compatibility | 15% | < 60% blocks (for APIs) |
| Code Quality | 10% | None |
| Performance | 5% | None |
| Documentation | 5% | None |

## Steps

### Step 1: Gather PR Context

```bash
python3 amia_get_pr_context.py --pr <NUMBER>
python3 amia_get_pr_files.py --pr <NUMBER>
python3 amia_get_pr_diff.py --pr <NUMBER>
```

### Step 2: Execute Quick Scan (Stage 1)

See [op-quick-scan.md](../../amia-code-review-patterns/references/op-quick-scan.md)

- Assess file structure
- Review diff magnitude
- Identify obvious issues
- Calculate initial confidence

### Step 3: Execute Deep Dive (Stage 2)

See [op-deep-dive-analysis.md](../../amia-code-review-patterns/references/op-deep-dive-analysis.md)

Evaluate all 8 dimensions:

1. Functional Correctness
2. Security
3. Testing
4. Architecture & Design
5. Backward Compatibility
6. Code Quality
7. Performance
8. Documentation

### Step 4: Calculate Confidence Score

```bash
python3 scripts/deep_dive_calculator.py \
    --functional <SCORE> \
    --security <SCORE> \
    --testing <SCORE> \
    --architecture <SCORE> \
    --backward-compat <SCORE> \
    --code-quality <SCORE> \
    --performance <SCORE> \
    --documentation <SCORE>
```

### Step 5: Check Blocking Thresholds

Even if overall score >= 80%, check:

- Security >= 70%
- Functional >= 70%
- Backward Compatibility >= 60% (if API changes)

### Step 6: Generate Review Report

```bash
python3 scripts/review_report_generator.py --pr <NUMBER> --output <PATH>
```

### Step 7: Apply Gate Decision

If confidence >= 80% and no blocking threshold failures:

```bash
gh pr edit <NUMBER> --remove-label "gate:review-pending" --add-label "gate:review-passed"
```

If confidence < 80% or blocking threshold failed:

```bash
gh pr edit <NUMBER> --add-label "gate:review-failed"
```

## Gate Pass Criteria

ALL of these must be true:

- [ ] Overall confidence score >= 80%
- [ ] Security dimension >= 70%
- [ ] Functional Correctness dimension >= 70%
- [ ] Backward Compatibility >= 60% (if public API changes)
- [ ] No critical issues identified

## Example

```bash
# Get PR context
python3 amia_get_pr_context.py --pr 123

# Calculate score (after evaluation)
python3 scripts/deep_dive_calculator.py \
    --functional 85 --security 90 --testing 75 \
    --architecture 80 --backward-compat 95 \
    --code-quality 85 --performance 80 --documentation 70

# Output: Final Score: 84.5% - PASSED

# Apply label
gh pr edit 123 --remove-label "gate:review-pending" --add-label "gate:review-passed"
```

## Failure Handling

If gate fails:

1. Apply `gate:review-failed` label
2. Add review comment with findings
3. Follow [Escalation Path B](escalation-paths.md)

```bash
gh pr review <NUMBER> --request-changes --body "$(cat <<'EOF'
## Review Gate Failed

**Confidence Score**: XX% (required: 80%)

### Dimension Scores
| Dimension | Score | Status |
|-----------|-------|--------|
| Security | XX% | BLOCKING |
| ... | ... | ... |

### Required Changes
1. <CHANGE_1>
2. <CHANGE_2>

Please address these issues and request re-review.
EOF
)"
```

## Error Handling

| Error | Action |
|-------|--------|
| Cannot access files | Check permissions, retry |
| Diff too large | Sample key files, flag for manual review |
| Unclear requirements | Request clarification, defer decision |

## Related Operations

- [op-execute-pre-review-gate.md](op-execute-pre-review-gate.md) - Previous gate
- [op-execute-pre-merge-gate.md](op-execute-pre-merge-gate.md) - Next gate after pass
- [op-escalate-failure.md](op-escalate-failure.md) - If review fails
