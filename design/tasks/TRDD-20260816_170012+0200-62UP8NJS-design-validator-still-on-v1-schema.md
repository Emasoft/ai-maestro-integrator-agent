---
trdd-id: 62UP8NJS
title: amia_design_validate.py rejects every TRDD in the repo because it still requires the v1 schema
column: todo
created: 2026-08-16T17:00:12+0200
updated: 2026-08-16T17:00:12+0200
current-owner: integrator
task-type: bugfix
min-approval-requirement: none
scope: project
relevant-rules: []
---

# The design validator validates nothing

`scripts/amia_design_validate.py` reports `"valid": false` for **13 of 13** TRDDs
in `design/`, including cards nobody has touched in weeks. Every failure is the
same pair:

```
Missing required field: type
Missing required field: status
```

Those are **v1 field names**. The TRDD v2 rules renamed them: `type` → `task-type`,
and `status` → `column` (v2 moved pipeline state into `column:`, and the residue of
`status:` is a *value*, never a field name). Measured: `grep -c '^status:'` across
`design/` returns 0; `grep -c '^task-type:'` returns 12 of 13.

So the validator is not finding a defect in the cards — the cards are correct and
the validator is stale. Found while closing TRDD-T3CLWN5Y; explicitly confirmed
pre-existing by running it against an archived card that card never touched.

## Why this matters more than a stale field list

A validator that fails 100% of its inputs is worse than one that does not exist.
It cannot distinguish a malformed card from a well-formed one, so its output
carries no information — and the only rational response to a check that always
reds is to stop reading it. At that point a real schema break lands silently,
because the alarm it would have tripped has already been tuned out.

## Approach

1. Update the required-field set to v2: `trdd-id`, `title`, `column`, `created`,
   `updated`, `current-owner`, `task-type`.
2. Validate `column:` against the ratified 17-column vocabulary rather than a
   free string, so a typo'd column is caught.
3. Do **not** add a back-compat branch that accepts `type`/`status` as aliases —
   no card in the repo uses them, and a dual-schema validator re-opens exactly
   the ambiguity v2 closed.
4. **Wire it into `tests/run-all-tests.py`.** This half is not optional and not
   cosmetic: fixing the schema without wiring leaves the validator exactly as
   unrun as it is today, and the next drift is invisible again. The two halves
   fail together — a correct checker nobody runs and a broken checker nobody
   trusts are the same checker.

## Acceptance criteria

1. All 13 existing TRDDs validate clean under `--strict`.
2. Non-vacuity: a card with a bogus `column: banana` FAILS, and passes once
   corrected — proved by injection, not by assumption.
3. A card missing `task-type:` still fails (the check is not merely disabled).
4. `tests/run-all-tests.py` invokes the validator, and its file count rises by
   one. Proved by injection: a deliberately malformed card turns the SUITE red,
   not merely the standalone script.
5. The full suite stays green once the injected card is reverted.

## Notes and lessons learned

Nothing in the repo surfaced this: the validator is not wired into
`tests/run-all-tests.py`, so 12/12 test files passed while a checked-in tool
rejected every document it exists to check. A check nobody runs and a check that
always fails are the same check.
