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

GitHub Projects V2 Kanban provides the display layer for task tracking. AI Maestro's task system (`backlog`, `pending`, `in_progress`, `review`, `completed`) is the authoritative status source. GitHub columns map onto these 5 statuses.

## Prerequisites

- GitHub CLI authenticated (`gh auth status`) with Projects V2 enabled
- GraphQL API access and Python 3.8+
- AI Maestro installed

## Instructions

1. **Initialize** - Verify `gh auth status` and Projects V2 access
2. **Query state** - Run `amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER`
3. **Create & assign** - 1 issue per module, set assignees, add to Backlog
4. **Track transitions** - Move cards through columns, handle blockers with `--reason`
5. **Verify completion** - Run `amia_kanban_check_completion.py` (exit 0 = all done)

### Checklist

Copy this checklist and track your progress:

- [ ] `gh auth status` passes and Projects V2 verified
- [ ] Board state queried successfully
- [ ] Module issues created and added to Backlog
- [ ] Issues moved Backlog -> Todo -> In Progress
- [ ] Agents assigned via issue assignees
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

See `references/` directory for all reference documents.

## Error Handling

Check exit code and stderr: 1=invalid params, 2-4=GitHub API errors. See the detailed guide in Resources.

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - The Iron Rule
  - Board Columns Quick Reference
  - Command Integration: /create-issue-tasks
  - Python Scripts Detailed Usage
  - Error Handling
  - Integration Points Summary
  - Proactive Kanban Monitoring Summary
  - Skill File Structure
  - Related Skills

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
