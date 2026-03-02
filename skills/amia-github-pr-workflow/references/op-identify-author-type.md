# Operation: Identify PR Author Type


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Output](#output)
- [Handling Rules](#handling-rules)
  - [Human PRs](#human-prs)
  - [AI/Bot PRs](#aibot-prs)
- [Error Handling](#error-handling)
- [Example](#example)
- [Critical Rule](#critical-rule)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-identify-author-type
---

## Purpose

Determine if a PR is from a human contributor or an AI/bot, as this affects handling rules.

## When to Use

- Before taking any action on a PR
- When deciding whether to delegate directly or escalate
- When choosing communication style

## Prerequisites

- PR number known
- GitHub CLI (`gh`) authenticated
- Access to repository

## Steps

1. **Get PR author information**:
   ```bash
   gh pr view <PR_NUMBER> --json author,authorAssociation --jq '.author.login, .authorAssociation'
   ```

2. **Check author patterns**:

   | Pattern | Author Type |
   |---------|-------------|
   | `[bot]` suffix | Bot |
   | `dependabot`, `renovate`, `github-actions` | Bot |
   | Known AI agent names | AI Agent |
   | Other usernames | Human |

3. **Check authorAssociation**:

   | Association | Likely Type |
   |-------------|-------------|
   | OWNER | Human (repo owner) |
   | MEMBER | Human (team member) |
   | CONTRIBUTOR | Human (external) |
   | FIRST_TIME_CONTRIBUTOR | Human (new) |
   | NONE | Could be either |

4. **Apply handling rules** based on type

## Output

| Field | Type | Description |
|-------|------|-------------|
| author_type | string | "human", "ai_agent", or "bot" |
| author_login | string | GitHub username |
| escalation_required | boolean | True for human PRs |

## Handling Rules

### Human PRs
- **Escalate to user** for guidance on communication
- **Never** modify without explicit approval
- **Polite, formal** communication style
- **Wait** for human response before proceeding

### AI/Bot PRs
- **Direct delegation** allowed
- Can modify without escalation
- **Technical, direct** communication style
- Can proceed autonomously within scope

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| PR not found | Invalid number | Verify PR exists |
| Unknown author | New account | Treat as human (safer) |

## Example

```bash
# Get author info
gh pr view 123 --json author,authorAssociation

# Output
{
  "author": {"login": "dependabot[bot]"},
  "authorAssociation": "NONE"
}
# Result: Bot PR - direct delegation allowed

# Human example
{
  "author": {"login": "john-developer"},
  "authorAssociation": "CONTRIBUTOR"
}
# Result: Human PR - escalation required
```

## Critical Rule

When in doubt, treat as human PR. Incorrectly treating a human as a bot can damage contributor relationships.
