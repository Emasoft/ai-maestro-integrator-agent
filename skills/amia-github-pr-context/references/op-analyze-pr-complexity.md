# Operation: Analyze PR Complexity

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Complexity Factors](#complexity-factors)
- [Steps](#steps)
  - [Step 1: Gather Metrics](#step-1-gather-metrics)
  - [Step 2: Calculate Size Category](#step-2-calculate-size-category)
  - [Step 3: Identify Sensitive Files](#step-3-identify-sensitive-files)
  - [Step 4: Assess Module Spread](#step-4-assess-module-spread)
  - [Step 5: Check Test Coverage](#step-5-check-test-coverage)
  - [Step 6: Calculate Final Score](#step-6-calculate-final-score)
  - [Step 7: Generate Review Time Estimate](#step-7-generate-review-time-estimate)
  - [Step 8: Create Delegation Recommendation](#step-8-create-delegation-recommendation)
- [Example: Complete Analysis](#example-complete-analysis)
- [Complexity Score Guide](#complexity-score-guide)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Assess the complexity of a Pull Request to determine review effort, delegation strategy, and time estimates.

## When to Use

- At the start of PR review planning
- To estimate review time
- To decide on review delegation
- To identify high-risk areas

## Prerequisites

- PR context retrieved (op-get-pr-context)
- File list available (op-get-pr-files)
- Diff statistics available (op-get-pr-diff --stat)

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number |
| context | object | Yes | Output from op-get-pr-context |
| files | array | Yes | Output from op-get-pr-files |
| diff_stats | object | No | Output from op-get-pr-diff --stat |

## Output

| Field | Type | Description |
|-------|------|-------------|
| complexity_score | integer | 1-10 complexity rating |
| size_category | string | small, medium, large, extra-large |
| estimated_review_time | string | Time estimate for review |
| risk_areas | array | Identified high-risk areas |
| delegation_recommendation | object | How to split review |

## Complexity Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Files Changed | 20% | Number of files affected |
| Lines Changed | 20% | Total additions + deletions |
| File Types | 15% | Variety of file types |
| Module Spread | 15% | How many modules/directories |
| Sensitive Files | 20% | Security, config, DB files |
| Test Coverage | 10% | Presence of test changes |

## Steps

### Step 1: Gather Metrics

```bash
# Get context
CONTEXT=$(python3 amia_get_pr_context.py --pr <NUMBER>)

# Get files
FILES=$(python3 amia_get_pr_files.py --pr <NUMBER>)

# Get diff stats
STATS=$(python3 amia_get_pr_diff.py --pr <NUMBER> --stat)
```

### Step 2: Calculate Size Category

| Category | Files | Lines | Score Impact |
|----------|-------|-------|--------------|
| Small | 1-10 | 1-100 | +1 |
| Medium | 11-30 | 101-500 | +3 |
| Large | 31-50 | 501-1000 | +5 |
| Extra-Large | 50+ | 1000+ | +7 |

### Step 3: Identify Sensitive Files

High-risk file patterns:

- `**/auth/**` - Authentication code
- `**/security/**` - Security code
- `**/*config*` - Configuration files
- `**/db/**`, `**/models/**` - Database code
- `**/api/**` - API endpoints
- `.env*`, `*secret*`, `*credential*` - Secrets

```bash
# Check for sensitive files
echo "$FILES" | jq -r '.[].filename' | grep -E "(auth|security|config|db|api|\.env|secret|credential)" -i
```

### Step 4: Assess Module Spread

```bash
# Count unique top-level directories
echo "$FILES" | jq -r '.[].filename' | cut -d'/' -f1 | sort -u | wc -l
```

| Modules | Impact |
|---------|--------|
| 1-2 | Focused change (+1) |
| 3-5 | Moderate spread (+2) |
| 6+ | Wide spread (+3) |

### Step 5: Check Test Coverage

```bash
# Check if tests are included
TEST_FILES=$(echo "$FILES" | jq '[.[] | select(.filename | test("test"))] | length')
CODE_FILES=$(echo "$FILES" | jq '[.[] | select(.filename | test("test") | not)] | length')
```

| Condition | Impact |
|-----------|--------|
| Tests >= Code files | Good coverage (-1) |
| Some tests | Partial coverage (0) |
| No tests | Missing coverage (+2) |

### Step 6: Calculate Final Score

```python
def calculate_complexity(metrics):
    score = 0

    # Size
    files = metrics['files_changed']
    lines = metrics['lines_changed']

    if files <= 10 and lines <= 100:
        score += 1
    elif files <= 30 and lines <= 500:
        score += 3
    elif files <= 50 and lines <= 1000:
        score += 5
    else:
        score += 7

    # Sensitive files
    score += metrics['sensitive_file_count'] * 0.5

    # Module spread
    if metrics['modules'] <= 2:
        score += 1
    elif metrics['modules'] <= 5:
        score += 2
    else:
        score += 3

    # Test coverage
    if metrics['test_ratio'] >= 1:
        score -= 1
    elif metrics['test_ratio'] == 0:
        score += 2

    return min(10, max(1, round(score)))
```

### Step 7: Generate Review Time Estimate

| Complexity | Estimated Time |
|------------|----------------|
| 1-2 | 15-30 minutes |
| 3-4 | 30-60 minutes |
| 5-6 | 1-2 hours |
| 7-8 | 2-4 hours |
| 9-10 | 4+ hours (consider splitting) |

### Step 8: Create Delegation Recommendation

```json
{
  "delegation_recommendation": {
    "single_reviewer_ok": true,
    "suggested_split": [
      {"area": "src/auth/", "reviewer_type": "security"},
      {"area": "src/db/", "reviewer_type": "database"},
      {"area": "tests/", "reviewer_type": "qa"}
    ],
    "special_attention": [
      "src/auth/oauth.py - New authentication method",
      "src/db/migrations/ - Database schema changes"
    ]
  }
}
```

## Example: Complete Analysis

```bash
# Get all data
CONTEXT=$(python3 amia_get_pr_context.py --pr 123)
FILES=$(python3 amia_get_pr_files.py --pr 123)
STATS=$(python3 amia_get_pr_diff.py --pr 123 --stat)

# Analyze
# Files: 18
# Lines: 450
# Modules: 3 (src/auth, src/db, tests)
# Sensitive: 5 files (auth, db)
# Tests: 4 test files

# Result:
{
  "complexity_score": 5,
  "size_category": "medium",
  "estimated_review_time": "1-2 hours",
  "risk_areas": [
    "src/auth/oauth.py - New OAuth implementation",
    "src/db/user.py - User table changes"
  ],
  "delegation_recommendation": {
    "single_reviewer_ok": false,
    "suggested_split": [
      {"area": "src/auth/", "reviewer_type": "security_expert"},
      {"area": "src/db/", "reviewer_type": "database_expert"}
    ]
  }
}
```

## Complexity Score Guide

| Score | Category | Description |
|-------|----------|-------------|
| 1-2 | Trivial | Small, focused change |
| 3-4 | Simple | Moderate change, clear scope |
| 5-6 | Moderate | Substantial change, some complexity |
| 7-8 | Complex | Large change, multiple concerns |
| 9-10 | Very Complex | Consider splitting PR |

## Error Handling

| Error | Action |
|-------|--------|
| Missing context | Run op-get-pr-context first |
| Missing files | Run op-get-pr-files first |
| Analysis incomplete | Return partial results with warnings |

## Related Operations

- [op-get-pr-context.md](op-get-pr-context.md) - Get PR context
- [op-get-pr-files.md](op-get-pr-files.md) - Get file list
- [op-get-pr-diff.md](op-get-pr-diff.md) - Get diff statistics
