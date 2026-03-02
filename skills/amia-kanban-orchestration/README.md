# GitHub Kanban Core

**THE SINGLE SOURCE OF TRUTH for AMOA orchestration.**

## Overview

This skill establishes GitHub Projects V2 Kanban as the absolute center of AMOA orchestration. All planning, tracking, assignment, and completion verification flows through the Kanban board.

**The Iron Rule:** If it's not on the board, it doesn't exist. If the board says "In Progress", it IS in progress.

## Key Principles

1. **Every module = 1 GitHub Issue** on the board
2. **Every agent assignment = 1 Issue assignee**
3. **Every status change = 1 board column move**
4. **The orchestrator NEVER tracks work outside the board**

## Directory Structure

```
github-kanban-core/
├── SKILL.md                              # Main skill file with TOC
├── README.md                             # This file
├── scripts/
│   ├── amia_kanban_get_board_state.py         # Get full board state
│   ├── amia_kanban_move_card.py               # Move card between columns
│   └── amia_kanban_check_completion.py        # Check completion for stop hook
└── references/
    ├── kanban-as-truth.md                # Why Kanban is single source of truth
    ├── board-column-semantics.md         # Column meanings and requirements
    ├── issue-to-module-mapping.md        # Module-to-issue 1:1 mapping
    ├── agent-assignment-via-board.md     # Assignment via issue assignees
    ├── status-transitions.md             # Valid state transitions
    ├── blocking-workflow.md              # Handling blocked items
    ├── board-queries.md                  # GraphQL queries for board state
    ├── stop-hook-integration.md          # Stop hook completion checks
    ├── ai-agent-vs-human-workflow.md     # Different workflows for AI vs humans
    └── troubleshooting.md                # Common issues and solutions
```

## Scripts

### amia_kanban_get_board_state.py

Get complete board state with all items grouped by status column.

```bash
python3 scripts/amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER [--json] [--summary]
```

### amia_kanban_move_card.py

Move a card to a different status column with validation.

```bash
python3 scripts/amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS [--reason "Reason"]
```

### amia_kanban_check_completion.py

Check if all board items are complete (for stop hook).

```bash
python3 scripts/amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER [--verbose] [--json]
```

**Exit codes:**
- `0`: All items Done (can exit)
- `1`: Items still in progress (cannot exit)
- `2`: Blocked items exist (needs attention)

## Board Columns

| Column | Meaning |
|--------|---------|
| **Backlog** | Not yet scheduled |
| **Todo** | Ready to start |
| **In Progress** | Active development |
| **AI Review** | Integrator reviews PR (all tasks) |
| **Human Review** | User reviews PR (big tasks only) |
| **Merge/Release** | PR ready to merge |
| **Done** | Completed and merged |
| **Blocked** | Cannot proceed |

## Integration Points

- **Planning phase:** Creates issues on board
- **Orchestration phase:** Moves cards between columns
- **Stop hook:** Checks board state before exit
- **Module assignment:** Uses issue assignees
- **PR completion:** Auto-moves to Done on merge

## Related Skills

- `github-projects-sync` - Detailed GitHub Projects V2 operations
- `remote-agent-coordinator` - Agent communication and task routing
- `orchestrator-stop-hook` - Stop hook behavior and configuration

## License

Apache-2.0
