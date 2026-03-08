# Operation: Detect State Triggers

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Parse user prompt for indicators](#step-1-parse-user-prompt-for-indicators)
  - [Step 2: Extract identifiers](#step-2-extract-identifiers)
  - [Step 3: Determine trigger type](#step-3-determine-trigger-type)
  - [Step 4: Check for existing memory](#step-4-check-for-existing-memory)
  - [Step 5: Return trigger analysis](#step-5-return-trigger-analysis)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Trigger Types](#trigger-types)
- [Recommended Actions](#recommended-actions)
- [Error Handling](#error-handling)
  - [Cannot parse user prompt](#cannot-parse-user-prompt)
  - [GitHub access fails](#github-access-fails)
  - [Multiple triggers detected](#multiple-triggers-detected)
- [Verification](#verification)

## Purpose

Analyze the user prompt and context at session start to determine what type of work is being resumed and what memory should be loaded.

## When to Use

- At the very start of every AMIA session
- When receiving a new task from orchestrator
- When context is unclear and memory state is needed

## Prerequisites

1. User prompt or task description available
2. Access to handoff directory for state files
3. GitHub CLI for PR/issue lookup

## Procedure

### Step 1: Parse user prompt for indicators

Look for these trigger patterns in the user message:

```
PR-related triggers:
- "PR #123", "pull request 123", "#123"
- "review", "approve", "merge"
- GitHub PR URL pattern

Issue-related triggers:
- "issue #456", "#456"
- "bug", "fix", "implement"
- GitHub issue URL pattern

Release triggers:
- "release", "version", "deploy"
- "v1.2.3", "1.2.3"
- "rollback", "revert"

Integration triggers:
- "CI", "pipeline", "workflow"
- "failing", "broken", "build"
```

### Step 2: Extract identifiers

```bash
# Extract PR number from prompt
PR_NUM=$(echo "$USER_PROMPT" | grep -oP '(?:PR|pull request)\s*#?(\d+)' | grep -oP '\d+' | head -1)

# Extract issue number
ISSUE_NUM=$(echo "$USER_PROMPT" | grep -oP '(?:issue)\s*#?(\d+)' | grep -oP '\d+' | head -1)

# Extract GitHub URL
GH_URL=$(echo "$USER_PROMPT" | grep -oP 'https://github.com/[^\s]+')
```

### Step 3: Determine trigger type

```bash
TRIGGER_TYPE="unknown"

if [ -n "$PR_NUM" ] || echo "$USER_PROMPT" | grep -qi "pull request\|PR\|review\|merge"; then
  TRIGGER_TYPE="pr_review"
elif [ -n "$ISSUE_NUM" ] || echo "$USER_PROMPT" | grep -qi "issue\|bug\|fix"; then
  TRIGGER_TYPE="issue_work"
elif echo "$USER_PROMPT" | grep -qi "release\|version\|deploy\|rollback"; then
  TRIGGER_TYPE="release"
elif echo "$USER_PROMPT" | grep -qi "CI\|pipeline\|workflow\|build"; then
  TRIGGER_TYPE="ci_integration"
else
  TRIGGER_TYPE="general"
fi

echo "Detected trigger type: $TRIGGER_TYPE"
```

### Step 4: Check for existing memory

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"

# Check for session state
if [ -f "$HANDOFF_DIR/current.md" ]; then
  echo "Found existing handoff document"
  HAS_HANDOFF=true
fi

# Check for PR-specific state
if [ -n "$PR_NUM" ]; then
  PR_STATE=$(gh pr view "$PR_NUM" --comments --json comments | jq -r '
    .comments[] | select(.body | contains("AMIA-SESSION-STATE")) | .body
  ' 2>/dev/null)
  if [ -n "$PR_STATE" ]; then
    echo "Found PR-specific state"
    HAS_PR_STATE=true
  fi
fi
```

### Step 5: Return trigger analysis

```json
{
  "trigger_type": "pr_review",
  "identifiers": {
    "pr_number": 123,
    "issue_number": null,
    "github_url": "https://github.com/owner/repo/pull/123"
  },
  "memory_sources": {
    "has_handoff": true,
    "has_pr_state": true,
    "has_release_history": false
  },
  "recommended_action": "load_pr_memory"
}
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_prompt | string | yes | The user message or task description |
| check_memory | boolean | no | Whether to check for existing memory |

## Output

| Field | Type | Description |
|-------|------|-------------|
| trigger_type | string | Type of work detected |
| identifiers | object | Extracted PR/issue numbers, URLs |
| memory_sources | object | What memory sources exist |
| recommended_action | string | What to do next |

## Example Output

```json
{
  "trigger_type": "pr_review",
  "identifiers": {
    "pr_number": 123,
    "issue_number": null,
    "github_url": null
  },
  "memory_sources": {
    "has_handoff": true,
    "has_pr_state": false,
    "has_release_history": false
  },
  "recommended_action": "load_handoff_then_pr"
}
```

## Trigger Types

| Type | Keywords | Memory to Load |
|------|----------|----------------|
| `pr_review` | PR, pull request, review, merge | PR comment state, handoff |
| `issue_work` | issue, bug, fix, implement | Issue state, handoff |
| `release` | release, version, deploy, rollback | Release history, handoff |
| `ci_integration` | CI, pipeline, workflow, build | CI state, handoff |
| `general` | None matched | Handoff only |

## Recommended Actions

| Condition | Recommended Action |
|-----------|-------------------|
| PR detected + PR state exists | `load_pr_memory` |
| PR detected + no PR state | `start_fresh_pr` |
| Issue detected + handoff exists | `load_handoff_then_issue` |
| Release detected | `load_release_history` |
| No triggers + handoff exists | `load_handoff` |
| No triggers + no memory | `start_fresh` |

## Error Handling

### Cannot parse user prompt

**Cause**: Prompt is empty or unparseable.

**Solution**: Ask for clarification about the task.

### GitHub access fails

**Cause**: Cannot access PR/issue data.

**Solution**: Proceed without PR-specific memory, use handoff only.

### Multiple triggers detected

**Cause**: Prompt contains multiple work types.

**Solution**: Prioritize by order: PR > Issue > Release > CI > General.

## Verification

After detecting triggers:

```bash
# Log detected triggers
echo "Trigger Type: $TRIGGER_TYPE"
echo "PR Number: ${PR_NUM:-none}"
echo "Issue Number: ${ISSUE_NUM:-none}"
echo "Has Handoff: ${HAS_HANDOFF:-false}"
echo "Has PR State: ${HAS_PR_STATE:-false}"

# Proceed to appropriate memory loading
case "$TRIGGER_TYPE" in
  pr_review)
    # Use op-load-pr-memory
    ;;
  release)
    # Use op-load-release-history
    ;;
  *)
    # Use op-load-handoff-docs
    ;;
esac
```
