---
trdd-id: 2MD3YY57
title: Adopt the async-approval model plus RP-MODEL-01 and RP-SKILL-MENU-01
column: completed
created: 2026-08-08T12:34:20+0200
updated: 2026-08-15T00:33:41+0200
current-owner: integrator-session
task-type: docs
release-via: publish
min-approval-requirement: none
mandate: true
mandated-by: self
external-refs: [ai-maestro TRDD-O16UGID8, role-plugins-spec 1.1.0, ai-maestro#136]
implementation-commits: []
npt: []
eht: []
---

# Adopt the async-approval model plus RP-MODEL-01 and RP-SKILL-MENU-01

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-08

- **Done.** All three work-order items implemented, each with a falsified test.
- **NEXT ACTION:** none. Closure record goes back to the hub session.

This card is itself Tier-0 (`mandate: true`, `mandated-by: self`,
`min-approval-requirement: none`) — authored straight to work, per the model it adopts.

## Why

Work order from the ai-maestro hub citing `TRDD-O16UGID8` (spec 1.1.0, tip `eaf609ad`).
Its measurement of this repo reproduced exactly, before changing anything:

| Field | Files (population: all tracked `.md`) |
|---|---|
| `min-approval-requirement` | **0** |
| `mandate:` / `mandated-by:` | **0** |
| `derived-kind:` | **0** |
| deprecated `approval-tier:` | **1** |

The choice trees predated the async model, so an agent following them would WAIT where the
model says author-as-planned-and-proceed.

**The `approval-tier: 1` was mine, authored earlier the same day** — I wrote a card in the
deprecated vocabulary hours before being told the vocabulary had moved. Worth recording: the
gap was not old debt accumulating quietly, it was still actively growing.

## The part that needed judgement, not a sweep

The hub flagged it precisely: **the INTEGRATOR owns release transitions, which ARE Tier-2.**
A blanket "un-gate everything" would have been as wrong as the stall it fixes.

Grepping "wait for approval" shapes across all tracked `.md` returned **5**. Read individually:

| Hit | Verdict |
|---|---|
| `bot-categories.md:103` — `\| human \| Wait for approval \|` | **false positive** — a table classifying review *bots* |
| `github-pr-merge/README.md:10` — "PRs waiting on CI or approvals" | **false positive** — describes GitHub's auto-merge feature |
| `merge-state-verification.md:364` — `{"code": "REVIEW_REQUIRED"...}` | **false positive** — a literal API payload in a comment |
| `instruction-templates.md:139` — `AWAIT APPROVAL BEFORE MERGING TO MAIN` | **correctly gated** — merge to main is Tier-2; kept |
| `blocking-workflow.md:27` — blocked pending MANAGER approval | the real one — needed D1 never-block |

So **1 of 5** needed changing and **1 of 5** had to be deliberately preserved. A regex-driven
rewrite would have removed the release gate — the failure mode being guarded against, arrived
at from the opposite direction.

## What changed

- **`skills/amia-prrd-trdd-kanban/references/async-approval-model.md`** (new) — Tier-0
  default, the field vocabulary, the D3 escalation table, D1 never-block, the completion gate,
  and the explicit list of what stays gated.
- **`SKILL.md` steps 2-3 REWRITTEN, not appended to.** They said "request MANAGER approval,
  then spawn". They now say request it, log it in `## Approval log`, **move on**, and spawn
  when approval lands. The gate is unchanged; the idling is gone. Appending a correct rule
  beside a stale tree leaves the agent following the tree.
- **`SKILL.md` Error Handling** gained the missing half: it was entirely "NEVER without MANAGER
  approval" with no Tier-0 counterpart, which teaches over-gating by omission.
- **RP-MODEL-01** — dropped `model: opus` from the main agent.
- **RP-SKILL-MENU-01** — added the full 20-skill menu. `auto_skills:` preloaded 9 of 20 and
  nothing listed the other 11, so a reader had no way to learn they exist.
- Detail lives in `references/` because `SKILL.md` was already 4756 chars against this
  plugin's own under-4000 convention; growing it would have traded one violation for another.

## Falsification

| Injected regression | Result |
|---|---|
| `model: opus` restored | `FAIL: main agent still pins 'model: opus'` |
| a menu row deleted | `FAIL: menu drift — missing ['amia-quality-gates']` |
| **a new skill dir added, menu untouched** | `FAIL: menu drift — missing ['amia-phantom-not-in-menu']` |
| `approval-tier: 0` reintroduced | `FAIL: deprecated approval-tier still used` |

The third row is the one that matters: RP-SKILL-MENU-01 requires the menu be updated *in the
same change that touches any skill*, and that is a promise about future behaviour. Only a
check that fails when a skill appears without a menu row can keep it.

## Verification

| Gate | Result |
|---|---|
| `tests/test_governance_compliance.py` | 15/15 |
| `pytest tests/` | see release commit |
| ruff + mypy | clean |
| overlay fields after | `min-approval-requirement` + `mandate:` present; `approval-tier:` **0** |

## Approval log

- 2026-08-15T00:33:41+0200 — COMPLETED by integrator. Archived: work finished and shipped.
