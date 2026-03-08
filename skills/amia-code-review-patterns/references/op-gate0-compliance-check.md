---
name: op-gate0-compliance-check
description: Perform Gate 0 requirement compliance check before starting PR review
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Gate 0 Compliance Check

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Steps](#steps)
  - [Step 1: Retrieve PR Context](#step-1-retrieve-pr-context)
  - [Step 2: Check Requirement Traceability](#step-2-check-requirement-traceability)
  - [Step 3: Check Technology Compliance](#step-3-check-technology-compliance)
  - [Step 4: Check Scope Compliance](#step-4-check-scope-compliance)
  - [Step 5: Document Findings](#step-5-document-findings)
- [Decision Criteria](#decision-criteria)
- [Example](#example)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Verify that the PR meets basic requirement compliance before starting the two-stage review process. This is a pre-flight check that ensures the PR is even eligible for review.

## When to Use

- Before starting any PR review
- When receiving a new PR review request
- As the first step in the code review workflow

## Prerequisites

- PR number and repository identified
- Access to the PR description and linked issues
- Knowledge of project requirements and scope

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to check |
| repo | string | No | Repository in owner/repo format (defaults to current) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| compliant | boolean | Whether PR passes Gate 0 |
| issues | array | List of compliance issues found |
| recommendation | string | PROCEED, REJECT, or CLARIFY_NEEDED |

## Steps

### Step 1: Retrieve PR Context

```bash
python3 amia_get_pr_context.py --pr <PR_NUMBER>
```

### Step 2: Check Requirement Traceability

Verify the PR:

- Links to at least one issue or requirement
- Has a clear description of what it accomplishes
- Matches the scope of linked issues

### Step 3: Check Technology Compliance

Verify the PR:

- Uses approved technologies and libraries
- Follows project coding standards
- Does not introduce forbidden dependencies

### Step 4: Check Scope Compliance

Verify the PR:

- Does not exceed the scope of linked issues
- Does not include unrelated changes
- Follows the single-responsibility principle for PRs

### Step 5: Document Findings

Record compliance status and any issues found.

## Decision Criteria

| Condition | Decision |
|-----------|----------|
| All checks pass | PROCEED to Stage 1 Quick Scan |
| Minor issues | CLARIFY_NEEDED - request clarification |
| Major issues | REJECT - PR not eligible for review |

## Example

```bash
# Check Gate 0 compliance for PR #123
python3 amia_get_pr_context.py --pr 123

# Verify requirements:
# 1. PR links to issue(s) - check "closes #" or "fixes #" in description
# 2. Description explains the change
# 3. Files changed match expected scope
```

## Error Handling

| Error | Action |
|-------|--------|
| PR not found | Return error, verify PR number |
| No linked issues | Flag as compliance issue, may proceed with caution |
| Description missing | Flag as compliance issue, request author to add description |

## Related Operations

- [op-quick-scan.md](op-quick-scan.md) - Next step after Gate 0 passes
- [requirement-compliance.md](requirement-compliance.md) - Detailed compliance checklist
