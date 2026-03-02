# Error Handling

## Table of Contents

1. [When encountering GitHub API errors](#overview)
2. [When hitting rate limits](#api-rate-limiting)
3. [When project or item is not found](#project-not-found)
4. [When item updates fail](#item-update-failed)
5. [When authentication fails](#authentication-errors)
6. [When webhook delivery fails](#webhook-errors)
7. [When implementing retry logic](#retry-patterns)

## Overview

This document covers error handling patterns for GitHub Projects V2 API operations. All scripts should implement proper error handling to ensure graceful degradation.

## API Rate Limiting

GitHub GraphQL API has rate limits. Check before operations.

### Check Rate Limit Status

```bash
gh api rate_limit | jq '.resources.graphql'
```

Output:
```json
{
  "limit": 5000,
  "remaining": 4892,
  "reset": 1705320000,
  "used": 108
}
```

### Rate Limit Handling Script

```bash
#!/bin/bash
# check-rate-limit.sh

RATE_INFO=$(gh api rate_limit | jq '.resources.graphql')
REMAINING=$(echo "$RATE_INFO" | jq '.remaining')
RESET_TIME=$(echo "$RATE_INFO" | jq '.reset')

if [ "$REMAINING" -lt 100 ]; then
  RESET_DATE=$(date -r "$RESET_TIME" "+%Y-%m-%d %H:%M:%S")
  echo "WARNING: Low rate limit remaining: $REMAINING"
  echo "Resets at: $RESET_DATE"

  if [ "$REMAINING" -lt 10 ]; then
    echo "ERROR: Rate limit critically low. Waiting for reset."
    WAIT_SECONDS=$((RESET_TIME - $(date +%s) + 5))
    if [ "$WAIT_SECONDS" -gt 0 ]; then
      sleep "$WAIT_SECONDS"
    fi
  fi
fi
```

### Exponential Backoff for Rate Limits

```bash
#!/bin/bash
# api-call-with-backoff.sh

MAX_RETRIES=5
RETRY_DELAY=1

for i in $(seq 1 $MAX_RETRIES); do
  RESULT=$(gh api graphql -f query="$QUERY" 2>&1)

  if echo "$RESULT" | grep -q "rate limit"; then
    echo "Rate limited. Retry $i/$MAX_RETRIES in ${RETRY_DELAY}s"
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
  else
    echo "$RESULT"
    exit 0
  fi
done

echo "ERROR: Max retries exceeded"
exit 1
```

## Project Not Found

When project ID is invalid or inaccessible.

### Detection

```bash
RESULT=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 { title }
    }
  }
' -f projectId="$PROJECT_ID" 2>&1)

if echo "$RESULT" | grep -q "NOT_FOUND\|Could not resolve"; then
  echo "ERROR: Project not found: $PROJECT_ID"
  # Handle error
fi
```

### Error Handling Protocol

```
1. VERIFY project exists:
   - Check project ID format (should start with "PVT_")
   - Query project to confirm access

2. VERIFY authentication scopes:
   - gh auth status
   - Ensure "project" scope is included

3. LOG error with details:
   - Project ID attempted
   - Error message
   - Timestamp

4. ESCALATE to user:
   - Report project not accessible
   - Request verification
```

### Verification Script

```bash
#!/bin/bash
# verify-project-access.sh PROJECT_ID

PROJECT_ID="$1"

# Check ID format
if [[ ! "$PROJECT_ID" =~ ^PVT_ ]]; then
  echo "ERROR: Invalid project ID format. Expected PVT_..."
  exit 1
fi

# Query project
RESULT=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        title
        closed
      }
    }
  }
' -f projectId="$PROJECT_ID" 2>&1)

if echo "$RESULT" | grep -q "error\|NOT_FOUND"; then
  echo "ERROR: Cannot access project"
  echo "Details: $RESULT"

  # Check auth
  echo ""
  echo "Checking authentication..."
  gh auth status
  exit 1
fi

TITLE=$(echo "$RESULT" | jq -r '.data.node.title')
CLOSED=$(echo "$RESULT" | jq -r '.data.node.closed')

echo "Project: $TITLE"
echo "Closed: $CLOSED"
```

## Item Update Failed

When updating project item status fails.

### Common Causes

| Error | Cause | Solution |
|-------|-------|----------|
| `UNPROCESSABLE` | Invalid field value | Check field type and allowed values |
| `NOT_FOUND` | Item not in project | Verify item belongs to project |
| `FORBIDDEN` | No write access | Check permissions |

### Retry Protocol

```
1. RETRY once after 5 seconds
2. IF still fails: LOG error with full context
3. ADD comment to issue manually (fallback)
4. CONTINUE with other operations
5. REPORT failure in sync summary
```

### Update with Fallback

```bash
#!/bin/bash
# update-with-fallback.sh

update_status() {
  PROJECT_ID="$1"
  ITEM_ID="$2"
  STATUS="$3"

  # First attempt
  RESULT=$(gh api graphql -f query='
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item { id }
      }
    }
  ' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID" 2>&1)

  if echo "$RESULT" | grep -q "error"; then
    echo "First attempt failed. Retrying in 5s..."
    sleep 5

    # Retry
    RESULT=$(gh api graphql -f query='...' 2>&1)

    if echo "$RESULT" | grep -q "error"; then
      echo "ERROR: Update failed after retry"
      echo "$RESULT"

      # Fallback: Add comment
      ISSUE=$(get_issue_number "$ITEM_ID")
      gh issue comment "$ISSUE" --body "⚠️ Status update failed. Intended: $STATUS"

      return 1
    fi
  fi

  return 0
}
```

## Authentication Errors

### Check Authentication

```bash
# Verify gh is authenticated
gh auth status

# Check scopes
gh auth status --show-token 2>&1 | grep -i scope
```

### Required Scopes

| Scope | Required For |
|-------|--------------|
| `repo` | Issue/PR operations |
| `project` | Projects V2 operations |
| `read:org` | Organization projects |

### Re-authenticate with Scopes

```bash
gh auth login --scopes "repo,project,read:org"
```

## Webhook Errors

See [ci-notification-setup.md](./ci-notification-setup.md#troubleshooting) for webhook-specific errors.

### Common Webhook Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Handler not running | Start webhook handler |
| Invalid signature | Secret mismatch | Verify GITHUB_WEBHOOK_SECRET |
| SSL verification failed | Certificate issue | Use valid SSL or ngrok |
| Timeout | Handler too slow | Optimize handler, increase timeout |

## Retry Patterns

### Simple Retry

```bash
retry() {
  local max_attempts=$1
  local delay=$2
  shift 2
  local cmd=("$@")

  for ((i=1; i<=max_attempts; i++)); do
    if "${cmd[@]}"; then
      return 0
    fi
    echo "Attempt $i failed. Retrying in ${delay}s..."
    sleep "$delay"
  done

  return 1
}

# Usage
retry 3 5 gh api graphql -f query="$QUERY"
```

### Exponential Backoff

```bash
retry_exponential() {
  local max_attempts=$1
  shift
  local cmd=("$@")
  local delay=1

  for ((i=1; i<=max_attempts; i++)); do
    if "${cmd[@]}"; then
      return 0
    fi
    echo "Attempt $i failed. Retrying in ${delay}s..."
    sleep "$delay"
    delay=$((delay * 2))
  done

  return 1
}

# Usage
retry_exponential 5 gh api graphql -f query="$QUERY"
```

### Circuit Breaker Pattern

```bash
# Track consecutive failures
FAILURE_COUNT=0
CIRCUIT_OPEN=false
CIRCUIT_RESET_TIME=0

api_call() {
  local now=$(date +%s)

  # Check if circuit is open
  if [ "$CIRCUIT_OPEN" = true ]; then
    if [ "$now" -lt "$CIRCUIT_RESET_TIME" ]; then
      echo "Circuit open. Skipping call."
      return 1
    fi
    # Reset circuit
    CIRCUIT_OPEN=false
    FAILURE_COUNT=0
  fi

  # Make call
  if gh api graphql -f query="$1"; then
    FAILURE_COUNT=0
    return 0
  fi

  # Handle failure
  FAILURE_COUNT=$((FAILURE_COUNT + 1))
  if [ "$FAILURE_COUNT" -ge 3 ]; then
    CIRCUIT_OPEN=true
    CIRCUIT_RESET_TIME=$((now + 60))  # Open for 60 seconds
    echo "Circuit opened due to consecutive failures"
  fi

  return 1
}
```
