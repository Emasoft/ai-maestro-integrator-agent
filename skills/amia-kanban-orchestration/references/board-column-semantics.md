# Board Column Semantics

## Table of Contents

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

---

## 2.1 Overview

The AMOA orchestration workflow uses exactly 8 columns. Each column has a precise meaning, requirements, and rules about who can move items into it.

```
┌──────────┬──────────┬────────────┬───────────┬──────────────┬───────────────┬──────────┬──────────┐
│ Backlog  │   Todo   │In Progress │ AI Review │ Human Review │ Merge/Release │   Done   │ Blocked  │
├──────────┼──────────┼────────────┼───────────┼──────────────┼───────────────┼──────────┼──────────┤
│ Not yet  │ Ready to │  Active    │ Integrator│ User reviews │ Ready to      │ Merged   │ Cannot   │
│scheduled │  start   │   work     │ reviews   │ BIG tasks    │ merge         │          │ proceed  │
└──────────┴──────────┴────────────┴───────────┴──────────────┴───────────────┴──────────┴──────────┘
```

**Flow:** Backlog -> Todo -> In Progress -> AI Review -> Human Review (big tasks) / Merge/Release (small tasks) -> Done

**Special:** Any status can move to Blocked (and back)

---

## 2.2 Backlog

### Meaning

Items in Backlog are:
- Identified and defined
- Not yet scheduled for work
- Waiting for prioritization or capacity

### Requirements to Enter Backlog

- Issue exists with clear title and description
- Acceptance criteria defined (what "done" means)
- No duplicate of existing issue

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| New issue | Automatic (creation) |
| Todo | Orchestrator only |
| Cancelled | Orchestrator only |

### Example Items

- Features identified during planning but not yet prioritized
- Bugs that are low priority
- Improvements for future iterations

### Orchestrator Actions

When reviewing Backlog:
1. Prioritize items
2. Move high-priority items to Todo
3. Add missing details to items
4. Remove or cancel invalid items

---

## 2.3 Todo

### Meaning

Items in Todo are:
- Scheduled for the current or next sprint/iteration
- Ready to be assigned and started
- Have all prerequisites met

### Requirements to Enter Todo

- Clear acceptance criteria
- Dependencies identified (and satisfied or in progress)
- Effort estimated (optional but recommended)
- Assigned to sprint/iteration (if using iterations)

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Backlog | Orchestrator only |
| In Progress | Assigned agent (pausing) |
| Blocked | Orchestrator (after unblock) |

### Example Items

- Next module to implement
- Bug assigned for current sprint
- Refactoring scheduled for this iteration

### Orchestrator Actions

When working with Todo:
1. Assign items to agents
2. Ensure items are ready to start
3. Monitor for items stuck too long

---

## 2.4 In Progress

### Meaning

Items in In Progress are:
- Currently being worked on
- Have an assigned agent actively coding
- Have a feature branch created

### Requirements to Enter In Progress

- Assigned to an agent
- Agent has started work
- Feature branch exists (or will be created immediately)

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Todo | Assigned agent |
| AI Review | Assigned agent (changes requested) |
| Blocked | Assigned agent (after unblock) |

### Expected Duration

- Should not exceed a few days
- Long items should be broken down
- Orchestrator should check items stuck > 24 hours

### Agent Responsibilities

When item is In Progress:
1. Work on the feature branch
2. Update issue with progress comments
3. Move to AI Review when PR is created
4. Move to Blocked if cannot proceed

---

## 2.5 AI Review

### Meaning

