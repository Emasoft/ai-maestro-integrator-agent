---
trdd-id: ONCGHA1Q
title: The TDD issue-closure gate enforces the exact opposite of RED-before-GREEN
column: complete
created: 2026-08-16T17:52:57+0200
updated: 2026-08-18T20:08:29+0200
current-owner: integrator
task-type: bugfix
min-approval-requirement: none
scope: project
severity: high
relevant-rules: []
implementation-commits: [b201375]
last-test-result: pass
last-test-at: 2026-08-18T20:08:29+0200
---

# The TDD gate blocks correct sequences and passes incorrect ones

`scripts/amia_pre_issue_close_hook.py::verify_tdd_sequence()` (line 283) has an
inverted comparison. It does not fail open or fail closed — it fails **backwards**,
rejecting exactly the sequences it exists to require and admitting exactly the ones
it exists to reject.

Proven by executing the shipped function, not by reading it:

```
$ uv run python -c "… from amia_pre_issue_close_hook import verify_tdd_sequence …"
CORRECT RED->GREEN     -> is_valid=False  GREEN commit appears BEFORE RED commit in history
WRONG GREEN->RED       -> is_valid=True
```

`gh` returns commits newest-first, so a correct TDD history (RED committed first,
GREEN after) arrives as `['GREEN: …', 'RED: …']` — GREEN at the LOWER index.

## The defect is one operator, and the correct rule is already written above it

Lines 276-279 state the rule correctly, in the code's own words:

```python
# gh pr view shows commits newest-first: index 0 = newest commit
# In TDD, RED must come BEFORE GREEN chronologically.
# newest-first means RED (older) has HIGHER index than GREEN (newer).
# So GREEN index should be LESS than RED index for correct TDD order.
first_red = red_commits[0]
first_green = green_commits[0]

if first_green < first_red:            # ← line 283: treats the CORRECT order as failure
    return False, "GREEN commit appears BEFORE RED commit in history", …
```

The comment says `first_green < first_red` **is** correct order. The next statement
treats it as the failure condition. Whoever wrote the comment understood the
newest-first inversion perfectly and then wrote the comparison as if the list were
oldest-first.

The blocking machinery around it is sound: `main()` calls it at line 588 and returns
exit 2 on `is_valid == False`. So the gate really does block — it just blocks the
wrong population.

## Why this survived

The gate is *loud in the wrong direction*, which is the quietest possible failure
mode for a guard. A developer doing correct TDD gets BLOCKED with a confident,
specific message ("GREEN commit appears BEFORE RED commit in history") that
contradicts what they just did — so the natural reading is "the gate is buggy" or
"my commit names are wrong", and the workaround is to rename commits or bypass the
hook. Meanwhile every genuinely non-TDD PR sails through silently, because a guard
that passes you says nothing at all.

No test covers `verify_tdd_sequence()` — confirmed: the function name appears in no
file under `tests/`. A single two-line table test would have caught this on the day
it was written.

## Approach

1. Invert the comparison at line 283 to match the comment (`if first_red < first_green:`),
   or — clearer, and immune to the next reader making the same mistake — normalise
   the list to oldest-first at the top of the function and compare in chronological
   order, so the code reads the way the domain rule is stated.
2. Fix the error message to name the actual violation.
3. Add the missing test. It is the load-bearing step: the bug is invisible without one.

## Acceptance criteria

1. A table test asserts BOTH directions: `['GREEN: …','RED: …']` (correct TDD) is
   VALID, and `['RED: …','GREEN: …']` (wrong order) is INVALID. Both assertions must
   be present — a test covering only one direction would have passed against the
   current inverted code.
2. Non-vacuity: re-inverting the operator turns the new test RED. Proved by doing it,
   not asserted.
3. The `red_count == 0` / `green_count == 0` early returns keep their current
   behaviour (both remain invalid).
4. The full suite stays green and CPV stays 0/0/0/0.

## Notes and lessons learned

Found by the axis-2b "claimed vs enforced" pass of the fleet self-audit
(TRDD-BRRJK57P Phase 1), then verified first-hand by executing the function — the
report's reasoning was correct, but a claim that a comparison is "backwards" is
itself easy to get backwards, so reading it was not enough.

The general shape worth remembering: **a guard whose mechanism is present and wired
can still be measuring the wrong thing, and "the gate fires" is not evidence the gate
is right.** Everything structural here looked healthy — the function exists, `main()`
calls it, the exit code blocks. The only way to see the defect was to run it on a
known-good input and a known-bad input and check which one it rejected. Two inputs.
That is what an enforcement claim costs to verify, and why "cite the guard" is not
the same as "check the guard".

## Approval log

- 2026-08-18T20:35:00+0200 — COMPLETED, with the original finding PARTIALLY REFUTED
  by ai_review and the refutation verified first-hand. `gh pr view --json commits`
  returns commits CHRONOLOGICAL (oldest-first) — verified live on facebook/react#37143
  and microsoft/vscode#200000, committedDate ascends — so the original gate's BEHAVIOR
  was correct and only its COMMENT was wrong. This card's first fix (b201375) inverted
  a correct gate for one commit; ce4813c reverted to behavior proven identical to the
  original on all 6 table cases (both versions executed, original extracted verbatim
  from git). Net delivered: truthful comments pinning the VERIFIED ordering + the
  previously-missing both-direction test, its inputs now encoding gh's real shape.
  Lesson recorded on the card: the code comment, the audit worker, the card author,
  and the first test all shared ONE unverified premise — synthetic inputs derived
  from a premise "prove" the premise, not the code.
