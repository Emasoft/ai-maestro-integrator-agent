---
name: op-verify-memory-freshness
description: "Check timestamps and compare memory state with current GitHub state"
procedure: support-skill
workflow-instruction: support
---

# Operation: Verify Memory Freshness


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Extract memory timestamp](#step-1-extract-memory-timestamp)
  - [Step 2: Calculate memory age](#step-2-calculate-memory-age)
  - [Step 3: Check age thresholds](#step-3-check-age-thresholds)
  - [Step 4: Compare with GitHub state (for PR)](#step-4-compare-with-github-state-for-pr)
  - [Step 5: Compare with GitHub state (for release)](#step-5-compare-with-github-state-for-release)
  - [Step 6: Generate freshness report](#step-6-generate-freshness-report)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Freshness Levels](#freshness-levels)
- [Recommendations by Scenario](#recommendations-by-scenario)
- [Error Handling](#error-handling)
  - [Cannot parse timestamp](#cannot-parse-timestamp)
  - [GitHub API failure](#github-api-failure)
  - [No timestamp in memory](#no-timestamp-in-memory)
- [Verification Script](#verification-script)

## Purpose

Validate that loaded memory state is still accurate by comparing timestamps and checking for updates in the actual GitHub state (PRs, issues, releases).

## When to Use

- After loading any memory state
- Before relying on loaded state for decisions
- When memory is older than expected

## Prerequisites

1. Memory state loaded with timestamps
2. GitHub CLI authenticated
3. Access to relevant PR/issue/release data

## Procedure

### Step 1: Extract memory timestamp

```bash
# From session state
MEMORY_TS=$(echo "$SESSION_STATE" | jq -r '.last_updated // .started_at')

# From PR state
PR_STATE_TS=$(echo "$PR_STATE" | jq -r '.timestamp')

# From handoff
HANDOFF_TS=$(grep -oP '(?<=Last Updated: ).*' "$HANDOFF_DIR/current.md")
```

### Step 2: Calculate memory age

```bash
# Convert to epoch
MEMORY_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$MEMORY_TS" "+%s" 2>/dev/null || date -d "$MEMORY_TS" "+%s")
NOW_EPOCH=$(date "+%s")

# Calculate age
AGE_SECONDS=$((NOW_EPOCH - MEMORY_EPOCH))
AGE_HOURS=$((AGE_SECONDS / 3600))
AGE_DAYS=$((AGE_SECONDS / 86400))

echo "Memory age: $AGE_HOURS hours ($AGE_DAYS days)"
```

### Step 3: Check age thresholds

```bash
# Define freshness thresholds
FRESH_HOURS=24
STALE_DAYS=7

if [ $AGE_HOURS -lt $FRESH_HOURS ]; then
  FRESHNESS="fresh"
elif [ $AGE_DAYS -lt $STALE_DAYS ]; then
  FRESHNESS="aging"
else
  FRESHNESS="stale"
fi

echo "Freshness status: $FRESHNESS"
```

### Step 4: Compare with GitHub state (for PR)

```bash
if [ -n "$PR_NUMBER" ]; then
  # Get PR last update time
  PR_UPDATED=$(gh pr view "$PR_NUMBER" --json updatedAt --jq '.updatedAt')

  # Compare timestamps
  PR_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$PR_UPDATED" "+%s" 2>/dev/null || date -d "$PR_UPDATED" "+%s")

  if [ $PR_EPOCH -gt $MEMORY_EPOCH ]; then
    echo "WARNING: PR was updated after memory was saved"
    PR_CHANGED=true

    # Check what changed
    COMMITS_SINCE=$(gh pr view "$PR_NUMBER" --json commits --jq ".commits | map(select(.committedDate > \"$MEMORY_TS\")) | length")
    echo "Commits since memory: $COMMITS_SINCE"
  else
    PR_CHANGED=false
  fi
fi
```

### Step 5: Compare with GitHub state (for release)

```bash
if [ -n "$RELEASE_HISTORY" ]; then
  # Get latest GitHub release
  GH_LATEST=$(gh release list --limit 1 --json tagName,publishedAt --jq '.[0]')
  GH_TAG=$(echo "$GH_LATEST" | jq -r '.tagName')
  GH_DATE=$(echo "$GH_LATEST" | jq -r '.publishedAt')

  # Compare with memory
  MEMORY_LATEST=$(echo "$RELEASE_HISTORY" | jq -r '.latest_version')

  if [ "$GH_TAG" != "$MEMORY_LATEST" ]; then
    echo "WARNING: New release exists since memory was saved"
    echo "Memory: $MEMORY_LATEST, GitHub: $GH_TAG"
    RELEASES_CHANGED=true
  fi
fi
```

### Step 6: Generate freshness report

```json
{
  "memory_timestamp": "2025-02-04T15:42:00Z",
  "age_hours": 24,
  "age_days": 1,
  "freshness": "fresh",
  "github_changes": {
    "pr_updated": true,
    "commits_since": 2,
    "new_releases": false
  },
  "recommendation": "Verify PR changes before continuing"
}
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| memory_timestamp | string | yes | ISO 8601 timestamp from memory |
| pr_number | number | no | PR to compare against |
| check_releases | boolean | no | Whether to check release changes |
| fresh_threshold_hours | number | no | Hours to consider fresh (default: 24) |
| stale_threshold_days | number | no | Days to consider stale (default: 7) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| memory_timestamp | string | Original memory timestamp |
| age_hours | number | Age in hours |
| age_days | number | Age in days |
| freshness | string | fresh, aging, or stale |
| github_changes | object | Changes detected in GitHub |
| recommendation | string | Suggested action |

## Example Output

```json
{
  "memory_timestamp": "2025-02-04T15:42:00Z",
  "age_hours": 48,
  "age_days": 2,
  "freshness": "aging",
  "github_changes": {
    "pr_updated": true,
    "commits_since": 3,
    "comments_since": 1,
    "new_releases": false
  },
  "recommendation": "Re-review PR changes before continuing"
}
```

## Freshness Levels

| Level | Age | GitHub Changes | Action |
|-------|-----|----------------|--------|
| `fresh` | < 24h | None | Safe to use |
| `fresh` | < 24h | Yes | Review changes |
| `aging` | 1-7 days | None | Verify key state |
| `aging` | 1-7 days | Yes | Re-validate state |
| `stale` | > 7 days | Any | Discard, reload fresh |

## Recommendations by Scenario

| Scenario | Recommendation |
|----------|----------------|
| Fresh, no changes | Continue from memory |
| Fresh, PR updated | Check new commits before continuing |
| Aging, no changes | Verify current phase is still valid |
| Aging, changes | Re-validate state against GitHub |
| Stale | Archive old memory, start fresh |

## Error Handling

### Cannot parse timestamp

**Cause**: Memory timestamp is malformed.

**Solution**: Treat as stale, recommend fresh start.

### GitHub API failure

**Cause**: Cannot fetch GitHub state for comparison.

**Solution**: Rely on age-based freshness only.

### No timestamp in memory

**Cause**: Memory was saved without timestamp.

**Solution**: Treat as unknown age, recommend verification.

## Verification Script

```bash
#!/bin/bash
# verify_memory_freshness.sh

MEMORY_TS="$1"
PR_NUMBER="$2"

echo "=== Memory Freshness Verification ==="

# Calculate age
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Memory: $MEMORY_TS"
echo "Now: $NOW"

# Age calculation (simplified)
MEMORY_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$MEMORY_TS" "+%s" 2>/dev/null)
NOW_EPOCH=$(date "+%s")
AGE_HOURS=$(( (NOW_EPOCH - MEMORY_EPOCH) / 3600 ))

echo "Age: $AGE_HOURS hours"

# Freshness
if [ $AGE_HOURS -lt 24 ]; then
  echo "Status: FRESH"
elif [ $AGE_HOURS -lt 168 ]; then
  echo "Status: AGING"
else
  echo "Status: STALE"
fi

# GitHub comparison
if [ -n "$PR_NUMBER" ]; then
  PR_UPDATED=$(gh pr view "$PR_NUMBER" --json updatedAt --jq '.updatedAt')
  echo "PR last updated: $PR_UPDATED"

  if [[ "$PR_UPDATED" > "$MEMORY_TS" ]]; then
    echo "WARNING: PR updated since memory saved"
  else
    echo "OK: No PR changes since memory"
  fi
fi
```