Items in AI Review are:
- Have a Pull Request created
- Integrator agent reviews ALL tasks (both small and big)
- Code is ready for review (from author's perspective)

### Requirements to Enter AI Review

- PR created and linked to issue
- All local tests pass
- PR description explains changes
- Ready for Integrator examination

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| In Progress | Assigned agent |

### Expected Duration

- Should not exceed 48 hours
- Escalate if review is delayed
- Ping Integrator if no activity

### Exit Conditions

| Next Status | Condition |
|-------------|-----------|
| Human Review | Big tasks requiring user review |
| Merge/Release | Small tasks approved by Integrator |
| In Progress | Changes requested |
| Blocked | Blocker discovered during review |

---

## 2.5a Human Review

### Meaning

Items in Human Review are:
- Have passed AI Review by the Integrator
- Require user/human review due to task size or importance
- Only BIG tasks go through Human Review

### Requirements to Enter Human Review

- AI Review completed by Integrator
- Integrator approved the changes
- Task flagged as requiring human review

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| AI Review | Integrator agent |

### Expected Duration

- Depends on human availability
- Escalate if no response in 72 hours

### Exit Conditions

| Next Status | Condition |
|-------------|-----------|
| Merge/Release | Human approves |
| In Progress | Human requests changes |
| Blocked | Blocker discovered during review |

---

## 2.5b Merge/Release

### Meaning

Items in Merge/Release are:
- Ready to be merged to the target branch
- All reviews (AI and optionally Human) have been completed
- Awaiting final merge action

### Requirements to Enter Merge/Release

- AI Review completed (all tasks)
- Human Review completed (big tasks only)
- All CI checks passing

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| AI Review | Integrator (small tasks) |
| Human Review | Orchestrator (big tasks) |

### Expected Duration

- Should be merged promptly (within 24 hours)

### Exit Conditions

| Next Status | Condition |
|-------------|-----------|
| Done | PR merged |
| Blocked | Merge conflict or CI failure |

---

## 2.6 Done

### Meaning

Items in Done are:
- Code merged to main branch
- Issue closed
- Work is complete and verified

### Requirements to Enter Done

- PR merged (not just approved)
- All CI checks passed
- Issue automatically closed (via "Closes #N")

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Merge/Release | Automatic (PR merge) |
| Manual | Orchestrator (exceptional cases) |

### Terminal Status

Done is a terminal status. Items in Done:
- Do not move to other columns
- Are considered complete
- Can be archived

### Verification

Orchestrator should verify Done items:
- PR is actually merged
- CI passed
- No follow-up issues created

---

## 2.7 Blocked

### Meaning

Items in Blocked are:
- Cannot proceed due to external factor
- Waiting for resolution of blocker
- Need orchestrator or human attention

### Requirements to Enter Blocked

- Blocker identified and documented
- Blocker is outside agent's control
- Comment explains the blocker

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Any non-terminal | Any agent or orchestrator |

### Required Documentation

When moving to Blocked, MUST provide:
- Description of the blocker
- Link to blocking issue (if applicable)
- What is needed to unblock
- When it was discovered

### Escalation Timeline

| Duration | Action |
|----------|--------|
| 0-24h | Monitor, await resolution |
| 24-48h | Ping responsible parties |
| 48-72h | Escalate to orchestrator |
| >72h | Escalate to human |

---

## 2.8 Metadata Table

| Column | Code | Is Terminal | Requires Assignment | Requires Branch | Requires PR |
|--------|------|-------------|---------------------|-----------------|-------------|
| Backlog | `backlog` | No | No | No | No |
| Todo | `todo` | No | Yes (to start) | No | No |
| In Progress | `in-progress` | No | Yes | Yes | No |
| AI Review | `ai-review` | No | Yes | Yes | Yes |
| Human Review | `human-review` | No | Yes | Yes | Yes |
| Merge/Release | `merge-release` | No | Yes | Yes | Yes |
| Done | `done` | Yes | No | No | No |
| Blocked | `blocked` | No | Yes | - | - |

---

## 2.9 Visual Layout

```
GitHub Project Board: "Project Alpha - Sprint 3"
┏━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━┯━━━━━━━━━━┯━━━━━━━━━━━━━┓
┃ Backlog (3)   │ Todo (2)      │ In Progress (2) │ AI Review (1) │ Human Rev (0)  │ Merge/Rel (0)   │ Done (5) │ Blocked (1) ┃
┣━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━┫
┃ ┌───────────┐ │ ┌───────────┐ │ ┌─────────────┐ │ ┌───────────┐ │                │                 │          │ ┌─────────┐ ┃
┃ │ #12       │ │ │ #8        │ │ │ #5          │ │ │ #7        │ │                │                 │          │ │ #9      │ ┃
┃ │ User prefs│ │ │ Auth API  │ │ │ Data model  │ │ │ UI tests  │ │                │                 │          │ │ CI setup│ ┃
┃ │           │ │ │ @agent-1  │ │ │ @agent-1    │ │ │ @agent-2  │ │                │                 │          │ │ @agent-3│ ┃
┃ └───────────┘ │ └───────────┘ │ └─────────────┘ │ └───────────┘ │                │                 │          │ └─────────┘ ┃
┃ ┌───────────┐ │ ┌───────────┐ │ ┌─────────────┐ │               │                │                 │          │             ┃
┃ │ #13       │ │ │ #10       │ │ │ #6          │ │               │                │                 │          │             ┃
┃ │ Export    │ │ │ Logging   │ │ │ Validation  │ │               │                │                 │          │             ┃
┃ │           │ │ │ @agent-2  │ │ │ @agent-2    │ │               │                │                 │          │             ┃
┃ └───────────┘ │ └───────────┘ │ └─────────────┘ │               │                │                 │          │             ┃
┃ ┌───────────┐ │               │                 │               │                │                 │          │             ┃
┃ │ #14       │ │               │                 │               │                │                 │          │             ┃
┃ │ Analytics │ │               │                 │               │                │                 │          │             ┃
┃ └───────────┘ │               │                 │               │                │                 │          │             ┃
┗━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━┷━━━━━━━━━━┷━━━━━━━━━━━━━┛
```

**Reading the Board:**
- Numbers in parentheses = item count
- `@agent-X` = assigned agent
- Issue number and title shown
- Unassigned items have no `@`
