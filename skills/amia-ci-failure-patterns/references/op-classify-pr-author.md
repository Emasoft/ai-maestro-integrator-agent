# Operation: Classify PR Author

## Table of Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Author Categories](#author-categories)
- [Procedure](#procedure)
  - [Step 1: Get PR Author Information](#step-1-get-pr-author-information)
  - [Step 2: Check Against Bot Patterns](#step-2-check-against-bot-patterns)
  - [Step 3: Classify the Author](#step-3-classify-the-author)
  - [Step 4: Apply Category-Specific Handling](#step-4-apply-category-specific-handling)
- [Output](#output)
- [Decision Matrix](#decision-matrix)
- [Reliability Interpretation](#reliability-interpretation)
  - [Agent-Controlled (100%)](#agent-controlled-100)
  - [Mention-Triggered (60-70%)](#mention-triggered-60-70)
  - [Human (Variable)](#human-variable)
- [Error Handling](#error-handling)
  - [Cannot determine author type](#cannot-determine-author-type)
  - [Unknown bot](#unknown-bot)
- [Integration with CI Failure Handling](#integration-with-ci-failure-handling)
- [See Also](#see-also)

## Purpose

This operation classifies the author of a Pull Request into categories that determine how automated CI failure handling should proceed. Different author categories have different reliability expectations for automated fixes.

## Prerequisites

- Access to PR metadata via GitHub CLI or API
- PR number or author username

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes* | PR number to classify |
| author | string | Yes* | Author username to classify |

*Either pr_number or author is required.

## Author Categories

| Category | Description | Examples | Auto-Fix Reliability |
|----------|-------------|----------|---------------------|
| agent-controlled | Fully automated agents that respond to commands | claude[bot], dependabot[bot], renovate[bot] | 100% |
| mention-triggered | Bots that respond to @mentions | claude (via @claude), copilot | 60-70% |
| human | Human contributors | Any non-bot username | Variable |

## Procedure

### Step 1: Get PR Author Information

```bash
# Get author username from PR
gh pr view <pr_number> --json author -q '.author.login'

# Get author type (User or Bot)
gh api repos/{owner}/{repo}/pulls/<pr_number> --jq '.user.type'
```

### Step 2: Check Against Bot Patterns

**Agent-Controlled Bots (100% reliability):**

```bash
# These respond programmatically to all commands
AGENT_BOTS=(
  "claude[bot]"
  "dependabot[bot]"
  "renovate[bot]"
  "github-actions[bot]"
  "codecov[bot]"
  "snyk-bot"
)
```

**Mention-Triggered Bots (60-70% reliability):**

```bash
# These respond to @mentions but may not always act
MENTION_BOTS=(
  "claude"           # Responds to @claude mentions
  "copilot"          # GitHub Copilot suggestions
  "coderabbit"       # Code review bot
)
```

### Step 3: Classify the Author

```bash
#!/bin/bash
# classify_author.sh

AUTHOR=$(gh pr view $1 --json author -q '.author.login')
USER_TYPE=$(gh api repos/{owner}/{repo}/pulls/$1 --jq '.user.type')

# Check if Bot account type
if [ "$USER_TYPE" = "Bot" ]; then
  # Check for agent-controlled patterns
  if [[ "$AUTHOR" =~ \[bot\]$ ]] || [[ "$AUTHOR" =~ -bot$ ]]; then
    echo "agent-controlled"
    exit 0
  fi
fi

# Check for mention-triggered bots
MENTION_BOTS="claude copilot coderabbit"
if echo "$MENTION_BOTS" | grep -qw "$AUTHOR"; then
  echo "mention-triggered"
  exit 0
fi

# Default to human
echo "human"
```

### Step 4: Apply Category-Specific Handling

| Category | CI Failure Response |
|----------|---------------------|
| agent-controlled | Automatically request fix via API/command |
| mention-triggered | Post @mention with fix request, wait for response |
| human | Notify author, provide diagnostic information |

#### For Agent-Controlled PRs

```bash
# Dependabot: Trigger rebase
gh pr comment <pr_number> --body "@dependabot rebase"

# Renovate: Request update
gh pr comment <pr_number> --body "renovate: rebase"
```

#### For Mention-Triggered PRs

```bash
# Claude: Request fix via @mention
gh pr comment <pr_number> --body "@claude The CI is failing due to <pattern>. Please fix <specific-issue>."
```

#### For Human PRs

```bash
# Notify with helpful information
gh pr comment <pr_number> --body "CI failure detected: <pattern-category>

**Issue**: <description>
**Suggested Fix**: <fix-description>
**Reference**: See amia-ci-failure-patterns skill documentation

Would you like me to explain the fix in more detail?"
```

## Output

| Output | Type | Description |
|--------|------|-------------|
| category | string | agent-controlled, mention-triggered, or human |
| author | string | Author username |
| reliability | string | Expected response reliability |
| recommended_action | string | How to handle CI failure |

## Decision Matrix

| Category | Auto-Fix? | Notification Style | Wait Time |
|----------|-----------|-------------------|-----------|
| agent-controlled | Yes | Command | 5-10 min |
| mention-triggered | Partial | @mention request | 10-30 min |
| human | No | Informative comment | Variable |

## Reliability Interpretation

### Agent-Controlled (100%)

- Bot will always attempt to execute the requested action
- Action may still fail due to technical limitations
- Safe to automate retry loops

### Mention-Triggered (60-70%)

- Bot may or may not respond to the mention
- Response depends on bot configuration and context
- Use single attempt, then escalate to human

### Human (Variable)

- Response time and action depend on individual
- Provide all information needed for self-service fix
- Consider automated follow-up after timeout

## Error Handling

### Cannot determine author type

If the GitHub API doesn't return author type:

```bash
# Fallback to pattern matching on username
if [[ "$AUTHOR" =~ bot ]] || [[ "$AUTHOR" =~ Bot ]]; then
  echo "Likely bot - classify based on name pattern"
fi
```

### Unknown bot

If bot is not in known lists:

```bash
# Check bot's recent behavior
gh api repos/{owner}/{repo}/pulls --jq '[.[] | select(.user.login=="'$AUTHOR'")] | length'

# If many PRs from this bot, likely automated
# Add to appropriate category list
```

## Integration with CI Failure Handling

This classification informs the overall handling strategy:

```
CI Failure Detected
       |
       v
Classify PR Author
       |
       +---> agent-controlled --> Auto-request fix
       |
       +---> mention-triggered --> @mention with details
       |
       +---> human --> Informative comment + wait
```

## See Also

- [bot-categories.md](bot-categories.md) - Detailed bot category reference
- [claude-pr-handling.md](claude-pr-handling.md) - Claude-specific PR handling
