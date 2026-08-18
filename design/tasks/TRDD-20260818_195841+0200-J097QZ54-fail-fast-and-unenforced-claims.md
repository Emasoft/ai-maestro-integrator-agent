---
trdd-id: J097QZ54
title: Fix the swallowing except handlers and the three unenforced enforcement claims
column: ai_review
created: 2026-08-18T19:58:41+0200
updated: 2026-08-18T20:45:00+0200
implementation-commits: [83b21e0]
current-owner: integrator
task-type: bugfix
min-approval-requirement: none
scope: project
severity: medium
relevant-rules: []
---

# Fail-fast violations + claims that promise guards that do not exist

Two halves of one defect: code that silences failure, and prose that promises enforcement
nothing performs. Both make the system report healthier than it is.

## Half A — swallowing excepts (audit axis-4a, confirmed + coordinator-extended)

**13 × `except Exception: pass` across 6 files** (`check_version_consistency.py` ×4,
`claude-plugin-install.py` ×2, `cpv_validation_common.py` ×3, `update_marketplace_metadata.py`,
`validate_marketplace_pipeline.py`, `validate_xref.py` ×2 approx — re-derive the exact list
with the AST sweep at fix time), **plus 3 × `except (json.JSONDecodeError, Exception): pass`**
at `validate_xref.py:319,346,530` — the disguised form: reads targeted, `Exception` subsumes
the tuple.

House style is FAIL-FAST. Per-site judgment, not a blanket sweep:
- a site whose file TRDD-LBAN7T2K deletes needs no fix — sequence AFTER that card and
  re-derive the list against the post-deletion tree;
- a genuine best-effort probe (e.g. optional metadata enrichment) may narrow to the real
  exception type with a comment saying WHY swallowing is correct there;
- everything else propagates or exits non-zero.

The 29 narrow targeted catches (`ValueError`, `OSError`, ...) are fail-fast-compatible and
OUT of scope.

## Half B — unenforced enforcement claims (audit axis-2b, 3 remaining after ONCGHA1Q)

1. hooks.json issue-closure "requires evidence" — the guard only RECOMMENDS evidence.
   Either enforce or reword to "recommends".
2. `required_linear_history` prohibition is prose-only. NOTE: the USER's 2026-08-13
   Tier-3 ruling ABOLISHED that requirement fleet-wide and branch protection is the
   JANITOR's applier's job — so the correct fix here is likely deleting/softening the
   prose, NOT adding a guard. Verify against the DEP overlay
   (rules/aimaestro/aimaestro-manager-approval-defaults.md:123-126), never the stale IND
   rule at ~/.claude/rules/manager-approval-defaults.md:114-115.
3. Coverage-threshold claim is persona-only with no mechanical gate. Enforce or reword.

Direction per claim: make the TEXT true. Adding a guard is the bigger diff and only
right when the property genuinely must hold mechanically.

## Acceptance criteria

1. AST sweep (`except` handlers whose body is exactly `pass`, including Exception-in-tuple)
   finds 0 broad swallows outside sites carrying an explicit why-this-is-correct comment.
2. Non-vacuity: the sweep is committed as a test and fails when a bare
   `except Exception: pass` is injected.
3. Each axis-2b claim either has a real guard (proved by breaking it) or text that no
   longer promises one.
4. Suite green, CPV --strict 0/0/0/0.

## Notes

blocked-by ordering: work AFTER TRDD-LBAN7T2K lands, since deletion changes Half A's
site list.
