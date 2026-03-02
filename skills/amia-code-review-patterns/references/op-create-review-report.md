---
name: op-create-review-report
description: Create final review document combining Quick Scan and Deep Dive results
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Create Review Report


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Report Structure](#report-structure)
- [Summary](#summary)
- [Stage 1: Quick Scan Results](#stage-1-quick-scan-results)
  - [File Structure](#file-structure)
  - [Diff Statistics](#diff-statistics)
  - [Initial Assessment](#initial-assessment)
  - [Obvious Issues Found](#obvious-issues-found)
  - [Red Flags](#red-flags)
- [Stage 2: Deep Dive Analysis](#stage-2-deep-dive-analysis)
  - [Dimension Scores](#dimension-scores)
  - [Detailed Findings](#detailed-findings)
- [Final Decision](#final-decision)
  - [Required Actions Before Merge](#required-actions-before-merge)
  - [Blocking Issues](#blocking-issues)
- [Reviewer Information](#reviewer-information)
- [Steps](#steps)
  - [Step 1: Gather All Data](#step-1-gather-all-data)
  - [Step 2: Generate Report Using Script](#step-2-generate-report-using-script)
  - [Step 3: Review Generated Report](#step-3-review-generated-report)
  - [Step 4: Save Report](#step-4-save-report)
  - [Step 5: Return Report Path](#step-5-return-report-path)
- [Example](#example)
- [Report File Naming Convention](#report-file-naming-convention)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Generate the final comprehensive review document that combines Quick Scan results, Deep Dive analysis, confidence scores, and the final decision with rationale.

## When to Use

- After completing Deep Dive analysis
- When confidence score has been calculated
- Before communicating review decision to stakeholders

## Prerequisites

- Quick Scan completed
- Deep Dive completed
- Confidence score calculated
- Decision determined

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number reviewed |
| quick_scan_report | object | Yes | Results from Stage 1 |
| deep_dive_report | object | Yes | Results from Stage 2 |
| confidence_score | float | Yes | Final calculated score |
| decision | string | Yes | APPROVED, CHANGES_REQUESTED, or REJECTED |

## Output

| Field | Type | Description |
|-------|------|-------------|
| report_path | string | Path to generated report file |
| report_content | string | Full markdown content |
| summary | string | One-line summary for quick reference |

## Report Structure

```markdown
# Code Review Report: PR #<NUMBER>

## Summary
- **PR Title**: <TITLE>
- **Author**: <AUTHOR>
- **Review Date**: <TIMESTAMP>
- **Final Decision**: <APPROVED/CHANGES_REQUESTED/REJECTED>
- **Confidence Score**: <PERCENTAGE>%

---

## Stage 1: Quick Scan Results

### File Structure
- Files changed: <COUNT>
- Scope category: <small/medium/large>

### Diff Statistics
- Lines added: <COUNT>
- Lines deleted: <COUNT>

### Initial Assessment
- Initial confidence: <PERCENTAGE>%
- Go/No-Go decision: <GO/NO-GO>

### Obvious Issues Found
<LIST_OR_NONE>

### Red Flags
<LIST_OR_NONE>

---

## Stage 2: Deep Dive Analysis

### Dimension Scores

| Dimension | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Functional Correctness | XX% | 20% | XX.X |
| Security | XX% | 20% | XX.X |
| Testing | XX% | 15% | XX.X |
| Architecture & Design | XX% | 15% | XX.X |
| Backward Compatibility | XX% | 15% | XX.X |
| Code Quality | XX% | 10% | XX.X |
| Performance | XX% | 5% | XX.X |
| Documentation | XX% | 5% | XX.X |
| **TOTAL** | | **100%** | **XX.X%** |

### Detailed Findings

#### Critical Issues
<LIST_OR_NONE>

#### Major Issues
<LIST_OR_NONE>

#### Minor Issues
<LIST_OR_NONE>

#### Positive Observations
<LIST>

---

## Final Decision

**Decision**: <APPROVED/CHANGES_REQUESTED/REJECTED>

**Confidence Score**: <PERCENTAGE>%

**Rationale**:
<DETAILED_EXPLANATION>

### Required Actions Before Merge
<LIST_IF_CHANGES_REQUESTED>

### Blocking Issues
<LIST_IF_REJECTED>

---

## Reviewer Information
- **Reviewer**: <AGENT_NAME>
- **Review Method**: Two-Stage Review (Quick Scan + Deep Dive)
- **Report Generated**: <TIMESTAMP>
```

## Steps

### Step 1: Gather All Data

Collect:
- Quick Scan report
- Deep Dive report
- Confidence calculation
- PR metadata

### Step 2: Generate Report Using Script

```bash
python3 scripts/review_report_generator.py \
    --pr <NUMBER> \
    --quick-scan <PATH_TO_QUICK_SCAN> \
    --deep-dive <PATH_TO_DEEP_DIVE> \
    --output <OUTPUT_PATH>
```

### Step 3: Review Generated Report

Verify:
- All sections populated
- Scores match calculations
- Decision is consistent with score
- Rationale is clear and actionable

### Step 4: Save Report

Save to standardized location:
```
docs_dev/integration/reports/pr-<NUMBER>-review-<TIMESTAMP>.md
```

### Step 5: Return Report Path

Provide the path for communication to other agents/stakeholders.

## Example

```bash
# Generate the final report
python3 scripts/review_report_generator.py \
    --pr 123 \
    --quick-scan ./reports/pr-123-quick-scan.json \
    --deep-dive ./reports/pr-123-deep-dive.json \
    --output ./docs_dev/integration/reports/pr-123-review.md

# Output: Report generated at ./docs_dev/integration/reports/pr-123-review.md
```

## Report File Naming Convention

```
pr-<NUMBER>-review-<YYYYMMDD-HHMMSS>.md
```

Example: `pr-123-review-20250205-143022.md`

## Error Handling

| Error | Action |
|-------|--------|
| Missing Quick Scan data | Cannot generate - run Quick Scan first |
| Missing Deep Dive data | Cannot generate - run Deep Dive first |
| Score mismatch | Recalculate confidence before generating |
| Output path not writable | Use fallback path, report error |

## Related Operations

- [op-deep-dive-analysis.md](op-deep-dive-analysis.md) - Provides Deep Dive input
- [op-calculate-confidence.md](op-calculate-confidence.md) - Provides score
- [op-merge-decision.md](op-merge-decision.md) - Uses report for decision execution
