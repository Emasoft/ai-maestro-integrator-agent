---
name: amia-kanban-orchestration
description: "Use when managing GitHub Kanban boards. Trigger with board state, card move, or completion requests."
license: Apache-2.0
compatibility: "Requires GitHub CLI authentication, GitHub Projects V2 enabled repository, GraphQL API access, Python 3.8+. Requires AI Maestro installed."
metadata:
  author: Emasoft
  version: 1.0.0
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Kanban Core

## Overview

GitHub Projects V2 Kanban is the single source of truth for AMOA orchestration. Every module = 1 issue, every assignment = 1 assignee, every status = 1 column move. If it's not on the board, it doesn't exist.

## Prerequisites

- GitHub CLI installed and authenticated (`gh auth status`)
- GitHub Projects V2 enabled for the repository
- GraphQL API access available
- Python 3.8+ for board management scripts
- AI Maestro installed for agent notifications

## Instructions

1. **Initialize** - Verify `gh auth status` and Projects V2 access
2. **Query state** - Run `amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER`
3. **Create issues** - 1 issue per module, following `references/issue-to-module-mapping.md`
4. **Assign work** - Set issue assignees per `references/agent-assignment-via-board.md`
5. **Track transitions** - Move cards per `references/status-transitions.md`
6. **Handle blockers** - Move to Blocked with `--reason` per `references/blocking-workflow.md`
7. **Verify completion** - Run `amia_kanban_check_completion.py` (exit 0 = all done)

### Checklist

- [ ] `gh auth status` passes
- [ ] Projects V2 access verified
- [ ] Board state queried successfully
- [ ] Module issues created (1 issue = 1 module)
- [ ] Issues added to board in Backlog column
- [ ] Ready issues moved Backlog -> Todo -> In Progress
- [ ] Agents assigned via issue assignees
- [ ] PRs linked to issues, moved to AI Review
- [ ] Blockers handled with reason
- [ ] Completion verified (exit code 0)

## Output

| Output | Format | Script |
|--------|--------|--------|
| Board State | JSON (items by column) | `amia_kanban_get_board_state.py` |
| Transition Result | JSON (success/fail + validation) | `amia_kanban_move_card.py` |
| Completion Status | Exit code: 0=done, 1=pending, 2=blocked | `amia_kanban_check_completion.py` |

> **Output discipline:** All scripts support `--output-file <path>`. Use it from agents to minimize tokens.

## Reference Documents

**Core Concepts:**

- `references/kanban-as-truth.md` -- Why Kanban is single source of truth
- `references/board-column-semantics.md` -- Column meanings and requirements
- `references/issue-to-module-mapping.md` -- Module-to-issue 1:1 mapping
- `references/status-transitions.md` -- Valid state transitions matrix

**Workflows:**

- `references/agent-assignment-via-board.md` -- Assignment via issue assignees
- `references/blocking-workflow.md` -- Handling blocked items
- `references/ai-agent-vs-human-workflow.md` -- AI vs human workflow differences
- `references/proactive-kanban-monitoring.md` -- Board polling and change detection

**Integration:**

- `references/integration-points.md` -- Planning, orchestration, stop hooks, PRs
- `references/stop-hook-integration.md` -- Stop hook completion checks
- `references/instruction-templates.md` -- Message and assignment templates
- `references/failure-scenarios.md` -- Failure handling and recovery

**Operations:**

- `references/board-queries.md` -- GraphQL queries for board state
- `references/troubleshooting.md` -- Common issues and solutions
- `references/detailed-guide.md` -- Full board columns, error handling, command integration details

## Examples

### Example: Move Card and Check Completion

```bash
# Get board state
python3 scripts/amia_kanban_get_board_state.py owner repo 1

# Move issue #42 to In Progress
python3 scripts/amia_kanban_move_card.py owner repo 1 42 in-progress --reason "Starting work"

# Verify all items complete
python3 scripts/amia_kanban_check_completion.py owner repo 1
# Exit: 0=all done, 1=pending, 2=blocked
```
