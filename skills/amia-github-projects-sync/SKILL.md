---
name: amia-github-projects-sync
description: Use when managing team tasks through GitHub Projects V2 or synchronizing project state via GraphQL API. Trigger with /sync-projects or when updating project items.
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

Manages team tasks through GitHub Projects V2 via GraphQL API. This is the official task management interface for coordinating work across remote developer agents. READ + STATUS UPDATE ONLY — never executes code or modifies source files.

## Prerequisites

- GitHub CLI (`gh`) authenticated with `project` scope
- GitHub Projects V2 enabled repository
- GraphQL API access
- Python 3.8+ for automation scripts

## Instructions

1. **Identify task type** — create, update, query, or sync GitHub Projects data
2. **Authenticate** — verify with `gh auth status` (needs `project` scope)
3. **Locate project** — find project ID via GraphQL query (see Examples)
4. **Select operation** — consult Reference Documents for the matching use case
5. **Execute** — use `gh api graphql` or run automation scripts
6. **Verify** — check project board or query API to confirm changes
7. **Notify** — send AI Maestro messages to relevant agents if needed

### Checklist

Copy this checklist and track your progress:

- [ ] Identify task type (create/update/query/sync)
- [ ] Verify GitHub CLI auth with `project` scope
- [ ] Locate project using GraphQL queries
- [ ] Select operation from reference documentation
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

**Core Operations:**

- `references/core-operations.md` — day-to-day project operations (create, update, query, link, comment)
- `references/graphql-queries.md` — complete GraphQL query/mutation reference
- `references/graphql-queries-part1-read-operations.md` — all read queries
- `references/graphql-queries-part2-mutations.md` — all mutations

**Status & Labels:**

- `references/status-management.md` — status transitions, lifecycle policy, reports
- `references/label-taxonomy.md` — label categories, creation, filtering, colors

**Templates & Tracking:**

- `references/issue-templates.md` — issue/PR templates for features, bugs, epics, refactoring
- `references/sub-issue-tracking.md` — parent/child issues, progress tracking

**Planning & Review:**

- `references/planning-phase-mapping.md` — planning phases to GitHub status mapping
- `references/iteration-cycle-rules.md` — sprint/iteration management, review flow
- `references/review-worktree-workflow.md` — isolated review environment setup
- `references/plan-file-linking.md` — GitHub issue to plan file linking

**Automation & Integration:**

- `references/automation-scripts.md` — sync_tasks.py, ci_webhook_handler.py, amia_kanban_sync.py
- `references/skill-integrations.md` — coordination with other AMOA skills
- `references/ci-notification-setup.md` — webhook configuration for CI/project sync
- `references/github-sync-procedure.md` — full sync procedure with external systems

**Troubleshooting:**

- `references/error-handling.md` — API errors, rate limits, retry logic, auth failures
- `references/best-practices.md` — dos, don'ts, lifecycle reminders
- `references/examples-and-inline-troubleshooting.md` — worked examples and common failure fixes
- `references/detailed-guide.md` — expanded guide with lifecycle policy, thresholds, AI Maestro integration

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

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

See `references/` directory for all reference documents.
