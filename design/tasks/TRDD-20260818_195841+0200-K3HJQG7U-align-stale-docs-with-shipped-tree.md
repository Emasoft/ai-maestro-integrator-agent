---
trdd-id: K3HJQG7U
title: Align stale documentation claims with the shipped tree (audit axis-1 findings)
column: ai_review
created: 2026-08-18T19:58:41+0200
updated: 2026-08-18T20:45:00+0200
implementation-commits: [8bb018a]
current-owner: integrator
task-type: docs
min-approval-requirement: none
scope: project
severity: medium
relevant-rules: []
---

# Align stale docs with the shipped tree

One atomic task: reconcile every documentation claim the Phase-1 audit (TRDD-BRRJK57P,
axis 1, all four findings CONFIRMED by two passes and coordinator-verified) proved false
against the shipped tree. The defect class is one thing — prose promising a capability
the tree does not ship — so the fix is one sweep with one acceptance shape.

## The four confirmed findings

1. **`/create-issue-tasks` documented, ships nothing.**
   `skills/amia-kanban-orchestration/references/detailed-guide.md:45-49` documents the
   command with usage syntax; `commands/` contains 0 files; `.agent.toml` declares
   `[commands] recommended = []`. Decide: remove the doc section (the lazy correct fix),
   or ship the command (scope change — needs its own card if wanted).
2. **README "Non-Standard Directories" lists `rules/`, which does not exist** — and
   `.github/workflows/validate.yml:13` still triggers on `rules/**`. Fix both.
3. **`agents/ai-maestro-integrator-agent-main-agent.md:299` promises `amia-session-memory`**,
   deleted 2026-06-16; its replacement pair deleted 2026-06-19 (commit 61124e6). Two
   retirements each updated frontmatter and left this body prose. Remove the parenthetical.
4. **README:147 "All 60+ scripts support `--output-file`" is false** — 70 skill scripts,
   54 implement it (measured twice, unbounded instruments). Either implement the flag in
   the 16 (scope change — own card) or scope the claim honestly.

## Approach

Default to the smallest true documentation, not new capability: delete/correct prose in
1-3, re-scope the claim in 4. Any decision to instead BUILD the missing capability is a
separate feature card, not this one.

## Acceptance criteria

1. `grep -rn 'create-issue-tasks' skills/ commands/ docs/ README.md` returns no hits that
   present the command as available (historical mentions marked as removed are fine).
2. No reference to a `rules/` directory in README or workflow triggers; `validate.yml`
   paths list only directories that exist.
3. `grep -n 'amia-session-memory' agents/` returns nothing.
4. README's `--output-file` sentence is true against a fresh count.
5. Suite 12/12 + handle guard green; CPV --strict 0/0/0/0.
