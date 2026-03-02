# Single-Account GitHub Workflow

## Overview

Use this workflow when you have only ONE GitHub account but want to track AI agent assignments.

## Setup

1. All issues assigned to you (repository owner)
2. Track agents with labels: `assign:{agent-id}`

## Label Taxonomy

| Label | Description |
|-------|-------------|
| `assign:implementer-1` | First implementer agent |
| `assign:implementer-2` | Second implementer agent |
| `assign:code-reviewer` | Code review agent |
| `assign:orchestrator` | Orchestrator handling |
| `assign:human` | Human developer |

## Querying Assignments

```bash
# Find all issues for agent-1
gh issue list --label "assign:implementer-1"

# Find blocked items for agent-1
gh issue list --label "assign:implementer-1" --label "status:blocked"
```

## Kanban Board

Your kanban board will show:
- All items assigned to you (GitHub assignee)
- Agent differentiation via `assign:*` labels
- Use board filters on labels to see per-agent view

## Comparison with Multi-Account

| Aspect | Single-Account | Multi-Account |
|--------|----------------|---------------|
| Setup complexity | Low | High (SSH keys, identity switching) |
| Visual differentiation | Labels | Assignee avatars |
| Query method | Filter by label | Filter by assignee |
| PR authorship | All under your name | Per-agent names |
| Best for | Solo developers | Teams |
