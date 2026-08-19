---
trdd-id: TNZ8RCOE
title: Sweep bare agent-messaging invocations to frozen amp-* CLIs
column: completed
created: 2026-08-19T10:28:33+0200
updated: 2026-08-19T14:03:30+0200
current-owner: integrator-session
task-type: docs
min-approval-requirement: none
---

# Sweep bare agent-messaging invocations to frozen amp-* CLIs

Hub directive (ai-maestro-fd, 2026-08-19, USER hub-orchestration mandate) + hub correction:
`agent-messaging` IS a real knowledge skill shipped by ai-maestro-plugin, but plugin skills
resolve NAMESPACED — bare-name invocation ("send a message using the `agent-messaging` skill")
fails at runtime. 35 tracked files in this repo carry the string.

## Scope

Per-file classification, never bulk replace:
- INVOCATION-shaped teaching (skill named as the send mechanism) → rewrite to the frozen
  amp-* CLIs: `amp-send <recipient> <subject> <message> [--type request|response|notification|task|status] [--priority low|normal|high|urgent]`, `amp-inbox`, `amp-reply` (AMP frozen CLI). Model: AMOA commit d5d1588 method (parallel workers, grep-clean verify, tests).
- Genuine knowledge pointer → namespace as `ai-maestro-plugin:agent-messaging`.
- Historical prose → leave (or namespace if it reads as guidance).

File list captured at /tmp/sweep-files.txt (35 tracked; docs_dev excluded as unpublished).

## Acceptance

- [x] repo-wide grep: zero bare-invocation teachings remain (`agent-messaging` only as namespaced pointer or deliberate historical prose) — verified `bare-left=0` 2026-08-19
- [x] full test suite passes (15/15 files) — verified 2026-08-19 (fixed deprecated approval-tier field on this card, caught by test_governance_compliance)
- [x] committed with WHY; hub notified via SendMessage

## Execution record

5 parallel lean-workers + 1 orchestrator fix (the `grep -v worktrees` filter had excluded the
legit file removing-worktrees-part2-post-removal.md — 4 occurrences fixed by hand). Totals:
132 invocation teachings rewritten to amp-send/amp-inbox/amp-reply, 2 namespaced pointers,
0 bulk deletions. Batch reports: reports/phase2/*-tnz8rcoe-batch[1-5].md.

## Approval log

- 2026-08-19T14:03:30+0200 — COMPLETED by integrator-session (Tier 0, docs sweep). All acceptance boxes verified first-hand.
