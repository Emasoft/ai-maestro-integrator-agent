---
trdd-id: 8ddc5f37-bbdd-42c9-a09b-82266e47198e
title: MAESTRO persona section + governance SCEN suite + v1.3.1 release (R26–R40 9/9)
column: published
created: 2026-06-20T04:36:50+0200
updated: 2026-06-20T05:16:27+0200
current-owner: integrator
assignee: integrator
priority: 2
severity: MEDIUM
effort: M
labels: [governance, persona, scen, release]
task-type: docs
parent-trdd: null
npt: []
eht: []
blocked-by: []
supersedes: []
relevant-rules: [1, 2]
release-via: publish
delivery: direct-push
target-branch: main
merge-strategy: squash
must-pass-tests-before-merge: true
publish-target: ai-maestro-plugins
publish-channel: stable
test-requirements: [unit, lint]
audit-requirements: []
review-requirements: [human-review]
runtime-targets: [macos, linux]
impacts: []
attempts: 0
test-failures: 0
last-test-result: pass
last-test-at: 2026-06-20T05:16:27+0200
implementation-commits: [d3a2852, 22374ca, 48a539c, 51560cc, 5a5afdc]
published-version: 1.3.1
external-refs: ["github.com/Emasoft/ai-maestro/issues/37", "github.com/Emasoft/ai-maestro-integrator-agent/issues/15"]
---

# TRDD-8ddc5f37 — MAESTRO persona section + governance SCEN suite + v1.3.1 release

**Filename:** `design/tasks/TRDD-20260620_043650+0200-8ddc5f37-maestro-persona-scen.md`
**Tracked in:** this repo (`design/tasks/` is git-tracked)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-20

**Why this exists:** The fleet R26–R40 governance propagation (Emasoft/ai-maestro#37)
is at **8/9** role-plugins complete. The MANAGER's deep-verify (#37, 2026-06-19
09:46Z) confirms **only the integrator remains**: v1.3.0 already landed R29/R30 +
the R23 frozen-CLI decouple + the R24 global-memory directive, but the integrator
persona still lacks the **MAESTRO governance section** and there is **no
`tests/scenarios/governance-scenarios.md` SCEN suite** (v1.3.0 shipped a pytest
oracle, `tests/test_governance_compliance.py`, instead).

**USER authorization (apex / MAESTRO-level):** the project owner explicitly chose
**"Build + publish v1.3.1"** on 2026-06-20 — direct authorization above the MANAGER
Tier-2 gate. Recorded in `## Approval log`. Release uses
`amia_create_release.py --solo-user-approval` (the USER-as-MANAGER path), NOT a
bypass of PRRD S2.1.

**NEXT ACTION:** DONE — v1.3.1 published (commit 5a5afdc, tag v1.3.1). Persona
section + SCEN suite + 2 oracle guards landed; CPV `--strict` 0/0/0/0 (pinned +
unpinned) on the published commit; oracle 10/10. REMAINING (separate, pre-existing —
NOT from this work): CI is chronically red from a `uv sync --extra dev` workflow bug
(pyproject has no `[project.optional-dependencies].dev`) breaking Test/Release since
v1.3.0; a transient CPV default-branch drift flagged Plugin Validation I001 (clean on
local re-validate; re-run pending). Report on #37 + #15 next.

**Load-bearing facts / gotchas:**
- The INTEGRATOR is a **subordinate team-layer role** (one of the 5 base members,
  titled `INTEGRATOR`), NOT the MANAGER. R29/R30/R31 are **facts it must know**
  (powers the MANAGER holds), not powers the INTEGRATOR holds. Mirror the
  **orchestrator v1.9.0** adaptation, not AMAMA's MANAGER-centric one.
- Keep the Tier-3 `USER` enum in the approval-tiers vocabulary intact; ADD the
  MAESTRO apex (R36/R37) and state the ladder terminates at the MAESTRO. The
  `check_references_escalate_to_maestro_not_user` oracle only scans `skills/**`,
  not the persona — do not regress it.
