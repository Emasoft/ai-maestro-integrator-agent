---
name: op-execute-rollback
description: "Roll back to a previous version after release failure"
procedure: support-skill
workflow-instruction: support
---

# Operation: Execute Rollback


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify versions](#step-1-identify-versions)
  - [Step 2: Verify target version exists](#step-2-verify-target-version-exists)
  - [Step 3: Document rollback decision](#step-3-document-rollback-decision)
- [Impact Assessment](#impact-assessment)
- [Actions Taken](#actions-taken)
  - [Step 4: Mark bad release as deprecated (GitHub)](#step-4-mark-bad-release-as-deprecated-github)
  - [Step 5: Handle package registry (npm)](#step-5-handle-package-registry-npm)
  - [Step 6: Handle package registry (PyPI)](#step-6-handle-package-registry-pypi)
  - [Step 7: Create rollback issue](#step-7-create-rollback-issue)
- [Actions Taken](#actions-taken)
- [Root Cause](#root-cause)
- [Prevention](#prevention)
  - [Step 8: Notify stakeholders](#step-8-notify-stakeholders)
  - [Step 9: Verify rollback success](#step-9-verify-rollback-success)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [CRITICAL: User Approval Required](#critical-user-approval-required)
- [Error Handling](#error-handling)
  - [Target version not found](#target-version-not-found)
  - [GitHub release edit fails](#github-release-edit-fails)
  - [npm deprecation fails](#npm-deprecation-fails)
- [Complete Rollback Script](#complete-rollback-script)
- [Verification](#verification)

## Purpose

Revert to a previous stable version when a release causes critical issues, including deprecating the bad release and restoring the previous state.

## When to Use

- When post-release verification fails
- When critical bugs are discovered after release
- When user reports critical regression
- When deployment causes production issues

## Prerequisites

1. GitHub CLI authenticated with release permissions
2. Knowledge of which version to roll back to
3. Understanding of rollback impact
4. USER APPROVAL (required before execution)

## Procedure

### Step 1: Identify versions

```bash
ROLLBACK_FROM="1.2.4"
ROLLBACK_TO="1.2.3"
REASON="Critical regression in API endpoint"

echo "Rolling back from v$ROLLBACK_FROM to v$ROLLBACK_TO"
echo "Reason: $REASON"
```

### Step 2: Verify target version exists

```bash
# Check tag exists
if ! git rev-parse "v$ROLLBACK_TO" >/dev/null 2>&1; then
  echo "ERROR: Tag v$ROLLBACK_TO does not exist"
  exit 1
fi

# Check release exists on GitHub
if ! gh release view "v$ROLLBACK_TO" >/dev/null 2>&1; then
  echo "ERROR: Release v$ROLLBACK_TO not found on GitHub"
  exit 1
fi

echo "Target version v$ROLLBACK_TO verified"
```

### Step 3: Document rollback decision

```bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

ROLLBACK_DOC="# Rollback Report

**Date**: $TIMESTAMP
**From Version**: v$ROLLBACK_FROM
**To Version**: v$ROLLBACK_TO
**Reason**: $REASON

## Impact Assessment

- Users on v$ROLLBACK_FROM will need to update
- Any data changes since $ROLLBACK_FROM may need migration

## Actions Taken

(To be filled during rollback)
"

echo "$ROLLBACK_DOC" > rollback_report_$TIMESTAMP.md
```

### Step 4: Mark bad release as deprecated (GitHub)

```bash
# Edit release to mark as deprecated
gh release edit "v$ROLLBACK_FROM" \
  --title "[DEPRECATED] v$ROLLBACK_FROM" \
  --notes "**DEPRECATED**: This release has been rolled back due to: $REASON

Please use v$ROLLBACK_TO instead.

Original release notes:
$(gh release view "v$ROLLBACK_FROM" --json body --jq '.body')
"

echo "Release v$ROLLBACK_FROM marked as deprecated"
```

### Step 5: Handle package registry (npm)

```bash
# For npm packages
if [ -f "package.json" ]; then
  # Deprecate the bad version
  npm deprecate "$(jq -r '.name' package.json)@$ROLLBACK_FROM" \
    "Deprecated due to critical issue. Use $ROLLBACK_TO instead."

  echo "npm package v$ROLLBACK_FROM deprecated"
fi
```

### Step 6: Handle package registry (PyPI)

```bash
# For Python packages - PyPI doesn't support deprecation
# Create an issue/notice instead
if [ -f "pyproject.toml" ]; then
  echo "Note: PyPI does not support version deprecation"
  echo "Consider yanking via PyPI web interface if necessary"
fi
```

### Step 7: Create rollback issue

```bash
ISSUE_BODY="## Rollback Summary

**From**: v$ROLLBACK_FROM
**To**: v$ROLLBACK_TO
**Reason**: $REASON
**Date**: $TIMESTAMP

## Actions Taken

- [x] Marked v$ROLLBACK_FROM as deprecated on GitHub
- [x] Deprecated npm package (if applicable)
- [ ] Verify users are notified
- [ ] Root cause analysis
- [ ] Fix for next release

## Root Cause

(To be determined)

## Prevention

(Actions to prevent recurrence)
"

gh issue create \
  --title "[Rollback] v$ROLLBACK_FROM -> v$ROLLBACK_TO" \
  --body "$ISSUE_BODY" \
  --label "rollback,critical"

echo "Rollback issue created"
```

### Step 8: Notify stakeholders

Send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-eoa`
- **Subject**: `[ROLLBACK COMPLETE] v<ROLLBACK_FROM> -> v<ROLLBACK_TO>`
- **Priority**: `urgent`
- **Content**: `{"type": "rollback-complete", "message": "Rollback from v<ROLLBACK_FROM> to v<ROLLBACK_TO> completed. Reason: <REASON>"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Step 9: Verify rollback success

```bash
# Verify deprecated release
gh release view "v$ROLLBACK_FROM" --json name --jq '.name' | grep -q "DEPRECATED"

# Verify latest stable points to rollback target
LATEST_STABLE=$(gh release list --exclude-pre-releases --limit 1 --json tagName --jq '.[0].tagName')

echo "Latest stable release: $LATEST_STABLE"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| from_version | string | yes | Version to roll back from |
| to_version | string | yes | Version to roll back to |
| reason | string | yes | Reason for rollback |
| deprecate_npm | boolean | no | Whether to deprecate npm package |
| create_issue | boolean | no | Whether to create GitHub issue |

## Output

| Field | Type | Description |
|-------|------|-------------|
| rolled_back_from | string | Version rolled back from |
| rolled_back_to | string | Version rolled back to |
| status | string | success or failed |
| actions_taken | string[] | List of actions performed |
| issue_number | number | Created issue number |

## Example Output

```json
{
  "rolled_back_from": "v1.2.4",
  "rolled_back_to": "v1.2.3",
  "status": "success",
  "actions_taken": [
    "Deprecated GitHub release v1.2.4",
    "Deprecated npm package 1.2.4",
    "Created rollback issue #456"
  ],
  "issue_number": 456
}
```

## CRITICAL: User Approval Required

**NEVER execute rollback without explicit user approval.**

Before rollback, present:
1. Versions involved
2. Reason for rollback
3. Impact assessment
4. Actions that will be taken

Wait for user confirmation before proceeding.

## Error Handling

### Target version not found

**Cause**: Rollback target doesn't exist.

**Solution**: Verify version exists, check tag spelling.

### GitHub release edit fails

**Cause**: Permission or API issue.

**Solution**: Check permissions, retry.

### npm deprecation fails

**Cause**: Not logged in or no publish access.

**Solution**: Run `npm login` with publish credentials.

## Complete Rollback Script

```bash
#!/bin/bash
# execute_rollback.sh

FROM_VERSION="$1"
TO_VERSION="$2"
REASON="$3"

if [ -z "$FROM_VERSION" ] || [ -z "$TO_VERSION" ] || [ -z "$REASON" ]; then
  echo "Usage: execute_rollback.sh <from_version> <to_version> <reason>"
  exit 1
fi

echo "=== ROLLBACK EXECUTION ==="
echo "From: v$FROM_VERSION"
echo "To: v$TO_VERSION"
echo "Reason: $REASON"
echo ""
echo "This will:"
echo "  1. Mark v$FROM_VERSION as deprecated"
echo "  2. Deprecate npm package (if applicable)"
echo "  3. Create rollback issue"
echo ""
read -p "Proceed? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Rollback cancelled"
  exit 0
fi

ACTIONS=()

# Deprecate GitHub release
gh release edit "v$FROM_VERSION" --title "[DEPRECATED] v$FROM_VERSION"
ACTIONS+=("Deprecated GitHub release")

# Deprecate npm
if [ -f "package.json" ]; then
  PKG=$(jq -r '.name' package.json)
  npm deprecate "$PKG@$FROM_VERSION" "Deprecated. Use $TO_VERSION"
  ACTIONS+=("Deprecated npm package")
fi

# Create issue
gh issue create \
  --title "[Rollback] v$FROM_VERSION -> v$TO_VERSION" \
  --body "Rollback due to: $REASON" \
  --label "rollback"
ACTIONS+=("Created rollback issue")

echo ""
echo "=== ROLLBACK COMPLETE ==="
for a in "${ACTIONS[@]}"; do
  echo "  - $a"
done
```

## Verification

After rollback:

```bash
# Verify deprecation
gh release view "v$FROM_VERSION" --json name

# Verify npm deprecation
npm view <package>@$FROM_VERSION deprecated

# Verify issue created
gh issue list --label "rollback" --limit 1
```
