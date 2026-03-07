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

## THE IRON RULE

**GitHub Projects Kanban IS the orchestration state. There is no other source of truth.**

- Every module = 1 GitHub Issue on the board
- Every agent assignment = 1 Issue assignee
- Every status change = 1 board column move
- The orchestrator NEVER tracks work in memory, files, or any other system

If it's not on the board, it doesn't exist. If the board says "In Progress", it IS in progress.

---

## Overview

This skill establishes GitHub Projects V2 as the absolute center of AMOA orchestration workflow. All planning, tracking, assignment, and completion verification flows through the Kanban board.

## Prerequisites

Before using this skill, ensure:
1. GitHub CLI is installed and authenticated (`gh auth status`)
2. GitHub Projects V2 is enabled for the repository
3. GraphQL API access is available
4. Python 3.8+ for running board management scripts

## Instructions

Follow these steps when using GitHub Kanban as the orchestration source of truth:

1. **Initialize board access** - Verify GitHub CLI authentication and Projects V2 access
2. **Query current state** - Use `amia_kanban_get_board_state.py` to see all items and their columns
3. **Create module issues** - For new work, create GitHub Issues following the issue-to-module mapping (see references/issue-to-module-mapping.md)
4. **Assign work** - Set issue assignees to designate responsible agents (see references/agent-assignment-via-board.md)
5. **Track transitions** - Move cards between columns as work progresses (see references/status-transitions.md)
6. **Handle blockers** - Mark items as Blocked with reason when cannot proceed (see references/blocking-workflow.md)
7. **Verify completion** - Before exit, use `amia_kanban_check_completion.py` to ensure all items are Done

### Checklist

Copy this checklist and track your progress:

- [ ] Verify GitHub CLI authentication: `gh auth status`
- [ ] Verify Projects V2 access for the repository
- [ ] Query current board state: `python3 scripts/amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER`
- [ ] Create module issues for new work (1 issue = 1 module)
- [ ] Add issues to project board in Backlog column
- [ ] Move ready issues from Backlog to Todo
- [ ] Assign issues to responsible agents (issue assignee = agent)
- [ ] Agent moves issue to In Progress when starting work
- [ ] Agent creates PR linked to issue, moves to AI Review
- [ ] Track card transitions using: `python3 scripts/amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS`
- [ ] Handle any blockers: move to Blocked column with `--reason` flag
- [ ] Resolve blockers and move back to previous status
- [ ] Verify completion before exit: `python3 scripts/amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER`
- [ ] Ensure exit code is 0 (all items Done) before exiting

### When to Use This Skill

Read this skill when:
- Starting any orchestration session
- Planning new work (modules, features, tasks)
- Assigning work to agents or humans
- Checking work status or progress
- Verifying completion before exiting
- Handling blocked work items
- Integrating with stop hooks

---

## Quick Reference: Board Columns

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

## Python Scripts

### Get Board State ([scripts/amia_kanban_get_board_state.py](scripts/amia_kanban_get_board_state.py))

Get complete board state with all items grouped by column.

```bash
python3 scripts/amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER
```

**Output:** JSON with items grouped by status column.

---

### Move Card ([scripts/amia_kanban_move_card.py](scripts/amia_kanban_move_card.py))

Move a card to a different column with validation.

```bash
python3 scripts/amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS [--reason "Reason"]
```

**Validates:** Transition is allowed, preconditions met.

---

### Check Completion ([scripts/amia_kanban_check_completion.py](scripts/amia_kanban_check_completion.py))

Check if all board items are complete (for stop hook).

```bash
python3 scripts/amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER
```

**Exit codes:**
- 0: All items Done
- 1: Items still in progress
- 2: Blocked items exist

---

## Integration Points ([references/integration-points.md](references/integration-points.md))

Read this when understanding how Kanban connects to planning, orchestration, stop hooks, assignments, and PR completion.

**Contents:**
- IP.1 Planning Phase workflow
- IP.2 Orchestration Phase workflow
- IP.3 Stop Hook Phase workflow
- IP.4 Assignment Flow
- IP.5 PR Completion Flow

---

## Skill Files

```
github-kanban-core/
├── SKILL.md                              # This file (map/TOC)
├── README.md                             # Skill overview
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

---

## Output Discipline

All scripts support the `--output-file <path>` flag:
- **With flag**: Full JSON written to file; concise summary printed to stderr
- **Without flag**: Full JSON printed to stdout (backward compatible)

When invoking from agents or automated workflows, always pass `--output-file` to minimize token consumption.

## Examples

### Example 1: Get Current Board State

```bash
# Get full board state with all items
python3 scripts/amia_kanban_get_board_state.py owner repo 1

# Output: JSON with items grouped by status column (Backlog, Todo, In Progress, etc.)
```

### Example 2: Move Card and Check Completion

```bash
# Move issue #42 to In Progress
python3 scripts/amia_kanban_move_card.py owner repo 1 42 in-progress --reason "Starting work"

