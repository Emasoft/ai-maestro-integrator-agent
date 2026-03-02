---
name: op-compile-multilang-review
description: Compile comprehensive review summary from multilanguage PR analysis
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Compile Multilanguage Review


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Review Summary Template](#review-summary-template)
- [Multilanguage PR Review Summary](#multilanguage-pr-review-summary)
  - [Languages Detected](#languages-detected)
  - [Linter Results](#linter-results)
  - [Cross-Language Interface Review](#cross-language-interface-review)
  - [Summary](#summary)
  - [Recommendation](#recommendation)
  - [Detailed Findings](#detailed-findings)
- [Procedure](#procedure)
- [Categorizing Issues](#categorizing-issues)
  - [Blocking Issues](#blocking-issues)
  - [Warnings](#warnings)
  - [Suggestions](#suggestions)
- [Example Review Workflow](#example-review-workflow)
- [Review Status Decision Tree](#review-status-decision-tree)
- [Formatting Best Practices](#formatting-best-practices)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Aggregate all findings from language detection, linting, and cross-language analysis into a comprehensive review summary. This becomes the final review comment on the PR.

## When to Use

- After completing all language-specific reviews
- After running all linters
- After reviewing cross-language interfaces
- When ready to post final review

## Prerequisites

- Language detection completed (op-detect-pr-languages)
- Linters executed (op-run-multilang-linters)
- Cross-language review done (op-review-cross-language)
- All findings documented

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| Language detection | JSON | Output from op-detect-pr-languages |
| Linter results | JSON | Output from op-run-multilang-linters |
| Cross-language findings | List | Output from op-review-cross-language |
| Review patterns | Notes | Language-specific review notes |

## Output

| Field | Type | Description |
|-------|------|-------------|
| Review summary | Markdown | Formatted review comment |
| Approval status | String | APPROVE, REQUEST_CHANGES, COMMENT |
| Blocking issues | List | Issues that must be fixed |
| Suggestions | List | Non-blocking improvements |

## Review Summary Template

```markdown
## Multilanguage PR Review Summary

### Languages Detected
| Language | Files | Lines Changed |
|----------|-------|---------------|
| Python | 12 | 450 |
| TypeScript | 5 | 200 |
| Bash | 2 | 50 |

### Linter Results

#### Python (ruff, mypy)
- **ruff**: 3 issues found
  - `src/auth.py:10:1` - line too long
  - `src/auth.py:25:5` - unused import
  - `tests/test_auth.py:15:1` - missing docstring
- **mypy**: 0 issues (passed)

#### TypeScript (eslint)
- **eslint**: 2 issues found
  - `src/app.ts:5:1` - 'any' type used
  - `src/components/Login.tsx:30:1` - missing return type

#### Bash (shellcheck)
- **shellcheck**: 0 issues (passed)

### Cross-Language Interface Review

**Interfaces affected:**
- `/api/users` endpoint (Python backend -> TypeScript frontend)

**Findings:**
- Backend added `role` field to User response
- Frontend TypeScript interface updated to match

**Status:** Interfaces are consistent

### Summary

| Category | Count |
|----------|-------|
| Blocking Issues | 0 |
| Warnings | 5 |
| Suggestions | 2 |

### Recommendation

**APPROVE** - No blocking issues found. Minor linting warnings should be addressed but don't block merge.

### Detailed Findings

[Expandable sections with full linter output...]
```

## Procedure

1. **Gather all inputs**
   - Language detection results
   - Linter outputs
   - Cross-language findings
   - Review pattern notes

2. **Categorize findings**
   - Blocking issues (must fix)
   - Warnings (should fix)
   - Suggestions (nice to have)

3. **Format the summary**
   - Use markdown for readability
   - Include tables for quick overview
   - Provide expandable details

4. **Determine approval status**
   - APPROVE: No blocking issues
   - REQUEST_CHANGES: Has blocking issues
   - COMMENT: Only suggestions, no judgment

5. **Post the review**
   ```bash
   gh pr review <PR_NUMBER> --approve --body "$(cat review.md)"
   # or
   gh pr review <PR_NUMBER> --request-changes --body "$(cat review.md)"
   ```

## Categorizing Issues

### Blocking Issues

These MUST be fixed before merge:

- Type errors that will cause runtime failures
- Security vulnerabilities (bandit findings)
- Breaking changes to public APIs
- Cross-language interface mismatches
- Missing tests for critical code paths

### Warnings

These SHOULD be fixed but don't block:

- Style violations (line length, formatting)
- Missing docstrings
- Unused imports
- Deprecated function usage
- Minor type annotation gaps

### Suggestions

Nice to have improvements:

- Code structure improvements
- Performance optimizations
- Additional test coverage
- Documentation improvements

## Example Review Workflow

```bash
# 1. Gather all results
LANG_DETECT=$(cat language_detection.json)
LINTER_RESULTS=$(cat linter_results.json)
CROSS_LANG=$(cat cross_language.md)

# 2. Generate review summary
# (Use template above to format)

# 3. Determine status
if grep -q "blocking" findings.txt; then
    STATUS="--request-changes"
else
    STATUS="--approve"
fi

# 4. Post review
gh pr review 456 $STATUS --body "$(cat review_summary.md)"
```

## Review Status Decision Tree

```
START: Compile findings
    |
    v
Any blocking issues?
    |
    +-- YES --> REQUEST_CHANGES
    |           "X blocking issues must be fixed"
    |
    +-- NO --> Any warnings?
                 |
                 +-- YES --> APPROVE with comments
                 |           "Minor issues noted, not blocking"
                 |
                 +-- NO --> APPROVE
                            "LGTM - all checks passed"
```

## Formatting Best Practices

1. **Start with summary** - Approval status and key numbers
2. **Use tables** - Easy to scan
3. **Group by language** - Logical organization
4. **Include file:line references** - Easy to locate issues
5. **Provide actionable feedback** - How to fix, not just what's wrong
6. **Keep details collapsible** - Full linter output in expandable sections

## Error Handling

| Scenario | Action |
|----------|--------|
| Missing linter results | Note as "not run" in summary |
| Partial data | Include what's available, note gaps |
| Conflicting findings | Flag for human review |

## Related Operations

- [op-detect-pr-languages.md](op-detect-pr-languages.md) - Language detection input
- [op-run-multilang-linters.md](op-run-multilang-linters.md) - Linter results input
- [op-review-cross-language.md](op-review-cross-language.md) - Interface review input
