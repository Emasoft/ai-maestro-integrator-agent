---
trdd-id: TNZ8RCOE
title: Sweep bare agent-messaging invocations to frozen amp-* CLIs
column: dev
created: 2026-08-19T10:28:33+0200
updated: 2026-08-19T10:28:33+0200
current-owner: integrator-session
task-type: docs
approval-tier: 0
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

- [ ] repo-wide grep: zero bare-invocation teachings remain (`agent-messaging` only as namespaced pointer or deliberate historical prose)
- [ ] full test suite passes (15/15 files)
- [ ] committed with WHY; hub notified via SendMessage

## Approval log