- Release gate: `amia_create_release.py` exits **7** without recorded approval;
  use `--solo-user-approval "<USER's words>"`.

**Durable artifacts to read before acting:**
- Reference SCEN: `…/EMASOFT-ASSISTANT-MANAGER/ai-maestro-assistant-manager-agent/tests/scenarios/governance-scenarios.md` (read-only; cross-project).
- Reference persona section: same repo `agents/…-main-agent.md` → `### Foundational Governance Rules (R26–R40)`.
- The MANAGER turn-key draft: integrator#15 body.
- The 8/9 snapshot: ai-maestro#37 comments (2026-06-19 09:42–09:46Z).

## Context

`ai-maestro#37` tracks fleet-wide propagation of the USER-ratified governance rules
**R26–R40** (`GOVERNANCE-RULES.md` v4.0.1) into every role-plugin persona. The
MANAGER (AMAMA v2.12.0) is the reference implementation. Subordinate team-layer
roles adapt it: the **orchestrator (AMOA) v1.9.0** is the closest precedent for the
INTEGRATOR — both are non-MANAGER base members, so lifecycle rules are facts-to-know
rather than powers-held.

This TRDD closes the integrator's two remaining gaps to reach fleet **9/9**.

## Plan

1. **Persona section** — add `## Foundational Governance Rules (R26–R40)` to
   `agents/ai-maestro-integrator-agent-main-agent.md`: a "binds-you-directly vs
   facts-about-the-MANAGER/COS" split, the MAESTRO apex node (R36/R37), and the
   escalation-ladder-terminates-at-the-MAESTRO clarification.
2. **SCEN suite** — author `tests/scenarios/governance-scenarios.md` (Given/When/Then,
   INTEGRATOR actor-inverted mirror of AMAMA G01–G11) plus the INTEGRATOR-specific
   **release-approval-gate** scenario; coverage map; trace to the persona section.
3. **Guard tests** — add `check_persona_has_governance_section` +
   `check_governance_scenarios_present` to `tests/test_governance_compliance.py`
   (now 10 checks); run `tests/run-all-tests.py` green.
4. **CPV `--strict`** → 0/0/0/0 (no doc devitalization).
5. **Release** — bump `plugin.json` 1.3.0→1.3.1; canonical pipeline; release-governance
   via `--solo-user-approval`; watch CI green.
6. **Report** — ai-maestro#37 (INTEGRATOR → 9/9) + integrator#15 (reopen/comment).

## Acceptance criteria

- Persona carries an R26–R40 section naming the MAESTRO apex (R36/R37), with the
  subordinate facts/powers split.
- `tests/scenarios/governance-scenarios.md` exists, mirrors the fleet SCEN shape,
  and covers R28/R32/R36/R37 + the INTEGRATOR release-gate.
- `tests/run-all-tests.py` green (oracle now guards both new deliverables).
- CPV `--strict` 0/0/0/0.
- v1.3.1 published; CI green; #37 + #15 updated.

## Approval log

- 2026-06-20T04:36:50+0200 — **APPROVED by USER** (Tier-3 apex / MAESTRO-level), verbatim
  selection **"Build + publish v1.3.1"** in response to the 8/9-compliance decision
  prompt. Authorizes the persona+SCEN edits AND the outward-facing v1.3.1 release.
  Release-governance satisfied via direct USER authorization, recorded here (publish.py
  uses `gh release create` directly, not the `amia_create_release.py --solo-user-approval`
  path — the USER authorization above is the substantive governance record).
- 2026-06-20T05:16:27+0200 — **PUBLISHED v1.3.1** via the canonical pipeline
  (`publish.py --patch`; commit 5a5afdc, tag v1.3.1; push used the ratified admin-bypass
  for publish.py). Release: https://github.com/Emasoft/ai-maestro-integrator-agent/releases/tag/v1.3.1
