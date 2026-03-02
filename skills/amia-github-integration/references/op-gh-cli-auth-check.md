---
name: op-gh-cli-auth-check
description: "Verify GitHub CLI authentication status"
procedure: support-skill
workflow-instruction: support
---

# Operation: GitHub CLI Authentication Check


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Check authentication status](#step-1-check-authentication-status)
  - [Step 2: Verify required scopes](#step-2-verify-required-scopes)
  - [Step 3: Test API access](#step-3-test-api-access)
  - [Step 4: Verify repository access](#step-4-verify-repository-access)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Error Handling](#error-handling)
  - [Not logged in](#not-logged-in)
  - [Token expired](#token-expired)
  - [Insufficient scopes](#insufficient-scopes)
  - [Wrong account](#wrong-account)
- [Verification](#verification)
- [Related Operations](#related-operations)

## Purpose

Verify that the GitHub CLI is properly authenticated before performing any GitHub operations.

## When to Use

- At the start of any GitHub integration workflow
- Before executing batch operations
- When encountering authentication errors
- When switching between GitHub accounts

## Prerequisites

1. GitHub CLI installed (`gh` command available)

## Procedure

### Step 1: Check authentication status

```bash
gh auth status
```

Expected successful output:
```
github.com
  Logged in to github.com as USERNAME
  Token valid until EXPIRY_DATE
  Token scopes: gist, read:org, repo, workflow
```

### Step 2: Verify required scopes

Check that the token has necessary permissions:

```bash
gh auth status --show-token 2>&1 | grep "Token scopes"
```

Required scopes for most operations:
- `repo` - Full repository access
- `read:org` - Read organization data
- `workflow` - Workflow permissions (for CI/CD)

### Step 3: Test API access

```bash
# Test basic API access
gh api user --jq '.login'
```

### Step 4: Verify repository access

```bash
# Test access to specific repository
gh repo view owner/repo --json name,viewerPermission --jq '{name, permission: .viewerPermission}'
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| repository | string | no | Specific repository to verify access |
| required_scopes | string[] | no | Scopes required for operation |

## Output

| Field | Type | Description |
|-------|------|-------------|
| authenticated | boolean | Whether authentication is valid |
| username | string | Logged in username |
| token_valid | boolean | Whether token is not expired |
| scopes | string[] | Token permission scopes |
| can_access_repo | boolean | Whether specified repo is accessible |

## Example Output

```json
{
  "authenticated": true,
  "username": "Emasoft",
  "token_valid": true,
  "scopes": ["gist", "read:org", "repo", "workflow"],
  "can_access_repo": true
}
```

## Error Handling

### Not logged in

**Symptom**: `You are not logged in to any GitHub hosts`

**Solution**:
```bash
gh auth login
```
Follow the interactive prompts to authenticate.

### Token expired

**Symptom**: `token has expired`

**Solution**:
```bash
gh auth refresh
```

### Insufficient scopes

**Symptom**: `Your token does not have the required scopes`

**Solution**:
```bash
gh auth refresh -s repo,read:org,workflow
```

### Wrong account

**Symptom**: Authenticated as different user than expected

**Solution**:
```bash
# Check current user
gh api user --jq '.login'

# Re-authenticate as different user
gh auth logout
gh auth login
```

## Verification

Complete authentication verification script:

```bash
#!/bin/bash
echo "=== GitHub CLI Authentication Check ==="

# Check if logged in
if ! gh auth status &>/dev/null; then
  echo "FAIL: Not authenticated"
  exit 1
fi

# Get username
USERNAME=$(gh api user --jq '.login')
echo "OK: Logged in as $USERNAME"

# Check token validity
if gh auth status 2>&1 | grep -q "Token valid"; then
  echo "OK: Token is valid"
else
  echo "WARN: Token status unclear"
fi

# Check scopes
SCOPES=$(gh auth status 2>&1 | grep "Token scopes" | cut -d: -f2)
echo "OK: Token scopes:$SCOPES"

echo "=== Check Complete ==="
```

## Related Operations

- After authentication check succeeds, proceed with:
  - `op-batch-label-add` - Bulk label operations
  - `op-batch-issue-filter` - Issue filtering
  - API operations in `api-operations.md`
