# Review Gate

## Table of Contents

- [Purpose](#purpose)
- [Required Checks](#required-checks)
  - [8-Dimension Review Framework](#8-dimension-review-framework)
  - [Confidence Score Calculation](#confidence-score-calculation)
- [Blocking Conditions](#blocking-conditions)
- [Warning Conditions (Non-Blocking)](#warning-conditions-non-blocking)
- [Gate Pass Procedure](#gate-pass-procedure)
- [Gate Fail Procedure](#gate-fail-procedure)
- [Re-Review Triggers](#re-review-triggers)
- [Stage 1: Quick Scan (5 minutes)](#stage-1-quick-scan-5-minutes)
- [Stage 2: Deep Dive (20-40 minutes)](#stage-2-deep-dive-20-40-minutes)
- [Troubleshooting](#troubleshooting)
  - [Confidence Score Borderline (75-79%)](#confidence-score-borderline-75-79)
  - [Reviewer Disagrees with Prior Review](#reviewer-disagrees-with-prior-review)
  - [Author Disputes Review Findings](#author-disputes-review-findings)

---

## Purpose

> **MULTI-REPO RULE:** All `gh` commands MUST include `--repo "$OWNER/$REPO"` since the integrator works across multiple repos.

The Review Gate ensures code quality through systematic human review. It evaluates code across 8 dimensions and calculates a confidence score.

## Required Checks

### 8-Dimension Review Framework

Refer to **amia-code-review-patterns** skill for complete review methodology. Summary:

| Dimension | Weight | Evaluation Criteria |
|-----------|--------|---------------------|
| 1. Correctness | 15% | Logic correctness, edge cases handled |
| 2. Security | 15% | No vulnerabilities, secure patterns used |
| 3. Performance | 10% | Efficient algorithms, no bottlenecks |
| 4. Maintainability | 15% | Clean code, follows patterns |
| 5. Testability | 15% | Well-tested, test coverage adequate |
| 6. Documentation | 10% | Code comments, API docs present |
| 7. Architecture | 10% | Fits system design, no coupling issues |
| 8. Best Practices | 10% | Follows team standards |

### Confidence Score Calculation

**Formula**: Weighted average across all 8 dimensions

**Example**:

```
Correctness: 90% × 0.15 = 13.5
Security: 100% × 0.15 = 15.0
Performance: 80% × 0.10 = 8.0
Maintainability: 85% × 0.15 = 12.75
Testability: 70% × 0.15 = 10.5
Documentation: 90% × 0.10 = 9.0
Architecture: 95% × 0.10 = 9.5
Best Practices: 80% × 0.10 = 8.0

Total Confidence: 86.25% ✅ PASS (>= 80%)
```

## Blocking Conditions

These issues **always block** regardless of confidence score:

| Issue Type | Block Reason | Required Action |
|------------|--------------|-----------------|
| Security vulnerability | Safety critical | Fix vulnerability, no override allowed |
| Breaking change (unintentional) | API contract violation | Make compatible or get maintainer approval |
| Data loss risk | Irreversible damage possible | Prove safety or revert change |
| Test failures | Broken code | Fix tests |
| Critical bugs | Production impact | Fix bugs |

## Warning Conditions (Non-Blocking)

| Condition | Warning Label | Trigger |
|-----------|--------------|---------|
| Documentation incomplete | `gate:docs-needed` | Missing docstrings or API docs |
| Performance concerns | `gate:perf-review` | Potential inefficiency noted |
| Large PR complexity | `gate:large-pr` | High cyclomatic complexity |
| Minor style issues | `gate:style-issues` | Non-critical style deviations |

## Gate Pass Procedure

```bash
# Calculate confidence score (manual or via script)
CONFIDENCE=85

# If >= 80% and no blocking issues
gh pr edit $PR_NUMBER --add-label "gate:review-passed"
gh pr edit $PR_NUMBER --remove-label "gate:review-pending"

# Approve PR
gh pr review $PR_NUMBER --approve --body "✅ Review gate passed

Confidence Score: ${CONFIDENCE}%

All 8 dimensions evaluated. No blocking issues found. Approved for merge pending pre-merge checks."
```

## Gate Fail Procedure

```bash
# If < 80% or blocking issues present
gh pr edit $PR_NUMBER --add-label "gate:review-failed"

# Request changes
gh pr review $PR_NUMBER --request-changes --body "❌ Review gate failed

Confidence Score: 65% (threshold: 80%)

**Blocking Issues:**
- [List blocking issues with severity]

**Improvement Areas:**
- [List specific improvements needed per dimension]

Please address these issues and request re-review."

# Follow Escalation Path B if changes not addressed
```

## Re-Review Triggers

Re-review required when:

- Author addresses requested changes
- New commits pushed after review
- Blocking issues resolved
- Author explicitly requests re-review via comment

## Stage 1: Quick Scan (5 minutes)

**Purpose**: Rapid triage to identify obvious blockers

**Actions**:

1. Check PR size (< 400 lines preferred)
2. Verify tests present and passing
3. Scan for obvious security issues (SQL injection, XSS, etc.)
4. Check architecture fit
5. Decision: Proceed to Stage 2 or request changes immediately

## Stage 2: Deep Dive (20-40 minutes)

**Purpose**: Thorough evaluation across all 8 dimensions

**Actions**:

1. Evaluate each dimension per **amia-code-review-patterns**
2. Calculate dimension scores
3. Compute overall confidence score
4. Document findings
5. Make gate decision

## Troubleshooting

### Confidence Score Borderline (75-79%)

If score is close to threshold:

1. Review borderline dimensions
2. Request targeted improvements (not full rework)
3. Consider warning labels instead of blocking
4. Re-evaluate after improvements

### Reviewer Disagrees with Prior Review

If second reviewer conflicts with first:

1. Document disagreement
2. Escalate to senior reviewer
3. Discuss in PR comments
4. Senior reviewer makes final call

### Author Disputes Review Findings

If author disagrees with review:

1. Engage in constructive discussion in PR comments
2. Author can provide additional context
3. Reviewer can adjust score if justified
4. If unresolved, escalate to AMOA or maintainer
