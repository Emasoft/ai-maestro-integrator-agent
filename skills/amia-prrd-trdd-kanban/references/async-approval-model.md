# The async-approval model for the INTEGRATOR

Implements `TRDD-O16UGID8` (ai-maestro, `governance-rules`). The rule source is
`rules/aimaestro/aimaestro-trdd-approval.md`; this file is the INTEGRATOR's
projection of it, and it exists because the INTEGRATOR sits on both sides of the
line — most of its work is Tier-0, and its release transitions are Tier-2.

## The one thing to get right

**Approval is asynchronous. Needing approval is NOT a reason to stop working.**

Two failures, opposite directions, equally bad:

| Failure | What it looks like |
|---|---|
| Waiting where you should proceed | An in-scope task sits unstarted pending an approval nobody was ever asked for |
| Proceeding where you should gate | A release ships without the Tier-2 approval it required |

The INTEGRATOR is unusually exposed to both, because it owns `ai_review`,
`publish`, `deploy` and `live_auditing` — a mix of Tier-0 and Tier-2 work — and a
blanket habit in either direction is wrong for half of it.

## Tier 0 is the DEFAULT (self-mandate)

In-scope work and derived NPT/EHT cards are authored **directly** as
`column: planned` and worked immediately. No approval round-trip, no waiting:

```yaml
min-approval-requirement: none    # NEVER the deprecated `approval-tier: N`
mandate: true
mandated-by: self
```

A derived card adds, with **empty** `npt:`/`eht:` (the flock is depth-1):

```yaml
derived: true
derived-kind: npt          # or: eht
parent-trdd: <parent id8>
```

## Escalate only on an objective D3 trigger

Escalation is triggered by what the work TOUCHES, not by how it feels:

| Trigger | `min-approval-requirement:` |
|---|---|
| Cross-team / cross-repo · release surface · baseline-ruleset deviation · `.github/` · governance or persona edit | `manager` |
| Team-internal coordination affecting other members | `chief-of-staff` |
| GOLDEN PRRD change · shared credentials or owner identity · irreversible / highest-stakes | `user` |
| Everything else — in-scope work, NPT/EHT, docs, local refactor | `none` |

When unsure, escalate one level. But note the asymmetry: over-escalating a
Tier-0 card costs a stall on every future card of that shape, because the choice
tree is what the next agent reads. It is not free either.

## D1 — never block

Filing a Tier-1/2/3 proposal means writing it to `design/proposals/` and
**moving on to other work**. Do not spin-wait on an approver. The proposal is a
durable artifact; the approver drains the queue on their own cadence, and the
card resumes when the decision lands.

Concretely, for the INTEGRATOR's own gated transitions: request the approval,
record the request in the TRDD's `## Approval log`, then **pick up the next
card**. A release waiting on MANAGER is not a reason for the board to be idle.

## What stays gated, without exception

These are Tier-2 because they touch the release surface, and the async model does
**not** loosen them — it only stops you idling while they are pending:

- `complete → publish` / `complete → deploy`
- `publish → published` / `deploy → live`
- `ai_review → human_review`
- merging a PR to the default branch
- force-`failed`

Exempt and to be done without asking: launching an ai_review on a PR (the review
request, never the merge), CI runs, audit-evidence collection in
`live_auditing`, and mechanical column moves.

## Completion gate

A card reaches `complete` only when **both** hold:

1. its checklist exists (≥1 box) and every box is checked, and
2. every `npt:` / `eht:` child is terminal.

Otherwise it is `blocked`, with `blocked-by:` naming what blocks it. A card that
sits still without a non-empty `blocked-by:` is stalled, not parked — and a
`dev` column that nobody is working is worse than an unstarted card, because it
hides the stall from the only view anyone checks.
