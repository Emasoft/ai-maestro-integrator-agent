---
trdd-id: RGXRISNX
title: Refuse --install-branch-rules on a repo already carrying the ratified baseline
column: complete
created: 2026-08-08T11:15:17+0200
updated: 2026-08-08T11:15:17+0200
current-owner: integrator-session
task-type: security
release-via: publish
external-refs: [claude-plugins-validation#203, manager-approval-defaults §F]
implementation-commits: []
npt: []
eht: []
---

# Refuse `--install-branch-rules` on a repo already carrying the ratified baseline

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-08

- **Done.** `install_branch_rules()` now refuses when `baseline-history-protect` or
  `baseline-pr-and-checks` is present, and **fails closed** when the ruleset list
  cannot be read at all.
- **Verified:** 48 pytest · 7/7 test files · ruff + mypy clean · both falsifications bite.
- **NEXT ACTION:** none.

## Why

`cpv-setup-branch-rules` does **not** bring the ratified baseline to spec. Read in its
source at v5.3.0 (filed as claude-plugins-validation#203):

- `scripts/setup_branch_rules.py:110` — `RULESET_NAME = "cpv-branch-rules"`, hardcoded;
  the file contains **zero** occurrences of `baseline-`, so it cannot target the
  ratified pair even in principle.
- `:326 fetch_legacy_protection_rulesets()` classifies as "legacy" any ruleset whose
  rules intersect `{pull_request, required_status_checks, required_signatures,
  code_quality}` — which `baseline-pr-and-checks` always does.
- `:694` then prints `gh api --method DELETE …/rulesets/<id>` for each match.

So on a baselined repo the command **ADDS** a non-ratified ruleset — "adding a new
ruleset that affects the default branch" is **NON-EXEMPT** under
`manager-approval-defaults.md` §F — and **advises DELETING the ratified one**.
`baseline-history-protect` escapes only by accident: its rules
(`deletion`/`non_fast_forward`/`required_linear_history`) do not intersect that set.

**This is not hypothetical.** The command was run against this repo earlier today. It
created `cpv-branch-rules` (id 20583277) and printed a `DELETE` for
`baseline-pr-and-checks`. Caught only by diffing the resulting rulesets against the
ratified text rather than trusting the `✓ Ruleset created` line; the stray was removed
(JSON snapshotted first) and the `baseline-*` pair brought to spec by hand.

**This repo was also a distribution vector.** `install_branch_rules()`'s own docstring
said it shells out "so downstream plugins do not need to vendor
`setup_branch_rules.py` locally" — i.e. it put the hazard in front of anyone who copied
this pipeline. Fixing it upstream is necessary but not sufficient; the local entry point
needed the guard too. (The CORE session independently found the same vector in its copy
and shipped an equivalent guard.)

## The fail-closed detail, which is the whole design

`_ratified_baseline_present()` returns `True` / `False` on a successful read and
**`None` when the list could not be read at all**. A bare `[]` or `False` on failure is
the dangerous shape: it reads as "no baseline here", the caller steps aside, and the
destructive command runs against **precisely the repo nobody could inspect**. The read
goes through `gh_with_retry` for the same reason — a transient github.com hiccup must
not be the thing that decides a repo is unbaselined.

## Falsification

Both guardrails were broken on purpose. Note that the naive falsification — disabling
the guard to watch it not refuse — would have **actually run the destructive command**
and recreated the stray ruleset, so both were designed to avoid reaching it:

| Injected regression | Result |
|---|---|
| exit 1 for the WRONG reason (`slug=None`, returns before the command) | `FAIL: refused but said nothing actionable` |
| failed read returns `False` instead of `None` (the dangerous shape) | `FAIL: unreadable list returned False instead of None` |

`check_repo_really_is_baselined` establishes the PREMISE before the refusal checks run.
Without it, a guard refusing for the wrong reason — unreadable list, typo'd slug,
missing `gh` — is indistinguishable from one working correctly, and passes as a false
green. Ordering is load-bearing here.

## Not mocked, deliberately

The guard's entire value is that it reads the **live** ruleset list; substituting that
read would test a different function than the one that ships. The tests call real
`gh api` against the real repo and **skip honestly** (naming the reason) when `gh` is
missing or unauthenticated — a skip is truthful, a mock would not be.

## Incidental

Fixed two `cprint(f"\\n…")` sites that emitted a literal `\n` instead of a newline
(`install_branch_rules`, `install_git_hooks`). Pre-existing and cosmetic; spotted in the
falsification output.

## Verification

| Gate | Result |
|---|---|
| `pytest tests/` | 48 passed |
| `tests/run-all-tests.py` | 7/7 test files |
| `ruff --select=E,F,W,I --ignore=E501` | clean |
| `mypy --ignore-missing-imports` | clean |
| guard against the live repo | REFUSES, naming `cpv-branch-rules` and #203 |
