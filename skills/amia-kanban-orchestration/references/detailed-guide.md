# GitHub Kanban Core -- Detailed Guide

## Contents

- [The Iron Rule](#the-iron-rule)
- [Board Columns Quick Reference](#board-columns-quick-reference)
- [Command Integration: /create-issue-tasks](#command-integration-create-issue-tasks)
- [Python Scripts Detailed Usage](#python-scripts-detailed-usage)
- [Error Handling](#error-handling)
- [Integration Points Summary](#integration-points-summary)
- [Proactive Kanban Monitoring Summary](#proactive-kanban-monitoring-summary)
- [Skill File Structure](#skill-file-structure)
- [Related Skills](#related-skills)

---

## The Iron Rule

**GitHub Projects Kanban IS the orchestration state. There is no other source of truth.**

- Every module = 1 GitHub Issue on the board
- Every agent assignment = 1 Issue assignee
- Every status change = 1 board column move
- The orchestrator NEVER tracks work in memory, files, or any other system

If it's not on the board, it doesn't exist. If the board says "In Progress", it IS in progress.

---

## Board Columns Quick Reference

| Column | Code | Meaning | Who Can Move Here |
|--------|------|---------|-------------------|
| **Backlog** | `backlog` | Not scheduled | Orchestrator only |
| **Todo** | `todo` | Ready to start | Orchestrator only |
| **In Progress** | `in-progress` | Active work | Assigned agent |
| **AI Review** | `ai-review` | Integrator reviews ALL tasks | Integrator agent |
| **Human Review** | `human-review` | User reviews BIG tasks only | User/human reviewer |
| **Merge/Release** | `merge-release` | Ready to merge | Orchestrator |
| **Done** | `done` | Completed and merged | Auto (PR merge) |
| **Blocked** | `blocked` | Cannot proceed | Any (with reason) |

---

## Command Integration: /create-issue-tasks

The `/create-issue-tasks` command creates Claude Tasks checklists for handling issues. See the full command documentation at:
`${CLAUDE_PLUGIN_ROOT}/commands/create-issue-tasks.md`

### Quick Usage

```
/create-issue-tasks <CATEGORY> <REPORTER> <MODULE> "<TITLE>" ["<DESCRIPTION>"]
```

**Categories:** BUG, BLOCKER, QUESTION, ENHANCEMENT, CONFIG, INVESTIGATION

**Example:**

```
/create-issue-tasks BUG implementer-1 auth-core "Login fails with OAuth" "401 error after token expiry"
```

---

## Python Scripts Detailed Usage

### Get Board State (scripts/amia_kanban_get_board_state.py)

Get complete board state with all items grouped by column.

```bash
python3 scripts/amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER
```

**Output:** JSON with items grouped by status column.

### Move Card (scripts/amia_kanban_move_card.py)

Move a card to a different column with validation.

```bash
python3 scripts/amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS [--reason "Reason"]
```

**Validates:** Transition is allowed, preconditions met.

### Check Completion (scripts/amia_kanban_check_completion.py)

Check if all board items are complete (for stop hook).

```bash
python3 scripts/amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER
```

**Exit codes:**

- 0: All items Done
- 1: Items still in progress
- 2: Blocked items exist

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| **Issue not appearing on board** | Issue not added to Projects V2, wrong project number | Verify project link with `gh issue view <N>`, re-add to project |
| **Status change not reflecting** | Invalid transition, missing permissions | Check transition matrix in references/status-transitions.md, verify GitHub permissions |
| **Assignment not showing** | Issue not on board, invalid assignee username | Ensure issue is on project board, use correct GitHub username |
| **GraphQL API rate limit** | Too many rapid queries | Wait 60 seconds, use query caching, reduce polling frequency |
| **Permission denied** | Insufficient GitHub permissions | Verify `gh auth status`, ensure write access to repository and project |
| **Board state out of sync** | Stale cache, concurrent modifications | Force refresh with fresh GraphQL query, avoid caching board state |
| **Stop hook blocking exit** | Items not in Done column | Complete pending items, move to Done, or defer with explicit reason |
| **Corrupted board state** | Manual edits outside workflow | Use recovery procedure in references/troubleshooting.md section 10.8 |

---

## Integration Points Summary

Read `references/integration-points.md` for full details on how Kanban connects to:

- IP.1 Planning Phase workflow
- IP.2 Orchestration Phase workflow
- IP.3 Stop Hook Phase workflow
- IP.4 Assignment Flow
- IP.5 PR Completion Flow

---

## Proactive Kanban Monitoring Summary

Read `references/proactive-kanban-monitoring.md` for full details on:

- M.1 Overview of proactive monitoring
- M.2 Polling configuration and frequency
- M.3 What to check on each poll (detection table)
- M.4 Running the polling script
- M.5 Change detection logic (pseudocode)
- M.6 AI Maestro notifications for detected changes
- M.7 Proactive monitoring checklist

---

## Skill File Structure

```
amia-kanban-orchestration/
├── SKILL.md                              # Compact index (this skill's entry point)
├── README.md                             # Skill overview
├── scripts/
│   ├── amia_kanban_get_board_state.py    # Get full board state
│   ├── amia_kanban_move_card.py          # Move card between columns
│   └── amia_kanban_check_completion.py   # Check completion for stop hook
└── references/
    ├── detailed-guide.md                 # This file (extended details)
    ├── kanban-as-truth.md                # Why Kanban is single source of truth
    ├── board-column-semantics.md         # Column meanings and requirements
    ├── issue-to-module-mapping.md        # Module-to-issue 1:1 mapping
    ├── agent-assignment-via-board.md     # Assignment via issue assignees
    ├── status-transitions.md             # Valid state transitions
    ├── blocking-workflow.md              # Handling blocked items
    ├── board-queries.md                  # GraphQL queries for board state
    ├── stop-hook-integration.md          # Stop hook completion checks
    ├── ai-agent-vs-human-workflow.md     # Different workflows for AI vs humans
    ├── integration-points.md             # Planning, orchestration, stop hooks
    ├── proactive-kanban-monitoring.md    # Board polling and change detection
    ├── instruction-templates.md          # Message and assignment templates
    ├── failure-scenarios.md              # Failure handling and recovery
    └── troubleshooting.md               # Common issues and solutions
```

---

## Related Skills

- **github-projects-sync** - Detailed GitHub Projects V2 operations and templates
- **remote-agent-coordinator** - Agent communication and task routing
- **orchestrator-stop-hook** - Stop hook behavior and configuration

---

## When to Use This Skill

Read this skill when:

- Starting any orchestration session
- Planning new work (modules, features, tasks)
- Assigning work to agents or humans
- Checking work status or progress
- Verifying completion before exiting
- Handling blocked work items
- Integrating with stop hooks

---

## Content Moved from SKILL.md (trimmed for size)

### Original Reference Documents Listing

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

### Original Extended Instructions

1. **Handle blockers** - Move to Blocked with `--reason` per `references/blocking-workflow.md`
2. **Verify completion** - Run `amia_kanban_check_completion.py` (exit 0 = all done)

### Original Extended Checklist Items

- [ ] Issues added to board in Backlog column
- [ ] PRs linked to issues, moved to AI Review

### Original Error Handling Details

If a script fails, check the exit code and stderr output. Common issues:

- **Exit 1**: Invalid parameters or missing arguments
- **Exit 2-4**: GitHub API errors (auth, not found, rate limit)

### Original Resources Listing

- `references/agent-assignment-via-board.md`
- `references/ai-agent-vs-human-workflow-part1-fundamentals.md`
- `references/ai-agent-vs-human-workflow-part2-workflows.md`
- `references/ai-agent-vs-human-workflow.md`
- `references/blocking-workflow.md`
- `references/board-column-semantics.md`
- `references/board-queries-part1-basic.md`
- `references/board-queries-part2-filtered.md`
- ...and 22 more in `references/`
