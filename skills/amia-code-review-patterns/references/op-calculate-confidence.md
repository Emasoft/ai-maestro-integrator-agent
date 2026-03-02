---
name: op-calculate-confidence
description: Calculate confidence score from dimension evaluations
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Calculate Confidence Score


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Weight Distribution](#weight-distribution)
- [Calculation Formula](#calculation-formula)
- [Decision Thresholds](#decision-thresholds)
- [Score Interpretation Guidelines](#score-interpretation-guidelines)
  - [For Individual Dimensions](#for-individual-dimensions)
  - [Critical Dimension Failures](#critical-dimension-failures)
- [Steps](#steps)
  - [Step 1: Validate Input Scores](#step-1-validate-input-scores)
  - [Step 2: Apply Weights](#step-2-apply-weights)
  - [Step 3: Sum Contributions](#step-3-sum-contributions)
  - [Step 4: Check Critical Thresholds](#step-4-check-critical-thresholds)
  - [Step 5: Determine Decision](#step-5-determine-decision)
- [Example](#example)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Calculate the final weighted confidence score from individual dimension evaluations to determine PR approval status.

## When to Use

- After completing all 8 dimension evaluations in Deep Dive
- When you need to determine if PR meets approval threshold
- To generate the numerical basis for merge/reject decision

## Prerequisites

- All 8 dimensions evaluated with individual scores
- Understanding of weight distribution
- Deep Dive analysis completed

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| functional | integer | Yes | Functional Correctness score (0-100) |
| security | integer | Yes | Security score (0-100) |
| testing | integer | Yes | Testing score (0-100) |
| architecture | integer | Yes | Architecture & Design score (0-100) |
| backward_compat | integer | Yes | Backward Compatibility score (0-100) |
| code_quality | integer | Yes | Code Quality score (0-100) |
| performance | integer | Yes | Performance score (0-100) |
| documentation | integer | Yes | Documentation score (0-100) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| final_score | float | Weighted final score (0-100) |
| dimension_breakdown | object | Contribution from each dimension |
| decision | string | APPROVED, CHANGES_REQUESTED, or REJECTED |
| threshold_met | boolean | Whether 80% threshold is met |

## Weight Distribution

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Functional Correctness | 20% | Code must work correctly above all |
| Security | 20% | Security vulnerabilities are critical |
| Testing | 15% | Tests validate correctness and prevent regressions |
| Architecture & Design | 15% | Good design ensures maintainability |
| Backward Compatibility | 15% | Breaking changes affect users |
| Code Quality | 10% | Readability affects long-term maintenance |
| Performance | 5% | Efficiency is important but rarely critical |
| Documentation | 5% | Documentation helps future maintainers |

## Calculation Formula

```python
def calculate_confidence(scores):
    weights = {
        'functional': 0.20,
        'security': 0.20,
        'testing': 0.15,
        'architecture': 0.15,
        'backward_compat': 0.15,
        'code_quality': 0.10,
        'performance': 0.05,
        'documentation': 0.05
    }

    total = 0.0
    breakdown = {}

    for dimension, weight in weights.items():
        contribution = scores[dimension] * weight
        breakdown[dimension] = {
            'score': scores[dimension],
            'weight': weight,
            'contribution': contribution
        }
        total += contribution

    return {
        'final_score': round(total, 2),
        'breakdown': breakdown,
        'threshold_met': total >= 80.0,
        'decision': 'APPROVED' if total >= 80 else
                   'CHANGES_REQUESTED' if total >= 60 else 'REJECTED'
    }
```

## Decision Thresholds

| Score Range | Decision | Action |
|-------------|----------|--------|
| 80-100% | APPROVED | PR may be merged |
| 60-79% | CHANGES_REQUESTED | Specific improvements needed before approval |
| 0-59% | REJECTED | Major rework required, significant issues |

## Score Interpretation Guidelines

### For Individual Dimensions

| Score | Meaning |
|-------|---------|
| 90-100 | Excellent - No issues found |
| 80-89 | Good - Minor issues only |
| 70-79 | Acceptable - Some issues to address |
| 60-69 | Marginal - Significant issues present |
| 0-59 | Poor - Critical issues found |

### Critical Dimension Failures

Even if the overall score meets 80%, certain dimension failures should block approval:

| Dimension | Blocking Threshold |
|-----------|-------------------|
| Security | Below 70% always blocks |
| Functional Correctness | Below 70% always blocks |
| Backward Compatibility | Below 60% blocks if public API |

## Steps

### Step 1: Validate Input Scores

Ensure all 8 dimension scores are:
- Present and complete
- Within valid range (0-100)
- Based on actual evaluation (not default values)

### Step 2: Apply Weights

Multiply each dimension score by its weight.

### Step 3: Sum Contributions

Add all weighted contributions for final score.

### Step 4: Check Critical Thresholds

Even with passing overall score, check for critical dimension failures.

### Step 5: Determine Decision

Apply decision thresholds to final score.

## Example

```bash
# Using the calculator script
python3 scripts/deep_dive_calculator.py \
    --functional 85 \
    --security 90 \
    --testing 75 \
    --architecture 80 \
    --backward-compat 95 \
    --code-quality 85 \
    --performance 80 \
    --documentation 70

# Output:
# Final Score: 84.25%
# Decision: APPROVED
# Breakdown:
#   Functional:  85 x 0.20 = 17.00
#   Security:    90 x 0.20 = 18.00
#   Testing:     75 x 0.15 = 11.25
#   Architecture: 80 x 0.15 = 12.00
#   Backward:    95 x 0.15 = 14.25
#   Quality:     85 x 0.10 =  8.50
#   Performance: 80 x 0.05 =  4.00
#   Documentation: 70 x 0.05 = 3.50
#   TOTAL:                   84.50
```

## Error Handling

| Error | Action |
|-------|--------|
| Missing dimension score | Cannot calculate - request missing evaluation |
| Score out of range | Flag as invalid, request correction |
| All dimensions at 100 | Unusual - verify evaluations were thorough |
| All dimensions very low | Verify understanding of criteria |

## Related Operations

- [op-deep-dive-analysis.md](op-deep-dive-analysis.md) - Provides input scores
- [op-merge-decision.md](op-merge-decision.md) - Uses calculated score
- [op-create-review-report.md](op-create-review-report.md) - Documents the score
