---
trdd-id: L3XIKYMO
title: Stop-hook Check 3 is inert - nothing ever writes .claude/tasks
column: complete
created: 2026-08-25T13:54:58+0200
updated: 2026-08-25T14:07:00+0200
current-owner: integrator-claude
task-type: refactor
relevant-rules: []
min-approval-requirement: none
implementation-commits: [d3d52c8]
---

# Stop-hook Check 3 is inert — nothing ever writes `.claude/tasks/`

## Problem (verified 2026-08-22, CC 2.1.233→240 alignment audit)

`amia_stop_hook.py::check_claude_tasks()` reads `<project>/.claude/tasks/` to
report open tasks at Stop time, but **no code path in this plugin or in Claude
Code writes that directory** — the check has always returned the empty result.
This predates CC 2.1.233 (it is unrelated to the todo-tool removal; the two
"Claude Tasks" concepts are distinct and a blanket purge would break this hook —
see the alignment ledger `reports/cc-alignment-233-240/DELEGATION.md`).

## Decision to make (why this is a card, not a fix)

Two exits, both cheap, mutually exclusive:
1. **Delete Check 3** — dead code under the fail-fast/no-legacy rule; smallest diff.
2. **Implement a writer** — only if some workflow is supposed to persist tasks
   into `.claude/tasks/`; none is known today, which makes this option YAGNI
   until a consumer appears.

Default recommendation when picked up: option 1, unless a writer requirement
has appeared meanwhile. Verify with a repo-wide grep for `.claude/tasks`
before deleting (references in prose count).

## Acceptance

- [x] `check_claude_tasks` either removed (with its call site and any prose
      naming it) or fed by a real writer with a test that exercises both.
      → REMOVED (option 1): function, call site, docstring line, and the
      phantom-store prose in github-sync-procedure.md §1.5.4/§1.8 + the
      amia-github-sync agent's mirrored TOC. Repo-wide grep confirmed no
      writer exists; remaining "Claude Tasks" prose elsewhere refers to the
      distinct personal-tasks concept, not this store, and was left alone.
- [x] `tests/run-all-tests.py` still green. → 16/16, ruff 0, mypy 0.

## Approval log

- 2026-08-25T14:07:00+0200 — COMPLETED by integrator-claude
  (min-approval-requirement: none; USER delegated completion of pending
  TRDDs on verified facts, 2026-08-25). Implemented in commit d3d52c8.
