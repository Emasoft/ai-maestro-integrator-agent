# Why Kanban Is the Single Source of Truth

## Table of Contents

- 1.1 [Why centralized truth matters for AI orchestration](#11-why-centralized-truth-matters)
- 1.2 [The problems with distributed state tracking](#12-problems-with-distributed-state)
- 1.3 [Why GitHub Projects V2 is the ideal choice](#13-why-github-projects-v2)
- 1.4 [The Iron Rules of Kanban-centric orchestration](#14-the-iron-rules)
- 1.5 [What happens when you violate these rules](#15-violation-consequences)
- 1.6 [Comparison: Traditional vs Kanban-centric orchestration](#16-comparison)

---

## 1.1 Why Centralized Truth Matters

AI orchestration involves multiple autonomous agents working concurrently on different parts of a project. Each agent has:
- Limited context window (cannot remember everything)
- No persistent memory between sessions
- No direct communication with other agents (except messaging)
- No visibility into what other agents are doing

Without a centralized source of truth:
- Agents might work on the same task
- Completed work might be reassigned
- Blocked items might be ignored
- Progress is invisible to the orchestrator

**The solution:** A single, authoritative system that ALL agents and the orchestrator read from and write to.

---

## 1.2 Problems with Distributed State

### Problem 1: Orchestrator Memory

If the orchestrator tracks work in its context window:
- Memory is lost on session restart
- Context compaction loses state
- No visibility for humans
- No audit trail

### Problem 2: Local Files

If state is tracked in local files (Claude Tasks, markdown, JSON):
- Files can become stale
- Multiple agents cannot safely update
- Merge conflicts corrupt state
- No real-time visibility

### Problem 3: Agent Self-Reporting

If agents report their own status:
- Reports can be wrong or outdated
- Agent crashes lose state
- No verification mechanism
- Orchestrator must poll constantly

### Problem 4: Multiple Systems

If state is split across systems:
- Synchronization overhead
- Conflicting information
- No single "truth"
- Complex reconciliation logic

---

## 1.3 Why GitHub Projects V2

GitHub Projects V2 solves all these problems:

| Requirement | GitHub Projects Solution |
|-------------|--------------------------|
| Persistent | Board state survives all session restarts |
| Concurrent | Multiple agents can update safely |
| Visible | Humans can see board in browser |
| Auditable | Full history in issue timeline |
| Integrated | PRs auto-close issues on merge |
| API Access | GraphQL API for programmatic access |
| Notifications | Built-in notification system |
| Free | Included with GitHub repository |

### Key Features for Orchestration

1. **Columns as States:** Each column represents a workflow state
2. **Cards as Work Items:** Each card is an issue representing one unit of work
3. **Assignees as Owners:** Issue assignees show who is responsible
4. **Automation:** PR merges can auto-move cards to Done
5. **Labels:** Additional metadata without cluttering the board
6. **Comments:** Full discussion history on each item

---

## 1.4 The Iron Rules

These rules are ABSOLUTE. No exceptions.

### Rule 1: Board Is Truth

```
IF board says "In Progress" THEN work IS in progress
IF board says "Done" THEN work IS done
IF board says "Blocked" THEN work IS blocked

There is no "but actually..." - the board IS reality.
```

### Rule 2: All Work Is On Board

```
IF work is not on the board THEN work does not exist
The orchestrator NEVER tracks work outside the board
Claude Tasks is for personal tasks, NOT project work
```

### Rule 3: State Changes Through Board

```
To change work status:
  1. Update the board
  2. That's it. The board IS the status.

NOT:
  1. Update internal state
  2. Then update board

The board update IS the state change.
```

### Rule 4: Assignments Are Assignees

```
To assign work to an agent:
  1. Set the issue assignee to the agent
  2. That's it. The assignee IS the assignment.

NOT:
  1. Track assignment in memory
  2. Then update assignee

The assignee update IS the assignment.
```

### Rule 5: Completion Is Column Position

```
Work is complete when:
  - Issue is in "Done" column

NOT when:
  - Agent says it's done
  - PR is merged (until board reflects it)
  - Tests pass
  - Anyone thinks it's done

Only the "Done" column means done.
```

---

## 1.5 Violation Consequences

### Violation: Tracking State Elsewhere

**What happens:**
- Orchestrator believes work is in state X
- Board shows state Y
- Decisions are made based on wrong state
- Work is duplicated, lost, or corrupted

**Example:**
```
Orchestrator thinks: "Module A is done" (from memory)
Board shows: Module A is "In Progress"
Result: Module A never gets finished because orchestrator moved on
```

### Violation: Not Adding Work to Board

**What happens:**
- Work exists but is invisible
- Other agents don't know about it
- Stop hook doesn't track it
- Work is lost on session restart

**Example:**
```
Orchestrator assigns work verbally: "Agent, implement auth module"
Board: No auth module issue exists
Result: Work vanishes when agent session ends
```

### Violation: Disagreeing with Board

**What happens:**
- Orchestrator "knows better" than board
- Makes decisions based on assumptions
- Board becomes stale and useless
- Total loss of orchestration coherence

**Example:**
```
Board shows: 5 items "In Progress"
Orchestrator believes: "Those are all done, agents just forgot to update"
Result: Orchestrator exits with incomplete work
```

---

## 1.6 Comparison

### Traditional Orchestration

```
┌─────────────────┐
│   Orchestrator  │
│   ┌─────────┐   │
│   │ Memory  │   │  <-- State lives here
│   │ State   │   │
│   └─────────┘   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────┐
│Agent1│  │Agent2│
└──────┘  └──────┘
```

**Problems:**
- Memory is volatile
- Agents can't see state
- No persistence
- No audit trail

### Kanban-Centric Orchestration

```
┌─────────────────────────────────┐
│         GitHub Kanban           │  <-- State lives here
│ ┌────────┬────────┬──────────┐ │
│ │Backlog │  Todo  │In Progress│ │
│ ├────────┼────────┼──────────┤ │
│ │ #1     │ #3     │ #5       │ │
│ │ #2     │ #4     │          │ │
│ └────────┴────────┴──────────┘ │
└────────────────┬────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌──────────┐ ┌──────┐ ┌──────────┐
│Orchestr. │ │Agent1│ │  Human   │
│          │ │      │ │Developer │
└──────────┘ └──────┘ └──────────┘
```

**Benefits:**
- All parties see same state
- State survives crashes
- Full audit trail
- Real-time visibility

---

## Summary

The Kanban board is not a reporting tool. It is not a nice-to-have visualization.

**The Kanban board IS the orchestration state.**

Read it. Write to it. Trust it. Never contradict it.
