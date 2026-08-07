---
trdd-id: 8CKKY36P
title: Align the agent cost reporter to the current Claude model generation
column: complete
created: 2026-08-07T19:49:12+0200
updated: 2026-08-07T19:49:12+0200
current-owner: integrator-session
task-type: bugfix
release-via: publish
implementation-commits: [b626f20]
npt: []
eht: []
---

# Align the agent cost reporter to the current Claude model generation

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-07

- **Done.** `scripts/cpv_token_cost.py` now prices the 5-series correctly and
  `tests/test_token_cost.py` (10 checks) locks both regressions down.
- **Verified:** 32/32 pytest, 4/4 test files via `tests/run-all-tests.py`, ruff and
  mypy clean under MegaLinter's exact arguments
  (`--select=E,F,W,I --ignore=E501`, `--ignore-missing-imports`).
- **NEXT ACTION:** none. This TRDD is closed; the commit rides the next publish.

## Why

Claude Code 2.1.219 made Opus 5 the default model. The cost reporter's pricing
table stopped at the 4.x generation, so every agent run was costed against a
model that is not the one that ran.

Two independent defects, both silent — a wrong rate produces a plausible dollar
figure, never an error:

1. **`claude-opus-5` had no table entry.** It fell through the exact-key lookup
   and the substring loop into the fuzzy family branch, which returned
   `claude-opus-4-1` — the retired **$15/$75** rate. Actual Opus 5 is **$5/$25**,
   so every Opus cost line read **3x** the real spend.
2. **The fuzzy fallback aimed at a retired model on purpose.** Every legacy 4.x
   id already has its own explicit key and is caught by the substring loop, so
   pointing the fallback at 4.1 bought nothing and mispriced everything newer.
   It now aims at the current generation of each family, which is the only guess
   that can be right for an id the table has never seen.

Rates were taken from the bundled `claude-api` skill's model table (cached
2026-06-24), not from recall. Cache rates are derived, not quoted:
`cache_write = 1.25x input` (5-minute TTL), `cache_read = 0.10x input`.

## What changed

- `scripts/cpv_token_cost.py`
  - Added `claude-fable-5`, `claude-opus-5`, `claude-opus-4-8`,
    `claude-opus-4-7`, `claude-sonnet-5`.
  - Reordered the table most-specific-first per family and documented that the
    order is load-bearing (see the gotcha below).
  - Repointed the fuzzy fallback at the current generation per family and
    recorded the 3x-overcharge that the old target caused.
- `tests/test_token_cost.py` — new, 10 checks, dual-mode (pytest + standalone
  table) matching `test_hooks.py`'s house style. Real inputs, no mocks: the
  transcript check writes an actual JSONL and parses it through the real
  `parse_transcript`, covering dedup-by-message-id and the 4-category sum.

**Sonnet 5 is billed at the standard $3.00/$15.00, not its $2.00/$10.00
introductory rate** (which expires 2026-08-31). A cost estimate that errs high is
the safe direction, and the standard rate needs no dated maintenance to stay
correct once the intro window closes.

## Load-bearing gotcha — key order in `MODEL_PRICING`

`get_pricing` substring-matches keys **in insertion order**, and a shorter key is
a substring of a longer one: `"claude-opus-4"` lives inside
`"claude-opus-4-8"`. A less specific key placed above a more specific one
silently captures it and returns the wrong rate. Every family is therefore
listed most-specific-first, with the bare `claude-opus-4` / `claude-sonnet-4`
keys last within their family.

## The test that was decoration, and how it was caught

The first version of `check_specific_key_beats_shorter_prefix` asserted on bare
ids (`claude-opus-4-8`). It passed **even with the table deliberately
mis-ordered**, because a bare id is itself a table key and the exact-match lookup
returns before the substring loop ever runs.

It was caught by falsifying it — re-running the check against a deliberately
mis-ordered table and observing it still passed. The check now uses the **dated**
form the API actually returns (`claude-opus-4-8-20260301`), which misses the
exact lookup, falls into the loop where `claude-opus-4` also matches, and so
genuinely depends on order. Falsified again after the fix: mis-ordered table →
`FAIL: claude-opus-4-8-20260301 priced at $15.0/MTok input, expected $5.0`.

Both guardrails are proven to bite:

| Injected regression | Check that fires |
|---|---|
| fuzzy fallback repointed at `claude-opus-4-1` | `check_unknown_opus_uses_current_generation` |
| bare `claude-opus-4` moved above `claude-opus-4-8` | `check_specific_key_beats_shorter_prefix` |

**A test that cannot fail is decoration.** Any future check added to this file
should be falsified the same way before it is trusted.

## Verification

| Gate | Result |
|---|---|
| `uv run --with pytest pytest tests/ -q` | 32 passed |
| `uv run python tests/run-all-tests.py` | 4/4 test files passed |
| `ruff check --select=E,F,W,I --ignore=E501` | All checks passed |
| `mypy --ignore-missing-imports` | Success, no issues |
| Resolver spot-check, 16 real model ids | all correct |
