---
name: amia-prrd-trdd-kanban
description: "INTEGRATOR's role in the PRRD / TRDD / Kanban workflow. Use when INT reviews code in ai_review, dispatches the DEPLOYER subagent for service TRDDs (deploy → live), the RELEASER subagent for tool TRDDs (publish → published), or investigates anomalies in live_auditing."
allowed-tools: "Bash(python3:*), Bash(get-prrd.py:*), Bash(findprrd.py:*), Bash(findtrdd.py:*), Bash(kanban.py:*), Bash(git:*), Bash(gh:*), Read, Edit, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

## Overview

This is the INTEGRATOR's (AMIA) role-specific layer of the PRRD /
TRDD / Kanban model. INT owns the **ship and operate** columns:
`ai_review`, `publish`, `deploy`, and `live_auditing` (and watches
`live` for post-deploy soak). INT spawns two specialised subagents
via the Agent tool: **DEPLOYER** (`deploy → live`, services) and
**RELEASER** (`publish → published`, tools). Both subagents have NO
AMP identity; they return results to INT, which relays via AMP up
the chain INT → ORCH → COS → MANAGER → USER. For universal
mechanics see the `prrd-trdd-kanban` skill in `ai-maestro-plugin`.

## Prerequisites

- The universal `prrd-trdd-kanban` skill (ai-maestro-plugin) for
  shared column mechanics and the exempt-operations reference.
- A PRRD and TRDDs under `design/tasks/`; `findtrdd.py`,
  `get-prrd.py`, `kanban.py` on PATH.
- `gh` and `git` authenticated for PR review and CI.
- The `deployer.md` and `releaser.md` subagents in this plugin's
  `agents/` directory (dispatched via the Agent tool).

## Instructions

1. Find pending reviews: `findtrdd.py --column ai_review`. For each,
   fetch the PR (`gh pr view <pr-url>`), review against
   `relevant-rules:` (`get-prrd.py --cite <N>`). Approve →
   `column: complete` (or `human_review` if required); reject →
   `column: dev` with findings in the body.
2. When a TRDD reaches `complete` with `release-via: publish`,
   request MANAGER approval (via COS), then spawn the RELEASER
   subagent (`subagent_type: releaser`) with the publish target and
   channel; instruct it to run the publish pipeline and verify the
   artifact is installable.
3. When a TRDD reaches `complete` with `release-via: deploy`,
   request MANAGER approval, then spawn the DEPLOYER subagent
   (`subagent_type: deployer`) with the deploy target; instruct it
   to run the deploy pipeline and verify the service is live.
4. Parse the subagent's structured result. On publish success set
   `column: published`, `published-version:`, `published-at:`; on
   deploy success set `column: live`, `live-since:`.
5. Relay the outcome via AMP up the chain (INT → ORCH → COS →
   MANAGER → USER).
6. In `live_auditing`: author audit TRDDs (`task-type: audit`),
   investigate logs/sentry/traces. If benign → `column: complete`;
   if issue-confirmed → body grows a `## Fix plan`, `column: dev`.
   For soak windows after `deploy → live`, monitor until clean
   (`column: live`) or surface a new audit TRDD on an alert.

## Output

- Review verdicts on `ai_review` TRDDs (approve / reject + findings).
- DEPLOYER / RELEASER subagent dispatches and parsed results.
- TRDD column moves to `published` / `live` with version and
  `live-since` / `published-at` frontmatter.
- AMP messages relaying every outcome up the chain to MANAGER/USER.

## Error Handling

- A subagent returning a hard failure → set `column: failed` and
  grow a failure post-mortem in the TRDD body; relay the failure
  via AMP.
- NEVER merge a PR or trigger `complete → publish`, `complete →
  deploy`, `publish → published`, `deploy → live`, `ai_review →
  human_review`, or force-`failed` without MANAGER approval — these
  are non-exempt. Launching ai_review on a PR (review request, NOT
  merge), CI runs, and audit-evidence collection are exempt.
- `gh` / `git` auth failure → stop and report; do not retry blindly.

## Examples

Spawn RELEASER for a tool TRDD (after MANAGER approval): call the
Agent tool with `subagent_type: releaser`, description "Publish
TRDD-1a2b3c4d", prompt giving the title, publish target, and
channel; on success set `column: published` and `published-version`.

Spawn DEPLOYER for a service TRDD (after MANAGER approval): call the
Agent tool with `subagent_type: deployer`, description "Deploy
TRDD-9f8e7d6c", prompt giving the deploy target; on success set
`column: live` and `live-since`.

## Resources

For shared column mechanics and the canonical exempt-vs-non-exempt
rules, consult the universal `prrd-trdd-kanban` skill and its
exempt-operations reference in `ai-maestro-plugin`. The DEPLOYER and
RELEASER subagents this skill dispatches are defined in this
plugin's `agents/` directory as `deployer.md` and `releaser.md`.
