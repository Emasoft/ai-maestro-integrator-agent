---
trdd-id: 9MBKYW9E
title: Verify CI actually went green on the released commit instead of inferring it from a clean push
column: completed
created: 2026-08-08T11:31:13+0200
updated: 2026-08-15T00:33:41+0200
current-owner: integrator-session
task-type: infra
release-via: publish
external-refs: [claude-plugins-validation v5.1.1 ci-verify, manager-approval-defaults §F]
implementation-commits: [5c44695]
npt: []
eht: []
---

# Verify CI actually went green on the released commit instead of inferring it from a clean push

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-08

- **Done.** `publish.py` polls the check-runs API on the released commit and returns
  non-zero unless CI is genuinely green.
- **Verified:** 53 pytest · ruff + mypy clean · falsified three ways (below).
- **NEXT ACTION:** none.

## Why

`baseline-pr-and-checks` grants an admin bypass so `publish.py` can push straight to the
default branch. That is deliberate — the pipeline could not release otherwise — but it
means **the required status checks never gate the release push**. So the pipeline printed
"Published successfully" on the strength of `git push` and `gh release create` returning
0, having verified *nothing* about whether the released commit builds. A red CI on a
published tag would sit unnoticed until somebody happened to look.

Measured before the fix: `grep -c "gh run\|check-runs\|conclusion" scripts/publish.py`
returned **0**. The gap is real, not theoretical — and it is the one canonical-pipeline
offer that genuinely applies here (the canon triage found `cpv-standardize
--force-templates --dry-run` now *skips* `publish.py` as at/ahead of canon, and neither
Dependabot nor SPELL_CSPELL applies).

**This can only ever be detection, never prevention.** The commit must be on the remote
for CI to start, so the stage necessarily runs after the release. It deliberately does
**not** attempt to unpublish: the release is already public, and silently retracting it
would be worse than reporting it. It returns non-zero so the failure lands in the exit
status rather than only in scrollback.

## The fail-closed detail, and the falsification that corrected me

The first implementation returned `0` ("check manually") when the API could not be read —
reporting success on no evidence. That is the exact inversion the branch-rules guard
(`TRDD-RGXRISNX`) was written to avoid **two commits earlier**, and I reproduced it anyway
in new code the same day. Caught by testing, not by review.

The falsification then produced a result worth recording, because the naive reading of it
was wrong. Injecting the dangerous shape — `_ci_check_runs` returning `[]` on failure —
left the test **passing**, which looks exactly like a decorative test. It is not: there
are **two independent mechanisms**, and the injection only disabled one.

| Mechanism | What it stops |
|---|---|
| `runs is None` → keep polling, exit 1 at the deadline | a transient/unauthorized API read |
| green branch requires `gating` non-empty | an empty list read as "nothing failed" |

So `[]` still fails closed, via the second mechanism. The injection that actually reaches
a false green is a read that **wrongly reports success**, and that one does make the test
fail:

| Injected regression | Result |
|---|---|
| `_ci_check_runs` returns `[]` on failure | **passes** — second mechanism still holds (defence in depth) |
| read wrongly reports a green check for a commit with no CI | `FAIL: unreadable list reported success` |
| read reports a genuinely failing check | `rc=1`, `CI FAILED on the released commit: Lint=failure` |
| `_ci_check_runs` returns `[]` instead of `None` | `FAIL: unreadable list returned [] instead of None` |

`check_unreadable_read_returns_none` was added for the fourth row: it pins the
`None`-vs-`[]` contract at the function level, so a refactor cannot quietly delete one of
the two mechanisms and leave the stage resting on the other alone.

## Design details that are load-bearing

- **`CI_VERIFY_IGNORE = {"notify", "release"}`** — push-only jobs that never run on a PR.
  Awaiting them would hang until the deadline on every release.
- **`skipped`/`neutral` are not failures** — a conditional job that correctly did not run
  must not be read as a red build.
- **Timing out is not proof of success.** The timeout branch names what it was still
  waiting for and says "NOT verified green" rather than implying the opposite.

## Not mocked, deliberately

The tests poll the real check-runs API for real commits in this repo: `GREEN_SHA` is the
v1.3.9 release commit (pushed, completed, green) and `UNKNOWN_SHA` is 40 zeroes.
Substituting that read would test a different function than the one that ships — the
stage exists precisely because *a green publish is not evidence of a green build*. They
skip honestly, naming the reason, when `gh` is missing or unauthenticated.

## Verification

| Gate | Result |
|---|---|
| `pytest tests/` | 53 passed |
| `ruff --select=E,F,W,I --ignore=E501` | clean |
| `mypy --ignore-missing-imports` | clean |
| green commit `8c16c288` | rc=0, 8 checks, 0.5s |
| unknown sha | rc=1 after the deadline |
| `--dry-run` | rc=0, no network |

## Approval log

- 2026-08-15T00:33:41+0200 — COMPLETED by integrator. Archived: work finished and shipped.
