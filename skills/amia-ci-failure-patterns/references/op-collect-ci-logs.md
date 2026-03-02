---
procedure: proc-handle-failed-pr
workflow-instruction: "Step 22 - Handling Failed PRs"
operation: op-collect-ci-logs
description: "Collect CI failure logs from GitHub Actions workflow run"
---

# Operation: Collect CI Failure Logs


## Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Identify the Failed Workflow Run](#step-1-identify-the-failed-workflow-run)
  - [Step 2: Download the Workflow Logs](#step-2-download-the-workflow-logs)
  - [Step 3: Extract Relevant Sections](#step-3-extract-relevant-sections)
  - [Step 4: Save Logs for Analysis](#step-4-save-logs-for-analysis)
- [Output](#output)
- [Verification](#verification)
- [Error Handling](#error-handling)
  - [Authentication failure](#authentication-failure)
  - [Run not found](#run-not-found)
  - [Permission denied](#permission-denied)
- [Next Operation](#next-operation)

## Purpose

This operation retrieves the complete failure logs from a GitHub Actions workflow run to enable diagnosis of CI failures.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository access with read permissions
- The failed workflow run ID or PR number

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| repository | string | Yes | Repository in `owner/repo` format |
| run_id | integer | No | Specific workflow run ID |
| pr_number | integer | No | PR number to find failed runs for |

## Procedure

### Step 1: Identify the Failed Workflow Run

If you have a PR number but not a run ID:

```bash
# List workflow runs for a PR
gh run list --repo OWNER/REPO --branch BRANCH_NAME --limit 10

# Get the most recent failed run
gh run list --repo OWNER/REPO --status failure --limit 5
```

### Step 2: Download the Workflow Logs

```bash
# Download logs for a specific run
gh run view RUN_ID --repo OWNER/REPO --log > ci.log

# Download logs with failed steps only
gh run view RUN_ID --repo OWNER/REPO --log-failed > ci-failed.log
```

### Step 3: Extract Relevant Sections

If logs are large, extract the failure sections:

```bash
# Find the failing step
grep -n "##\[error\]" ci.log

# Extract context around errors (20 lines before and after)
grep -B 20 -A 20 "##\[error\]" ci.log > ci-errors.log
```

### Step 4: Save Logs for Analysis

Store the logs in a predictable location for the diagnostic script:

```bash
# Create logs directory if needed
mkdir -p .ci-logs

# Save with timestamp
cp ci.log .ci-logs/ci-$(date +%Y%m%d-%H%M%S).log
```

## Output

| Output | Type | Description |
|--------|------|-------------|
| ci.log | file | Complete workflow log file |
| ci-failed.log | file | Log containing only failed steps |
| ci-errors.log | file | Extracted error sections with context |

## Verification

Verify logs were collected successfully:

```bash
# Check log file exists and has content
test -s ci.log && echo "Log collected successfully" || echo "Log collection failed"

# Verify it contains GitHub Actions markers
grep -q "##\[group\]" ci.log && echo "Valid GitHub Actions log"
```

## Error Handling

### Authentication failure

If `gh` authentication fails:

```bash
# Re-authenticate
gh auth login

# Verify authentication
gh auth status
```

### Run not found

If the run ID is invalid:

```bash
# List recent runs to find the correct ID
gh run list --repo OWNER/REPO --limit 20
```

### Permission denied

Ensure your token has `actions:read` scope:

```bash
gh auth refresh --scopes actions:read
```

## Next Operation

After collecting logs, proceed to:
- [op-run-diagnostic-script.md](op-run-diagnostic-script.md) - Analyze logs with diagnostic script
