---
name: amia-github-pr-checks
description: "Use when monitoring PR checks. Trigger with CI status, check verification, or PR readiness requests. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
tags: "github, ci-cd, pull-requests, checks, automation"
metadata:
  version: 1.0.0
  author: Emasoft
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub PR Checks Skill

## Overview

Monitor, interpret, and wait for GitHub PR check statuses. Use when verifying CI/CD checks before merge, waiting for pending checks, or investigating failures.

## Prerequisites

- **gh CLI** installed and authenticated (`gh auth login`)
- **Repository access**: read access to target repository
- **Python 3.8+** for running scripts

## Instructions

1. **Get current status**: `python amia_get_pr_checks.py --pr <number>`
2. **Check required only**: add `--required-only` flag
3. **Quick mergeable check**: add `--summary-only` flag
4. **Wait for completion**: `python amia_wait_for_checks.py --pr <number> --timeout <seconds>`
5. **Investigate failure**: `python amia_get_check_details.py --pr <number> --check "<name>"`
6. **Parse JSON output**: check `all_passing` or `final_status` field
7. **Act on results**: merge if passing, fix if failing, wait if pending

### Checklist

Copy this checklist and track your progress:

- [ ] Verify gh CLI authenticated: `gh auth status`
- [ ] Get PR check status with `amia_get_pr_checks.py`
- [ ] Review `all_passing` field in JSON output
- [ ] If pending, wait with `amia_wait_for_checks.py`
- [ ] If failing, investigate with `amia_get_check_details.py`
- [ ] Identify required vs optional failing checks
- [ ] Take action: merge / fix / wait
- [ ] Verify PR is ready for merge before proceeding

## Output

| Output Type | Format | Contents |
|-------------|--------|----------|
| Check Status Report | JSON | Pass/fail counts, individual conclusions, required check status |
| Wait Completion Report | JSON | Final status, timeout status, wait time, checks summary |
| Check Details | JSON | Duration, logs URL, failure output for a specific check |
| Exit Code | Integer | 0=success, 1=bad params, 2=not found, 3=API error, 4=not auth |

> **Output discipline:** All scripts support `--output-file <path>`. Use it in automated workflows to minimize token consumption.

## Error Handling

Exit 1: bad params. Exit 2-4: API errors. See detailed guide in Resources.

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Decision Tree: Which Script Do I Need?
  - Check Status Quick Reference
  - Scripts Reference
    - 1. amia_get_pr_checks.py
    - 2. amia_wait_for_checks.py
    - 3. amia_get_check_details.py
  - Error Handling
    - Common Issues
  - Exit Codes (Standardized)
  - Debugging Commands

## Examples

### Example 1: Check and Wait for PR Merge Readiness

```bash
# Get current status
python amia_get_pr_checks.py --pr 123

# If checks pending, wait up to 10 minutes
python amia_wait_for_checks.py --pr 456 --timeout 600

# If a check failed, get details
python amia_get_check_details.py --pr 456 --check "build"
```