# Check if all items are complete (for stop hook)
python3 scripts/amia_kanban_check_completion.py owner repo 1
# Exit code 0 = all done, 1 = items pending, 2 = blocked items exist
```

---

## Output

| Output Type | Format | Description | When Generated |
|-------------|--------|-------------|----------------|
| **Board State JSON** | JSON object | All items grouped by status column | Via `amia_kanban_get_board_state.py` |
| **Transition Result** | JSON object | Success/failure of card move with validation | Via `amia_kanban_move_card.py` |
| **Completion Status** | Exit code + JSON | 0=all done, 1=pending, 2=blocked | Via `amia_kanban_check_completion.py` |
| **Assignment Notification** | AI Maestro message | Agent receives work assignment | When issue assigned |
| **GraphQL Query Results** | JSON object | Raw board data from GitHub API | Via reference queries |
| **Blocker Report** | JSON object | All blocked items with reasons | When querying blocked items |

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

## Resources

- [references/kanban-as-truth.md](references/kanban-as-truth.md) - Why Kanban is the single source of truth
  <!-- TOC: kanban-as-truth.md -->
  - 1.1 [Why centralized truth matters for AI orchestration](#11-why-centralized-truth-matters)
  - 1.2 [The problems with distributed state tracking](#12-problems-with-distributed-state)
  - 1.3 [Why GitHub Projects V2 is the ideal choice](#13-why-github-projects-v2)
  - 1.4 [The Iron Rules of Kanban-centric orchestration](#14-the-iron-rules)
  - 1.5 [What happens when you violate these rules](#15-violation-consequences)
  - 1.6 [Comparison: Traditional vs Kanban-centric orchestration](#16-comparison)
  <!-- /TOC -->
- [references/board-column-semantics.md](references/board-column-semantics.md) - Column meanings and requirements
  <!-- TOC: board-column-semantics.md -->
  - 2.1 [Overview of the 8-column workflow](#21-overview)
  - 2.2 [Backlog column - items not yet scheduled](#22-backlog)
  - 2.3 [Todo column - ready for immediate work](#23-todo)
  - 2.4 [In Progress column - active development](#24-in-progress)
  - 2.5 [AI Review column - Integrator reviews ALL tasks](#25-ai-review)
  - 2.5a [Human Review column - User reviews BIG tasks only](#25a-human-review)
  - 2.5b [Merge/Release column - Ready to merge](#25b-merge-release)
  - 2.6 [Done column - completed and verified](#26-done)
  - 2.7 [Blocked column - cannot proceed](#27-blocked)
  - 2.8 [Column metadata and requirements table](#28-metadata-table)
  - 2.9 [Visual board layout example](#29-visual-layout)
  <!-- /TOC -->
- [references/issue-to-module-mapping.md](references/issue-to-module-mapping.md) - Module-to-issue 1:1 mapping
  <!-- TOC: issue-to-module-mapping.md -->
  - 3.1 [The 1:1 principle: every module is exactly one issue](#31-the-11-principle)
  - 3.2 [Module issue template structure](#32-template-structure)
  - 3.3 [Required fields for module issues](#33-required-fields)
  - 3.4 [Naming conventions for module issues](#34-naming-conventions)
  - 3.5 [Linking module issues to parent epics](#35-linking-to-epics)
  - 3.6 [Creating module issues from plan files](#36-from-plan-files)
  - 3.7 [Bulk module issue creation workflow](#37-bulk-creation)
  - 3.8 [Module issue lifecycle from creation to closure](#38-lifecycle)
  <!-- /TOC -->
- [references/agent-assignment-via-board.md](references/agent-assignment-via-board.md) - Assignment via issue assignees
  <!-- TOC: agent-assignment-via-board.md -->
  - 4.1 [Assignment principle: issue assignee = responsible agent](#41-assignment-principle)
  - 4.2 [How to assign issues via CLI](#42-assign-via-cli)
  - 4.3 [How to assign issues via GraphQL](#43-assign-via-graphql)
  - 4.4 [Agent naming conventions for GitHub](#44-naming-conventions)
  - 4.5 [Verifying current assignments](#45-verify-assignments)
  - 4.6 [Reassigning work between agents](#46-reassigning)
  - 4.7 [Multi-agent collaboration on single issue](#47-multi-agent-collaboration)
  - 4.8 [Assignment notifications via AI Maestro](#48-notifications)
  <!-- /TOC -->
- [references/status-transitions.md](references/status-transitions.md) - Valid state transitions
  <!-- TOC: status-transitions.md -->
  - 5.1 [Valid transition matrix](#51-transition-matrix)
  - 5.2 [Transition preconditions and postconditions](#52-preconditions-and-postconditions)
  - 5.3 [Who can move cards](#53-who-can-move)
  - 5.4 [Backlog to Todo transition rules](#54-backlog-to-todo)
  - 5.5 [Todo to In Progress transition rules](#55-todo-to-in-progress)
  - 5.6 [In Progress to AI Review transition rules](#56-in-progress-to-ai-review)
  - 5.6a [AI Review to Human Review transition rules (big tasks)](#56a-ai-review-to-human-review)
  - 5.6b [AI Review to Merge/Release transition rules (small tasks)](#56b-ai-review-to-merge-release)
  - 5.6c [Human Review to Merge/Release transition rules](#56c-human-review-to-merge-release)
  - 5.7 [Merge/Release to Done transition rules](#57-merge-release-to-done)
  - 5.8 [Any status to Blocked transition rules](#58-any-to-blocked)
  - 5.9 [Blocked to previous status transition rules](#59-blocked-to-previous)
  - 5.10 [Invalid transitions and handling](#510-invalid-transitions)
  <!-- /TOC -->
- [references/blocking-workflow.md](references/blocking-workflow.md) - Handling blocked items
  <!-- TOC: blocking-workflow.md -->
  - 6.1 [What constitutes a blocked task](#61-what-constitutes-a-blocked-task)
  - 6.2 [How to mark an item as blocked](#62-marking-as-blocked)
  - 6.3 [Required information when blocking](#63-required-information)
  - 6.4 [Blocker escalation timeline](#64-escalation-timeline)
  - 6.5 [Resolving blockers and resuming work](#65-resolving-blockers)
  - 6.6 [Cross-issue blocking dependencies](#66-cross-issue-blocking)
  - 6.7 [External blockers](#67-external-blockers)
  - 6.8 [Blocker status reporting](#68-status-reporting)
  <!-- /TOC -->
- [references/board-queries.md](references/board-queries.md) - GraphQL queries for board state
  <!-- TOC: board-queries.md -->
  - ### Part 1: Basic Queries
  - 1 Full Board State - Get complete board with all items and field values
  - 1 GraphQL query for full project state
  <!-- /TOC -->
- [references/stop-hook-integration.md](references/stop-hook-integration.md) - Stop hook completion checks
  <!-- TOC: stop-hook-integration.md -->
  - 8.1 [The stop hook's role in orchestration](#81-stop-hook-role)
  - 8.2 [Board state queries performed by stop hook](#82-board-queries)
  - 8.3 [Completion criteria: when can orchestrator exit](#83-completion-criteria)
  - 8.4 [Handling incomplete work at exit time](#84-incomplete-work)
  - 8.5 [Blocked items and exit policy](#85-blocked-items)
  - 8.6 [Stop hook configuration options](#86-configuration)
  - 8.7 [Manual override of stop hook](#87-manual-override)
  - 8.8 [Stop hook error handling](#88-error-handling)
  <!-- /TOC -->
- [references/ai-agent-vs-human-workflow.md](references/ai-agent-vs-human-workflow.md) - Different workflows for AI vs humans
  <!-- TOC: ai-agent-vs-human-workflow.md -->
  - ### Part 1: Fundamentals and Communication
  - 1 Key differences in AI vs human workflow
  - 1 Comparison matrix (availability, response time, context)
  <!-- /TOC -->
- [references/instruction-templates.md](references/instruction-templates.md) - Message and assignment templates
  <!-- TOC: instruction-templates.md -->
  - Task Assignment Template
  - GitHub Issue Template for Subtasks
  - Integration Assignment Template
  <!-- /TOC -->
- [references/failure-scenarios.md](references/failure-scenarios.md) - Failure handling and recovery patterns
  <!-- TOC: failure-scenarios.md -->
  - Subtask Reports Failure After Others In Progress
  - Integration Reports Failures
  - Agent Becomes Unresponsive
  <!-- /TOC -->
- [references/troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
  <!-- TOC: troubleshooting.md -->
  - ### Part 1: Issue and Status Problems
  - 1 Issue not appearing on board after creation
  - Cause 1: Issue Not Added to Project
  <!-- /TOC -->

---

## Proactive Kanban Monitoring ([references/proactive-kanban-monitoring.md](references/proactive-kanban-monitoring.md))

Read this when setting up or running proactive board monitoring during orchestration sessions.

**Contents:**
- M.1 Overview of proactive monitoring
- M.2 Polling configuration and frequency
- M.3 What to check on each poll (detection table)
- M.4 Running the polling script
- M.5 Change detection logic (pseudocode)
- M.6 AI Maestro notifications for detected changes
- M.7 Proactive monitoring checklist

---

## Related Skills

- **github-projects-sync** - Detailed GitHub Projects V2 operations and templates
- **remote-agent-coordinator** - Agent communication and task routing
- **orchestrator-stop-hook** - Stop hook behavior and configuration
