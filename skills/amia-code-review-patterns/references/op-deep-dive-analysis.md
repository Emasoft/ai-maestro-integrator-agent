---
name: op-deep-dive-analysis
description: Execute Stage 2 Deep Dive with 8-dimension analysis
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Deep Dive Analysis (Stage 2)


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [The 8 Dimensions](#the-8-dimensions)
- [Steps](#steps)
  - [Step 1: Functional Correctness (20%)](#step-1-functional-correctness-20)
  - [Step 2: Security (20%)](#step-2-security-20)
  - [Step 3: Testing (15%)](#step-3-testing-15)
  - [Step 4: Architecture & Design (15%)](#step-4-architecture-design-15)
  - [Step 5: Backward Compatibility (15%)](#step-5-backward-compatibility-15)
  - [Step 6: Code Quality (10%)](#step-6-code-quality-10)
  - [Step 7: Performance (5%)](#step-7-performance-5)
  - [Step 8: Documentation (5%)](#step-8-documentation-5)
  - [Step 9: Calculate Final Confidence Score](#step-9-calculate-final-confidence-score)
  - [Step 10: Make Final Decision](#step-10-make-final-decision)
- [Deep Dive Output Template](#deep-dive-output-template)
- [Deep Dive Report: PR #<NUMBER>](#deep-dive-report-pr-number)
  - [Dimension Scores](#dimension-scores)
  - [Findings](#findings)
  - [Final Decision](#final-decision)
- [Example](#example)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Perform comprehensive multi-dimensional analysis of the PR across 8 quality dimensions to make a final approval/rejection decision.

## When to Use

- After Quick Scan (Stage 1) returns GO decision (>= 70% confidence)
- When thorough code quality assessment is required
- Before any merge decision

## Prerequisites

- Quick Scan completed with GO decision
- All PR files accessible
- Understanding of project architecture and standards

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to analyze |
| quick_scan_report | object | Yes | Results from Quick Scan |
| pr_diff | string | Yes | Full diff content |

## Output

| Field | Type | Description |
|-------|------|-------------|
| dimension_scores | object | Score for each of 8 dimensions |
| final_confidence | integer | Weighted confidence score 0-100% |
| findings | array | Detailed findings by dimension |
| decision | string | APPROVED, REJECTED, or CHANGES_REQUESTED |

## The 8 Dimensions

| Dimension | Weight | Key Question |
|-----------|--------|--------------|
| Functional Correctness | 20% | Does it work correctly? |
| Security | 20% | Is it safe and secure? |
| Testing | 15% | Is it adequately tested? |
| Architecture & Design | 15% | Is it well-designed? |
| Backward Compatibility | 15% | Does it break existing functionality? |
| Code Quality | 10% | Is it clean and maintainable? |
| Performance | 5% | Is it efficient? |
| Documentation | 5% | Is it well-documented? |

## Steps

### Step 1: Functional Correctness (20%)

Evaluate:
- [ ] Core functionality works as intended
- [ ] Edge cases handled correctly
- [ ] Input validation present
- [ ] Output correctness verified
- [ ] Error states handled gracefully

See [functional-correctness.md](functional-correctness.md) for detailed checklist.

### Step 2: Security (20%)

Evaluate:
- [ ] Input sanitization
- [ ] Authentication/authorization correct
- [ ] Sensitive data protected
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Dependencies are secure

See [security-analysis.md](security-analysis.md) for detailed checklist.

### Step 3: Testing (15%)

Evaluate:
- [ ] Unit tests present for new code
- [ ] Test coverage adequate
- [ ] Tests are meaningful (not just for coverage)
- [ ] Edge cases tested
- [ ] Integration tests where appropriate

See [testing-analysis.md](testing-analysis.md) for detailed checklist.

### Step 4: Architecture & Design (15%)

Evaluate:
- [ ] SOLID principles followed
- [ ] Design patterns appropriate
- [ ] Code organization logical
- [ ] Dependencies properly managed
- [ ] API design clean

See [architecture-design.md](architecture-design.md) for detailed checklist.

### Step 5: Backward Compatibility (15%)

Evaluate:
- [ ] API changes are backward compatible
- [ ] Database migrations safe
- [ ] Configuration changes documented
- [ ] Deprecation warnings added where needed
- [ ] Breaking changes documented

See [backward-compatibility.md](backward-compatibility.md) for detailed checklist.

### Step 6: Code Quality (10%)

Evaluate:
- [ ] Code is readable
- [ ] Naming conventions followed
- [ ] Functions have single responsibility
- [ ] No code duplication
- [ ] Error handling consistent

See [code-quality.md](code-quality.md) for detailed checklist.

### Step 7: Performance (5%)

Evaluate:
- [ ] Algorithm complexity appropriate
- [ ] No obvious performance issues
- [ ] Resource usage reasonable
- [ ] Database queries optimized

See [performance-analysis.md](performance-analysis.md) for detailed checklist.

### Step 8: Documentation (5%)

Evaluate:
- [ ] Code comments where needed
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Changelog entry added

See [documentation-analysis.md](documentation-analysis.md) for detailed checklist.

### Step 9: Calculate Final Confidence Score

```python
final_score = (
    functional * 0.20 +
    security * 0.20 +
    testing * 0.15 +
    architecture * 0.15 +
    backward_compat * 0.15 +
    code_quality * 0.10 +
    performance * 0.05 +
    documentation * 0.05
)
```

### Step 10: Make Final Decision

| Score | Decision |
|-------|----------|
| >= 80% | APPROVED - Ready for merge |
| 60-79% | CHANGES_REQUESTED - Specific improvements needed |
| < 60% | REJECTED - Major rework required |

## Deep Dive Output Template

```markdown
## Deep Dive Report: PR #<NUMBER>

**Date**: <TIMESTAMP>
**Reviewer**: <AGENT_NAME>

### Dimension Scores

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Functional Correctness | XX% | 20% | X.X |
| Security | XX% | 20% | X.X |
| Testing | XX% | 15% | X.X |
| Architecture & Design | XX% | 15% | X.X |
| Backward Compatibility | XX% | 15% | X.X |
| Code Quality | XX% | 10% | X.X |
| Performance | XX% | 5% | X.X |
| Documentation | XX% | 5% | X.X |
| **TOTAL** | | **100%** | **XX.X** |

### Findings

#### Critical Issues
<LIST_OR_NONE>

#### Major Issues
<LIST_OR_NONE>

#### Minor Issues
<LIST_OR_NONE>

#### Positive Observations
<LIST>

### Final Decision
**Confidence Score**: <PERCENTAGE>%
**Decision**: <APPROVED/CHANGES_REQUESTED/REJECTED>
**Rationale**: <EXPLANATION>
```

## Example

```bash
# Calculate confidence scores
python3 scripts/deep_dive_calculator.py --pr 123 \
    --functional 85 \
    --security 90 \
    --testing 75 \
    --architecture 80 \
    --backward-compat 95 \
    --code-quality 85 \
    --performance 80 \
    --documentation 70
```

## Error Handling

| Error | Action |
|-------|--------|
| Dimension unclear | Request clarification, document uncertainty |
| Conflicting findings | Document both perspectives, escalate if critical |
| Insufficient context | Request additional information before scoring |

## Related Operations

- [op-quick-scan.md](op-quick-scan.md) - Previous step
- [op-calculate-confidence.md](op-calculate-confidence.md) - Score calculation details
- [op-merge-decision.md](op-merge-decision.md) - Next step after decision
