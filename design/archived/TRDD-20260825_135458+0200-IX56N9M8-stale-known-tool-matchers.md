---
trdd-id: IX56N9M8
title: KNOWN_TOOL_MATCHERS in claude-plugin-install.py is stale - cosmetic, validator unused
column: complete
created: 2026-08-25T13:54:58+0200
updated: 2026-08-25T14:07:00+0200
current-owner: integrator-claude
task-type: refactor
relevant-rules: []
min-approval-requirement: none
implementation-commits: [684cf4e]
---

# `KNOWN_TOOL_MATCHERS` is stale — cosmetic, and its validator is unused

## Problem (verified 2026-08-22, CC 2.1.233→240 alignment audit)

`scripts/claude-plugin-install.py:796` hardcodes a tool-name allowlist that is
missing at least: SendMessage, ListAgents, Monitor, Artifact, ScheduleWakeup,
ReportFindings, TaskOutput, CronCreate, DesignSync, RemoteTrigger.

**Verified COSMETIC:** `publish.py` never invokes that validator, and the
validator returns `len(errors) == 0` without gating anything in the live
pipeline. No user-visible behavior is wrong today.

## Decision to make (why this is parked, not fixed)

Refreshing means hand-entering a tool list — **a wrong or misspelled name is
worse than a missing one** (it would start rejecting valid hook matchers), and
the CC tool roster moves with every release, so a hand-copied list re-stales
immediately. Options when picked up:
1. **Delete the validator** (and `KNOWN_TOOL_MATCHERS`) — dead code under
   fail-fast/no-legacy; smallest diff, removes the re-staling treadmill.
2. **Keep and refresh** — only if some caller starts using it; then derive the
   list from a live source rather than hand-typing, or downgrade unknown names
   to a warning so a stale list can never hard-block.

Default recommendation when picked up: option 1, after a repo-wide grep for
`KNOWN_TOOL_MATCHERS` and the validator's name confirms zero callers.

## Acceptance

- [x] Either zero references to `KNOWN_TOOL_MATCHERS` remain, or the validator
      has a real caller plus a non-hand-typed (or warn-only) tool list.
      → OPTION 2, because verification OVERTURNED option 1's premise: the
      validator IS called — `_validate_matcher` → hooks validation →
      `do_validate` → the `--validate` CLI flag (claude-plugin-install.py:3220).
      "publish.py never invokes it" was true but incomplete. List refreshed
      with 16 names copied from a live CC 2.1.240 harness (not from memory);
      the set was already warn-only; the miss message no longer overclaims.
- [x] `tests/run-all-tests.py` still green. → 16/16, ruff 0, mypy 0.

## Approval log

- 2026-08-25T14:07:00+0200 — COMPLETED by integrator-claude
  (min-approval-requirement: none; USER delegated completion of pending
  TRDDs on verified facts, 2026-08-25). Implemented in commit 684cf4e.
