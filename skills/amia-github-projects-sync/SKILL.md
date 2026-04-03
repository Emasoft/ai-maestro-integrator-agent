---
name: amia-github-projects-sync
description: Use when managing team tasks through GitHub Projects V2 or synchronizing project state via GraphQL API. Trigger with /sync-projects or when updating project items. Loaded by ai-maestro-integrator-agent-main-agent.
license: Apache-2.0
compatibility: "Requires GitHub CLI authentication, GitHub Projects V2 enabled repository, GraphQL API access, Python 3.8+, and AI Maestro integration for notifications. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Projects Sync

## Overview

Manages team tasks through GitHub Projects V2 via GraphQL API — READ + STATUS UPDATE ONLY.

## Prerequisites

- GitHub CLI (`gh`) authenticated with `project` scope
- GitHub Projects V2 enabled repository
- Python 3.8+ for automation scripts

## Instructions

1. **Authenticate** — verify with `gh auth status` (needs `project` scope)
2. **Locate project** — find project ID via GraphQL query (see Examples)
3. **Execute** — use `gh api graphql` or run automation scripts
4. **Verify** — check project board or query API to confirm changes
5. **Notify** — send AI Maestro messages to relevant agents if needed

### Checklist

Copy this checklist and track your progress:

- [ ] Verify GitHub CLI auth with `project` scope
- [ ] Locate project using GraphQL queries
- [ ] Execute via GraphQL API or automation scripts
- [ ] Verify result on project board or via API
- [ ] Notify stakeholders via AI Maestro if needed
- [ ] Document change in issue comments or task lists

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Project item IDs | JSON | GraphQL node IDs for created/updated items |
| Status updates | JSON | Confirmation of field value changes |
| Issue metadata | JSON | Issue numbers, titles, states, assignees |
| Project reports | Markdown | Status summaries, progress updates |
| Sync logs | Text/JSON | Automation script execution results |
| Error details | JSON/Text | API errors, validation failures, rate limits |

> **Output discipline:** All scripts support `--output-file <path>`. Use it in automated workflows to minimize token consumption.

## Reference Documents

See `references/` directory for all reference documents.

## Error Handling

Script failures return non-zero exit codes. See [error-handling](references/error-handling.md) for details:
  - When encountering GitHub API errors
  - When hitting rate limits
  - When project or item is not found
  - When item updates fail
  - When authentication fails
  - When webhook delivery fails
  - When implementing retry logic

## Examples

### Example 1: Find Your Project

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      projectsV2(first: 10) {
        nodes { id title number }
      }
    }
  }
'
```

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Critical Distinction
  - When to Invoke
  - Iron Rules Compliance
  - Issue Lifecycle Policy
  - AI Maestro Integration
  - Threshold Configuration
  - Error Handling Details
  - Status Columns
  - Reference File Contents Index
